# -*- coding: utf-8 -*-
"""
GPT 注册机 - 支付页面表单 agent（长驻进程）

由后端 gptBot 以 `python -u payment_agent.py` 启动，通过 stdin/stdout 以 JSONL（每行一个 JSON）交互：
  入站: {"id": N, "cmd": "inspect"|"fill"|"submit"|"quit", ...}
  出站: {"id": N, "ok": true|false, ...}

安全要求：
  - 支付数据（卡号/CVV 等）仅经 stdin 传入，绝不打日志、不落盘、不回显。
  - 出站消息不包含任何卡号、CVV 等敏感值，只回填字段 key 与脱敏/通用诊断信息。
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
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from DrissionPage import Chromium, ChromiumOptions

browser = None
page = None
co = ChromiumOptions()
_temp_dir = ""

# 字段类型 → 匹配关键词（用于从 name/id/label/autocomplete/placeholder 推断）
FIELD_RULES = {
    "card_number": ["cc-number", "cardnumber", "card number", "card_number", "cardnum", "pan"],
    "cvv": ["cvv", "cvc", "cc-csc", "security code", "csc", "securitycode"],
    "expiry": ["expiry", "expiration", "exp", "expdate", "mm/yy", "mm / yy", "exp-date"],
    "country": ["country", "countrycode", "billingcountry"],
    "name": ["name", "holder", "cardholder", "fullname", "firstname", "lastname"],
    "email": ["email"],
    "address": ["address", "street", "billingaddress"],
    "zip": ["zip", "postal", "postcode"],
    "phone": ["phone", "tel", "mobile"],
}


def out(obj: dict):
    """向 stdout 写一行 JSON（唯一输出通道，禁止其他 print）。"""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def start_browser():
    global browser, page, _temp_dir
    _temp_dir = tempfile.mkdtemp(prefix="pay_chrome_")
    co.auto_port()
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-gpu")
    co.set_argument("--disable-dev-shm-usage")
    co.set_user_data_path(_temp_dir)
    browser = Chromium(co)
    tabs = browser.get_tabs()
    page = tabs[-1] if tabs else browser.new_tab()
    return browser, page


def stop_browser():
    global browser, page, _temp_dir
    if browser is not None:
        try:
            browser.quit()
        except Exception:
            pass
    browser = None
    page = None
    if _temp_dir and os.path.isdir(_temp_dir):
        shutil.rmtree(_temp_dir, ignore_errors=True)
    _temp_dir = ""


def classify_field(el) -> str:
    """根据元素的属性推断字段类型。"""
    def lower(*vals):
        return " ".join(str(v or "") for v in vals).lower()

    el_type = lower(el.attr("type") or "")
    name = lower(el.attr("name") or "")
    el_id = lower(el.attr("id") or "")
    autocomplete = lower(el.attr("autocomplete") or "")
    placeholder = lower(el.attr("placeholder") or "")
    label = ""
    try:
        lab = el.ele("xpath:preceding::label[1]", timeout=0)
        label = lower(lab.text if lab else "")
    except Exception:
        pass

    haystack = f"{el_type} {name} {el_id} {autocomplete} {placeholder} {label}"

    if "email" in el_type or "email" in autocomplete or "email" in name:
        return "email"
    if "tel" in el_type or "phone" in name or "phone" in autocomplete:
        return "phone"

    for field_type, kws in FIELD_RULES.items():
        if any(kw in haystack for kw in kws):
            return field_type
    return "unknown"


def collect_fields() -> list:
    """扫描页面输入框与下拉框，返回字段描述列表。"""
    fields = []
    try:
        elements = page.eles("css:input, select, textarea", timeout=8)
    except Exception:
        elements = []
    seen = set()
    for idx, el in enumerate(elements or []):
        try:
            tag = el.tag
            el_type = (el.attr("type") or "").lower()
            if el_type in ("hidden", "submit", "button", "reset"):
                continue
            name = el.attr("name") or ""
            el_id = el.attr("id") or ""
            autocomplete = el.attr("autocomplete") or ""
            placeholder = el.attr("placeholder") or ""
            key = f"{tag}:{name or el_id or placeholder or idx}"
            if key in seen:
                continue
            seen.add(key)
            ft = classify_field(el)
            label = placeholder or name or el_id or autocomplete or ft
            field = {"key": key, "type": ft, "label": label, "required": False}
            if tag == "select":
                opts = []
                for o in el.eles("css:option", timeout=0) or []:
                    t = (o.text or "").strip()
                    if t:
                        opts.append(t)
                field["options"] = opts
            fields.append(field)
        except Exception:
            continue
    return fields


def fill_element(el, value: str):
    """向 input/select/textarea 填写值（触发 React 事件）。"""
    tag = (el.tag or "").lower()
    if tag == "select":
        page.run_js(
            "const s=arguments[0]; const v=arguments[1];"
            "for(const o of s.options){if((o.value||'').toLowerCase()===(v||'').toLowerCase()||(o.text||'').toLowerCase()===(v||'').toLowerCase()){s.value=o.value;}}"
            "s.dispatchEvent(new Event('change',{bubbles:true}));",
            el,
            value,
        )
        return
    page.run_js(
        "const el=arguments[0]; const v=arguments[1];"
        "const proto = el.tagName==='TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;"
        "const setter = Object.getOwnPropertyDescriptor(proto,'value').set;"
        "setter.call(el, v);"
        "el.dispatchEvent(new Event('input',{bubbles:true}));"
        "el.dispatchEvent(new Event('change',{bubbles:true}));",
        el,
        value,
    )


def do_inspect(req: dict):
    global page
    url = str(req.get("url", "")).strip()
    if not url:
        return {"ok": False, "error": "缺少支付链接 url"}
    start_browser()
    page.get(url)
    time.sleep(5)
    # 若存在 iframe 支付页，尝试切换到 iframe 内（Stripe/Checkout 常见）
    try:
        frames = page.eles("css:iframe", timeout=3)
        if frames:
            inner = frames[0].inner_page
            if inner:
                page = inner
    except Exception:
        pass
    title = ""
    try:
        title = page.title
    except Exception:
        pass
    fields = collect_fields()
    return {"ok": True, "targetUrl": page.url or url, "pageTitle": title, "fields": fields}


def find_element_by_key(key: str):
    """按 key 反查元素。key 形如 tag:name 或 tag:id 或 tag:placeholder。"""
    tag, _, ident = key.partition(":")
    if not ident:
        return None
    try:
        if tag == "select":
            return page.ele(f"css:select[name='{ident}'], select#{ident}", timeout=2)
        return page.ele(f"css:{tag}[name='{ident}'], {tag}#{ident}, {tag}[placeholder='{ident}']", timeout=2)
    except Exception:
        return None


def do_fill(req: dict):
    payload = req.get("payload") or {}
    fields = collect_fields()
    # 字段类型 → 待填值映射（仅内存）
    value_map = {
        "card_number": (payload.get("cardNumber") or "").replace(" ", ""),
        "cvv": payload.get("cvv") or "",
        "expiry": payload.get("expiry") or "",
        "country": payload.get("country") or "",
        "name": payload.get("name") or "",
        "email": payload.get("email") or "",
        "address": payload.get("address") or "",
        "zip": payload.get("zip") or "",
        "phone": payload.get("phone") or "",
    }
    filled = []
    unmatched = []
    for f in fields:
        val = value_map.get(f["type"], "")
        if not val:
            if f["type"] != "unknown":
                unmatched.append(f["key"])
            continue
        el = find_element_by_key(f["key"])
        if el is None:
            unmatched.append(f["key"])
            continue
        try:
            fill_element(el, val)
            filled.append(f["key"])
        except Exception:
            unmatched.append(f["key"])
    return {"ok": True, "filled": filled, "unmatched": unmatched}


def do_submit():
    clicked = False
    for _ in range(20):
        clicked = page.run_js(
            r"""
            const btns = Array.from(document.querySelectorAll('button, input[type="submit"], [role="button"]'));
            const t = btns.find(b => {
                const txt = ((b.innerText||b.textContent||b.value||'')).replace(/\s+/g,'').toLowerCase();
                return ['pay','支付','submit','提交','confirm','确认','subscribe','订阅','order','下单','continue','继续'].some(k => txt.includes(k));
            });
            if (!t) return false;
            t.click();
            return true;
            """
        )
        if clicked:
            break
        time.sleep(1)
    if not clicked:
        return {"ok": True, "status": "failed", "message": "未找到提交按钮"}

    time.sleep(8)
    url = (page.url or "").lower()
    html = ""
    try:
        html = (page.html or "").lower()
    except Exception:
        pass

    # 结果判定（启发式，可扩展）
    if any(k in html for k in ["3ds", "verify", "challenge", "authentication", "otp", "验证"]):
        return {"ok": True, "status": "needs_verification", "message": "需要额外验证（3DS/OTP）"}
    if any(k in html for k in ["thank you", "success", "succeeded", "支付成功", "order confirmed", "confirmation"]):
        return {"ok": True, "status": "success", "message": "支付提交成功"}
    if any(k in html for k in ["declined", "failed", "error", "支付失败", "拒绝"]):
        return {"ok": True, "status": "failed", "message": "支付被拒绝或失败"}
    # 页面结构变化（URL 跳转但未识别到明确结果）
    return {"ok": True, "status": "page_changed", "message": "页面结构发生变化，请人工核对支付结果"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            out({"id": 0, "ok": False, "error": "invalid json"})
            continue
        cmd = req.get("cmd")
        rid = req.get("id", 0)
        try:
            if cmd == "inspect":
                out({"id": rid, **do_inspect(req)})
            elif cmd == "fill":
                out({"id": rid, **do_fill(req)})
            elif cmd == "submit":
                out({"id": rid, **do_submit()})
            elif cmd == "quit":
                out({"id": rid, "ok": True})
                break
            else:
                out({"id": rid, "ok": False, "error": f"unknown cmd: {cmd}"})
        except Exception as e:
            out({"id": rid, "ok": False, "error": str(e)})
    stop_browser()


if __name__ == "__main__":
    main()
