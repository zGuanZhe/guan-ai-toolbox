# -*- coding: utf-8 -*-
"""
pay.153.ink 提链 - 浏览器驱动（无 API 调用）

流程：打开 pay.153.ink → 填入 Access Token / 代理池 / 订阅 / 支付路径 / 国家币种
      → 点击「开始提炼」→ 轮询读回 #resultValue（最终链接/付款码）→ 输出 [RESULT] <url>。

配置来源：register/config.json 的 gpt.payment（由后端写入）。
token 来源：stdin（一行 JSON {"token": "..."} 或纯文本 token），避免出现在进程参数中。

输出协议（供后端 gptBot 解析）：
  [RESULT] <最终链接/付款码>
  [META] type=... email=... region=... promo=...
  [ERROR] <失败原因>
"""
from __future__ import annotations

import os
import io
import sys
import json
import time
import shutil
import tempfile

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from DrissionPage import Chromium, ChromiumOptions


def read_token_from_stdin() -> str:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            # 兼容旧格式：JSON 里明确有 token 字段才提取，否则返回完整内容
            if isinstance(data, dict) and data.get("token"):
                return str(data["token"])
        except Exception:
            pass
        # 返回完整内容（完整 session JSON 或纯 token）
        return line
    return ""


def load_payment_config() -> dict:
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            c = json.load(f)
    except Exception:
        c = {}
    return ((c.get("gpt") or {}).get("payment") or {}) or {}


def _js_set_value(page, selector: str, value: str) -> bool:
    return bool(page.run_js(
        """
        const el = document.querySelector(arguments[0]);
        if (!el) return false;
        const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(el, arguments[1]);
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
        """,
        selector,
        value,
    ))


def _js_check_radio(page, selector: str) -> bool:
    return bool(page.run_js(
        """
        const el = document.querySelector(arguments[0]);
        if (!el) return false;
        // 点击 label 触发原生 click，让 React 受控组件感知（label class 变 active）
        const label = el.closest('label');
        if (label) {
            label.click();
        } else {
            el.click();
        }
        return true;
        """,
        selector,
    ))


def _js_select(page, selector: str, value: str) -> bool:
    return bool(page.run_js(
        """
        const s = document.querySelector(arguments[0]);
        if (!s) return false;
        for (const o of s.options) {
            if ((o.value || '') === arguments[1] || (o.text || '').trim().toUpperCase().startsWith(arguments[1].toUpperCase())) {
                s.value = o.value;
                break;
            }
        }
        s.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
        """,
        selector,
        value,
    ))


def _js_set_checkbox(page, selector: str, checked: bool) -> bool:
    return bool(page.run_js(
        """
        const el = document.querySelector(arguments[0]);
        if (!el) return false;
        el.checked = arguments[1];
        el.dispatchEvent(new Event('change', {bubbles:true}));
        el.dispatchEvent(new Event('input', {bubbles:true}));
        return true;
        """,
        selector,
        checked,
    ))


def _poll_result(page, timeout: int) -> str:
    deadline = time.time() + timeout
    last_log = ""
    last_diag = 0
    while time.time() < deadline:
        try:
            val = page.run_js("return (document.querySelector('#resultValue') || {}).value || ''")
        except Exception:
            val = ""
        val = (val or "").strip()
        if val:
            return val
        try:
            badge = page.run_js(
                "return document.querySelector('#statusBadge') ? document.querySelector('#statusBadge').innerText : ''"
            )
        except Exception:
            badge = ""
        # 每 20 秒打印一次诊断状态
        if time.time() - last_diag >= 20:
            last_diag = time.time()
            try:
                log = page.run_js(
                    "return document.querySelector('#logBox') ? document.querySelector('#logBox').innerText : ''"
                )
            except Exception:
                log = ""
            print(f"[诊断] badge={badge!r} logBox尾200={log[-200:]!r}")
        if ("失败" in badge) or ("错误" in badge) or ("failed" in badge.lower()):
            try:
                last_log = page.run_js(
                    "return document.querySelector('#logBox') ? document.querySelector('#logBox').innerText : ''"
                )
            except Exception:
                last_log = ""
            raise Exception(("提链失败: " + (last_log or badge))[:400])
        time.sleep(2)
    return ""


def _read_meta(page) -> dict:
    meta = {}
    for key, sel in {
        "type": "#resultType",
        "email": "#resultEmail",
        "region": "#resultRegion",
        "promo": "#resultPromo",
    }.items():
        try:
            meta[key] = page.run_js(f"return (document.querySelector('{sel}') || {{}}).innerText || ''")
        except Exception:
            meta[key] = ""
    return meta


def main() -> int:
    token = read_token_from_stdin()
    if not token:
        print("[ERROR] 未收到 access token")
        return 1

    pc = load_payment_config()
    url = str(pc.get("extractUrl") or "https://pay.153.ink/").strip()
    plan = str(pc.get("plan") or "plus").strip()
    channel = str(pc.get("channel") or "hosted").strip()
    country = str(pc.get("country") or "US").strip().upper()
    currency = str(pc.get("currency") or "USD").strip().upper()
    entry_proxy = str(pc.get("entryProxy") or "").strip()
    exit_proxy = str(pc.get("exitProxy") or "").strip()
    promo_campaign = str(pc.get("promoCampaign") or "").strip()
    retry_count = int(pc.get("retryCount") or 10)
    try_promo = bool(pc.get("tryPromo", False))
    use_sentinel = bool(pc.get("useSentinel", True))

    if not entry_proxy:
        print("[ERROR] 提链入口代理池(entryProxy)为空，pay.153.ink 任务必填")
        return 1

    # 订阅/空间映射：plan=codex → pay.153.ink 的 codex_low
    plan_value = "codex_low" if plan == "codex" else plan
    # 支付路径：channel 直接对应 pay.153.ink 的 link_type；custom 回退 paypal
    link_type = channel if channel in {"hosted", "ph_short", "paypal", "ideal", "upi", "pix", "momo", "gcash", "kakao"} else "paypal"

    co = ChromiumOptions()
    co.auto_port()
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-gpu")
    co.set_argument("--disable-dev-shm-usage")
    # 显式指定 Chromium 路径，避免 DrissionPage 自动探测失败卡住
    for _cp in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if os.path.isfile(_cp):
            co.set_browser_path(_cp)
            break
    tmp = tempfile.mkdtemp(prefix="pay153_")
    co.set_user_data_path(tmp)
    browser = Chromium(co)
    tabs = browser.get_tabs()
    page = tabs[-1] if tabs else browser.new_tab()

    try:
        page.get(url)
        time.sleep(4)

        # 1) Access Token
        if not _js_set_value(page, "#token", token):
            print("[ERROR] 未找到 token 输入框")
            return 1

        # 2) 订阅/空间
        _js_check_radio(page, f'input[name="plan"][value="{plan_value}"]')
        time.sleep(0.3)

        # 3) 支付路径
        _js_check_radio(page, f'input[name="link_type"][value="{link_type}"]')
        time.sleep(0.5)

        # 4) 国家/币种
        _js_select(page, "#country", country)
        _js_select(page, "#currency", currency)

        # 5) 代理池
        if not _js_set_value(page, "#entryProxy", entry_proxy):
            print("[ERROR] 未找到入口代理池输入框")
            return 1
        # exitProxy 必填，留空时复用入口代理池
        _js_set_value(page, "#exitProxy", exit_proxy or entry_proxy)

        # 6) 重试次数
        _js_set_value(page, "#retryCount", str(retry_count))

        # 7) 优惠活动 / SEN+SO 开关
        _js_set_checkbox(page, "#usePromo", try_promo)
        _js_set_checkbox(page, "#useSentinel", use_sentinel)
        if promo_campaign:
            _js_set_value(page, "#promoCampaign", promo_campaign)

        # 8) 提交（开始提炼）
        submit = page.ele("css:#submitButton", timeout=10)
        if submit is None:
            print("[ERROR] 未找到「开始提炼」按钮")
            return 1
        submit.click()

        # 9) 轮询结果
        result = _poll_result(page, timeout=300)
        if not result:
            print("[ERROR] 提链超时未返回结果")
            return 1

        meta = _read_meta(page)
        print(f"[META] type={meta.get('type','')} email={meta.get('email','')} region={meta.get('region','')} promo={meta.get('promo','')}")
        print(f"[RESULT] {result}")
        return 0
    finally:
        try:
            browser.quit()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
