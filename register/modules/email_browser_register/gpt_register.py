# -*- coding: utf-8 -*-
"""
GPT 注册机 - 自动化注册脚本（ChatGPT / OpenAI）· Playwright + stealth 反检测版

用 Playwright + playwright-stealth 替代 DrissionPage，以降低 Cloudflare/Arkose 人机验证触发率。
Playwright 原生支持带账号密码的代理（无需代理桥），配合干净住宅代理 + 有头浏览器（Xvfb）。

流程：
  chatgpt.com/auth/login → 邮箱 → （可选）密码 → 邮箱 OTP → about-you（姓名/生日）
  → 读取 /api/auth/session 的 accessToken → 检测 Plus 试用资格 → 输出 token 到文件。

输出协议（供后端 gptBot 解析）：
  [ACCOUNT] password=xxx
  [PLUS] eligible            /  [PLUS] not-eligible <reason>
  ✔ 第 N 轮成功 | email
  ✘ 第 N 轮失败 | reason
  注册完成，邮箱: xxx
"""
from __future__ import annotations

import os
import io
import sys
import json
import time
import uuid
import base64
import random
import string
import shutil
import tempfile
import argparse
import datetime
import logging
from pathlib import Path
from urllib.parse import urlparse

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import Stealth
except ImportError:
    Stealth = None

import requests

# 复用现有邮件取码能力（与 Grok 注册机一致：cloudflare / remail / auto）
from email_register import (
    get_email_and_token,
    get_manual_email,
    get_manual_code,
    get_oai_code,
    MAIL_MODE,
)

LOGIN_URL = os.environ.get("GPT_LOGIN_URL", "https://chatgpt.com/auth/login")
SESSION_API = os.environ.get("GPT_SESSION_API", "https://chatgpt.com/api/auth/session")
ACCOUNTS_CHECK_PATH = "/backend-api/accounts/check/v4-2023-04-27"

EMAIL_SELECTORS = ['input[type="email"]', 'input[name="email"]', 'input[autocomplete="email"]', 'input[id="email-input"]']
PASSWORD_SELECTORS = ['input[type="password"]', 'input[name="password"]', 'input[autocomplete="new-password"]']
OTP_SELECTORS = ['input[data-input-otp="true"]', 'input[autocomplete="one-time-code"]', 'input[name="code"]', 'input[inputmode="numeric"]']
NAME_SELECTORS = ['input[name="name"]', 'input[autocomplete="name"]', 'input[id="name"]']
BIRTH_SELECTORS = ['input[type="date"]', 'input[autocomplete="bday"]', 'input[name="birthday"]']

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_pw = None
_browser = None
_context = None
_page = None
run_logger: logging.Logger | None = None


def setup_run_logger() -> logging.Logger:
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"gpt_run_{ts}_{os.getpid()}.log")
    logger = logging.getLogger("gpt_register")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def gen_password() -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(16))


def random_adult_birthdate() -> str:
    year = random.randint(1970, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"


def _humanize(min_s=0.3, max_s=1.2):
    time.sleep(random.uniform(min_s, max_s))


def parse_proxy(proxy_url: str):
    if not proxy_url:
        return None
    if "://" not in proxy_url:
        proxy_url = "http://" + proxy_url
    u = urlparse(proxy_url)
    if not u.hostname:
        return None
    server = f"{u.scheme}://{u.hostname}:{u.port or 80}"
    return {"server": server, "username": u.username or "", "password": u.password or ""}


def build_stealth():
    if Stealth is None:
        return None
    try:
        return Stealth(
            navigator_user_agent=False,
            navigator_user_agent_data=False,
            navigator_platform=False,
            sec_ch_ua=False,
            webgl_vendor=False,
            chrome_runtime=True,
            chrome_app=True,
            chrome_csi=True,
            chrome_load_times=True,
            hairline=True,
            iframe_content_window=True,
            media_codecs=True,
            navigator_hardware_concurrency=True,
            navigator_languages=True,
            navigator_permissions=True,
            navigator_plugins=True,
            navigator_vendor=True,
            navigator_webdriver=True,
            error_prototype=True,
            navigator_languages_override=("en-US", "en"),
            init_scripts_only=True,
        )
    except Exception:
        return None


def start_browser():
    global _pw, _browser, _context, _page
    cfg = load_config()
    gpt_cfg = cfg.get("gpt", {}) or {}
    use_proxy = bool(gpt_cfg.get("use_proxy", False))
    proxy_url = gpt_cfg.get("proxy") or cfg.get("browser_proxy") or cfg.get("proxy") or ""

    _pw = sync_playwright().start()
    proxy_opt = parse_proxy(proxy_url) if use_proxy and proxy_url else None
    launch_kwargs = {
        "headless": False,
        "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
    }
    if proxy_opt:
        launch_kwargs["proxy"] = proxy_opt
    _browser = _pw.chromium.launch(**launch_kwargs)
    _context = _browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
        timezone_id="America/New_York",
        user_agent=UA,
    )
    stealth = build_stealth()
    if stealth:
        try:
            stealth.apply_stealth_sync(_context)
        except Exception:
            pass
    _page = _context.new_page()


def stop_browser():
    global _pw, _browser, _context, _page
    for obj in (_browser, _pw):
        if obj is not None:
            try:
                obj.close() if obj is _browser else obj.stop()
            except Exception:
                pass
    _browser = None
    _pw = None
    _context = None
    _page = None


def _first_locator(selectors):
    for sel in selectors:
        try:
            loc = _page.locator(sel).first
            if loc.count() > 0:
                return sel
        except Exception:
            continue
    return None


def wait_for_selector(selectors, timeout=15) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _first_locator(selectors):
            return True
        time.sleep(0.5)
    return False


def _has_captcha() -> bool:
    try:
        return bool(_page.evaluate(
            "() => Array.from(document.querySelectorAll('iframe')).some(f => /arkose|funcaptcha|turnstile|captcha|challenge/i.test(f.src || ''))"
        ))
    except Exception:
        return False


def wait_for_next_step(timeout=240) -> bool:
    """等待页面进入密码/OTP 页；若出现人机验证则提示用户去 VNC 手动完成并继续等待。"""
    deadline = time.time() + timeout
    captcha_notified = False
    while time.time() < deadline:
        if _has_captcha() and not captcha_notified:
            print("[提示] 检测到人机验证，请在 VNC 中手动完成（按住按钮继续）…")
            captcha_notified = True
        if _first_locator(PASSWORD_SELECTORS) or _first_locator(OTP_SELECTORS):
            return True
        time.sleep(2)
    return False


def detect_auth_state() -> str:
    """根据 URL 与输入框判断当前 OpenAI 认证状态。"""
    url = (_page.url or "").lower()
    if "/log-in/password" in url:
        return "login_password"
    if "email-verification" in url or "email_otp" in url:
        return "email_verification"
    if "about-you" in url or "/profile" in url:
        return "about_you"
    if "chatgpt.com" in url and "/auth/" not in url:
        return "chatgpt"
    if _first_locator(OTP_SELECTORS):
        return "email_verification"
    if _first_locator(NAME_SELECTORS) or _first_locator(BIRTH_SELECTORS):
        return "about_you"
    if "chatgpt.com/auth/login" in url:
        return "email_page"
    return "other"


def wait_auth_transition(timeout=30) -> str:
    """邮箱提交后等待跳转，返回最终状态。"""
    deadline = time.time() + timeout
    last = "other"
    captcha_notified = False
    while time.time() < deadline:
        if _has_captcha() and not captcha_notified:
            print("[提示] 检测到人机验证，请在 VNC 中手动完成…")
            captcha_notified = True
        s = detect_auth_state()
        if s not in ("other", "email_page"):
            return s
        last = s
        time.sleep(0.5)
    return last


def signin_openai_fetch(email: str) -> dict:
    """页内 fetch 调 signin 接口，拿到 auth.openai.com authorize URL（不依赖 UI 按钮）。"""
    did = uuid.uuid4().hex
    auth_log_id = uuid.uuid4().hex
    try:
        return _page.evaluate(
            r"""
            async ([email, did, authLogId]) => {
              try {
                const csrfResp = await fetch('/api/auth/csrf', {method:'GET', credentials:'include', headers:{'accept':'application/json'}});
                const csrfText = await csrfResp.text();
                let csrfData = {}; try { csrfData = JSON.parse(csrfText); } catch(_) {}
                const csrfToken = csrfData.csrfToken || '';
                if (!csrfResp.ok || !csrfToken) return {ok:false, stage:'csrf', status:csrfResp.status, body:csrfText.slice(0,300)};
                const q = new URLSearchParams({
                  prompt: 'login',
                  'ext-oai-did': did,
                  auth_session_logging_id: authLogId,
                  'ext-passkey-client-capabilities': '11111',
                  screen_hint: 'login_or_signup',
                  login_hint: email
                });
                const body = new URLSearchParams({ callbackUrl: 'https://chatgpt.com/', csrfToken, json: 'true' });
                const resp = await fetch('/api/auth/signin/openai?' + q.toString(), {
                  method:'POST', credentials:'include',
                  headers:{'accept':'application/json','content-type':'application/x-www-form-urlencoded','cache-control':'no-cache','pragma':'no-cache'},
                  body: body.toString()
                });
                const text = await resp.text();
                let data = {}; try { data = JSON.parse(text); } catch(_) {}
                let url = data.url || '';
                if (!resp.ok || !url) return {ok:false, stage:'signin', status:resp.status, body:text.slice(0,500)};
                try {
                  const u = new URL(url, location.href);
                  if (!u.searchParams.get('screen_hint')) u.searchParams.set('screen_hint', 'login_or_signup');
                  if (!u.searchParams.get('login_hint')) u.searchParams.set('login_hint', email);
                  if (!u.searchParams.get('ext-oai-did')) u.searchParams.set('ext-oai-did', did);
                  if (!u.searchParams.get('auth_session_logging_id')) u.searchParams.set('auth_session_logging_id', authLogId);
                  url = u.toString();
                } catch(_) {}
                return {ok:true, url:url};
              } catch(e) {
                return {ok:false, stage:'exception', error:String(e && (e.stack || e.message) || e).slice(0,400)};
              }
            }
            """,
            [email, did, auth_log_id],
        )
    except Exception as e:
        return {"ok": False, "stage": "evaluate_error", "error": str(e)[:300]}


def click_submit(timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        clicked = _page.evaluate(
            r"""
            () => {
              const btns = Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'));
              // 优先 type=submit
              let t = btns.find(b => (b.type || '').toLowerCase() === 'submit');
              // 其次精确匹配文本，避免点到 "Continue with Google" 等 SSO 按钮
              if (!t) {
                t = btns.find(b => {
                  const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                  return ['continue', 'continue →', 'next', 'next →', '继续', '继续 →', '下一步', 'get started'].includes(txt);
                });
              }
              if (!t) return false;
              t.click();
              return true;
            }
            """
        )
        if clicked:
            return True
        time.sleep(0.5)
    raise Exception("未找到提交按钮")


def click_onboarding_continue(timeout=30) -> bool:
    """登录后处理 ChatGPT 首次使用的 onboarding 引导按钮（Continue/Next/Get started/继续/下一步）。

    该引导页常在跳回 chatgpt.com 后延迟几秒出现，可能有多个步骤。
    循环检测并点击，直到不再出现引导按钮或超时。
    """
    deadline = time.time() + timeout
    clicked_any = False
    while time.time() < deadline:
        try:
            clicked = _page.evaluate(
                r"""
                () => {
                  const isVisible = (el) => {
                    if (!el) return false;
                    const s = getComputedStyle(el);
                    if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                  };
                  const keywords = ['continue', 'next', 'get started', '继续', '下一步'];
                  const btns = Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'))
                    .filter(isVisible)
                    .filter(b => !b.disabled && b.getAttribute('aria-disabled') !== 'true');
                  const t = btns.find(b => {
                    const txt = (b.innerText || b.textContent || b.value || '').replace(/\s+/g, ' ').trim().toLowerCase();
                    if (!txt) return false;
                    return keywords.some(k => txt === k || (txt.startsWith(k) && txt.length <= k.length + 4));
                  });
                  if (!t) return false;
                  t.click();
                  return true;
                }
                """
            )
        except Exception:
            clicked = False
        if clicked:
            clicked_any = True
            _humanize(1, 2)
            continue
        # 未发现引导按钮，onboarding 已完成
        break
    return clicked_any


def fill_input(selectors, value, timeout=15) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        for sel in selectors:
            try:
                locs = _page.locator(sel)
                n = locs.count()
                for i in range(n):
                    loc = locs.nth(i)
                    if not loc.is_visible():
                        continue
                    try:
                        loc.click()
                        loc.fill(value)
                    except Exception:
                        # fill 失败则逐字输入
                        loc.click()
                        loc.press_sequentially(value)
                    _humanize(0.2, 0.5)
                    # 校验值真的写进去了
                    try:
                        if (loc.input_value() or '').strip() == str(value).strip():
                            return True
                    except Exception:
                        pass
            except Exception:
                continue
        time.sleep(0.5)
    return False


def get_access_token() -> str | None:
    try:
        cookies = _context.cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
        ua = _page.evaluate("() => navigator.userAgent") or ""
        headers = {"cookie": cookie_str, "user-agent": ua}
        r = requests.get(SESSION_API, headers=headers, timeout=20)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return data.get("accessToken")
    except Exception:
        return None


def _decode_jwt_claims(access_token: str) -> dict:
    try:
        parts = (access_token or "").split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
    except Exception:
        return {}


def detect_plus_trial(access_token: str) -> tuple[bool | None, str]:
    claims = _decode_jwt_claims(access_token)
    auth = claims.get("https://api.openai.com/auth") or {}
    claim_account_id = auth.get("chatgpt_account_id")

    device_id = uuid.uuid4().hex
    url = f"https://chatgpt.com{ACCOUNTS_CHECK_PATH}?timezone_offset_min=-"

    # 用 Playwright 页面内 fetch（复用浏览器指纹和 session cookie，绕过 CF 拦截）
    try:
        result = _page.evaluate(
            """
            async ({url, deviceId, authToken, targetPath}) => {
                try {
                    const resp = await fetch(url, {
                        method: 'GET',
                        credentials: 'include',
                        headers: {
                            'accept': '*/*',
                            'authorization': 'Bearer ' + authToken,
                            'oai-device-id': deviceId,
                            'oai-language': 'en-US',
                            'referer': 'https://chatgpt.com/',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'same-origin',
                            'x-openai-target-path': targetPath,
                            'x-openai-target-route': targetPath,
                        }
                    });
                    const status = resp.status;
                    const text = await resp.text();
                    let data = {};
                    try { data = JSON.parse(text); } catch(e) {}
                    return { status, data };
                } catch(e) {
                    return { status: 0, error: String(e && (e.message || e)) };
                }
            }
            """,
            {"url": url, "deviceId": device_id, "authToken": access_token, "targetPath": ACCOUNTS_CHECK_PATH}
        )
        status = result.get("status")
        if status != 200:
            err = result.get("error") or ""
            return None, f"套餐查询接口返回 HTTP {status}" + (f" ({err[:100]})" if err else "")
        data = result.get("data") or {}
    except Exception as e:
        return None, f"套餐查询接口异常: {e}"

    accounts = data.get("accounts") if isinstance(data, dict) else None
    if not isinstance(accounts, dict):
        return None, "响应缺少 accounts 对象"

    item = None
    if claim_account_id and isinstance(accounts.get(claim_account_id), dict):
        item = accounts.get(claim_account_id)
    elif isinstance(accounts.get("default"), dict):
        item = accounts.get("default")
    else:
        for k, v in accounts.items():
            if k != "default" and isinstance(v, dict):
                item = v
                break
    if not isinstance(item, dict):
        return None, "未找到可解析的账号条目"

    account = item.get("account") or {}
    entitlement = item.get("entitlement") or {}
    plan_type = account.get("plan_type") or auth.get("chatgpt_plan_type") or ""
    subscription_plan = entitlement.get("subscription_plan") or ""
    is_free = str(plan_type).lower() == "free" or str(subscription_plan).lower() == "chatgptfreeplan"
    promos = item.get("eligible_promo_campaigns") or {}
    plus_campaign = promos.get("plus") if isinstance(promos, dict) else None
    plus_trial_eligible = bool(is_free and plus_campaign)

    if plus_trial_eligible:
        return True, f"具备 Plus 试用资格 (plan={plan_type})"
    return False, f"不具备 Plus 试用资格 (plan={plan_type or subscription_plan or 'unknown'})"


def _fill_spinbutton_birthday(year: str, month: str, day: str) -> bool:
    """React Aria spinbutton 年/月/日控件填写。"""
    ok = False
    for selector, value in [
        ('[role="spinbutton"][data-type="year"]', str(year)),
        ('[role="spinbutton"][data-type="month"]', str(int(month)).zfill(2)),
        ('[role="spinbutton"][data-type="day"]', str(int(day)).zfill(2)),
    ]:
        try:
            loc = _page.locator(selector).first
            if loc.count() == 0:
                continue
            loc.click()
            _page.keyboard.press("Control+A")
            _page.keyboard.press("Backspace")
            _page.keyboard.type(str(value), delay=40)
            ok = True
        except Exception:
            pass
    return ok


def fill_about_you(name: str, birth_date: str):
    """JS 全量兜底填写 about-you/profile：姓名 + 生日 + 勾选协议 + 提交。"""
    try:
        year, month, day = birth_date.split("-")
    except Exception:
        year, month, day = "1995", "01", "01"
    try:
        from datetime import date as _date
        _today = _date.today()
        age = max(18, min(60, _today.year - int(year) - ((_today.month, _today.day) < (int(month), int(day)))))
    except Exception:
        age = 25

    result = _page.evaluate(
        r"""
        ({name, birthday, year, month, day, age}) => {
          const month2 = String(month).padStart(2, '0');
          const day2 = String(day).padStart(2, '0');
          const visible = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
            && getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).display !== 'none'
            && !el.disabled && !el.readOnly;
          const setValue = (el, value) => {
            if (!el) return false;
            try { el.scrollIntoView?.({block:'center'}); el.focus?.(); } catch(e) {}
            const tag = (el.tagName || '').toLowerCase();
            const proto = tag === 'textarea' ? HTMLTextAreaElement.prototype : tag === 'select' ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
            if (setter) setter.call(el, String(value)); else el.value = String(value);
            if (tag === 'select') { [...el.options].forEach(opt => { opt.selected = String(opt.value) === String(value) || String(opt.textContent || '').trim() === String(value); }); }
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            try { el.blur?.(); } catch(e) {}
            return true;
          };
          const hay = el => [el.name, el.id, el.placeholder, el.getAttribute('aria-label'), el.autocomplete, el.getAttribute('data-testid')].join(' ').toLowerCase();
          const allInputs = [...document.querySelectorAll('input, textarea')].filter(visible);
          const filled = {};

          const nameInput = allInputs.find(el => /(name|full.?name|user.?name|名前|氏名|姓名)/i.test(hay(el)) && !/(month|day|year|age|birth|code|email|phone|password)/i.test(hay(el)))
            || allInputs.find(el => ['text',''].includes((el.type||'').toLowerCase()) && !/(code|email|phone|tel|number|password|month|day|year|age|birth)/i.test(hay(el)));
          if (nameInput) filled.name = setValue(nameInput, name);

          const ageInput = allInputs.find(el => /(age|年齢|年龄)/i.test(hay(el)) || ((el.type||'').toLowerCase()==='number' && !/(day|month|year)/i.test(hay(el))));
          if (ageInput) filled.age = setValue(ageInput, age);

          const dateInput = [...document.querySelectorAll('input[name="birthdate"], input[type="date"], input[name="birthday"]')].find(el => visible(el) || String(el.getAttribute('type')||'').toLowerCase()==='date');
          if (dateInput) filled.birthdate = setValue(dateInput, birthday);

          const setFirst = (selectors, values, key) => {
            for (const sel of selectors) for (const el of [...document.querySelectorAll(sel)]) {
              if (!visible(el)) continue;
              for (const val of values) {
                if ((el.tagName||'').toLowerCase()==='select') { const has=[...el.options].some(o=>String(o.value)===String(val)||String(o.textContent||'').trim()===String(val)); if(!has) continue; }
                if (setValue(el, val)) { filled[key]=val; return true; }
              }
            }
            return false;
          };
          const yOk = setFirst(['select[name="year"]','input[name="year"]','select[id*="year"]','input[id*="year"]','input[aria-label*="year" i]'], [year], 'year');
          const mOk = setFirst(['select[name="month"]','input[name="month"]','select[id*="month"]','input[id*="month"]','input[aria-label*="month" i]'], [month, month2], 'month');
          const dOk = setFirst(['select[name="day"]','input[name="day"]','select[id*="day"]','input[id*="day"]','input[aria-label*="day" i]'], [day, day2], 'day');
          if (yOk && mOk && dOk) { const hidden = document.querySelector('input[name="birthday"],input[name="birthdate"]'); if (hidden) setValue(hidden, birthday); filled.ymd = true; }

          // React Aria 隐藏 select：按 option 范围推断年/月/日
          const selects = [...document.querySelectorAll('[data-testid="hidden-select-container"] select, .react-aria-Select select, select')].filter(el => !el.disabled);
          const nums = sel => [...sel.options].map(o=>Number(o.value)).filter(Number.isFinite);
          const maxNum = sel => Math.max(...nums(sel), -Infinity);
          const minNum = sel => Math.min(...nums(sel), Infinity);
          const hasOption = (sel, val) => [...sel.options].some(o=>String(o.value)===String(val));
          const yearSelects = selects.filter(sel => hasOption(sel, year) && maxNum(sel) > 1900);
          const smallSelects = selects.filter(sel => !yearSelects.includes(sel));
          const monthSelects = smallSelects.filter(sel => (hasOption(sel, month)||hasOption(sel, month2)) && minNum(sel) <= 1 && maxNum(sel) <= 12);
          const daySelects = smallSelects.filter(sel => (hasOption(sel, day)||hasOption(sel, day2)) && maxNum(sel) >= 28);
          let birthMode = filled.age ? 'age' : (filled.birthdate ? 'birthdate' : (filled.ymd ? 'ymd' : null));
          if (!birthMode && yearSelects.length && monthSelects.length && daySelects.length) {
            setValue(yearSelects[0], year);
            setValue(monthSelects[0], hasOption(monthSelects[0], month) ? month : month2);
            const ds = daySelects.find(x => x !== monthSelects[0]) || daySelects[0];
            setValue(ds, hasOption(ds, day) ? day : day2);
            const hidden = document.querySelector('input[name="birthday"],input[name="birthdate"]'); if (hidden) setValue(hidden, birthday);
            filled.reactSelect = true; birthMode = 'react_select';
          }

          // checkbox
          const isChecked = el => el.checked === true || String(el.getAttribute('aria-checked') || el.closest('[role="checkbox"]')?.getAttribute('aria-checked') || '').toLowerCase() === 'true';
          const mark = el => {
            if (!el || isChecked(el)) return false;
            const label = el.closest('label');
            try { (label && visible(label) ? label : el).scrollIntoView({block:'center'}); (label && visible(label) ? label : el).click(); } catch(e) {}
            if (!isChecked(el)) { const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'checked')?.set; if (setter) setter.call(el, true); else el.checked = true; el.dispatchEvent(new MouseEvent('click',{bubbles:true})); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }
            return isChecked(el);
          };
          let checkboxCount = 0;
          for (const box of [...document.querySelectorAll('input[type="checkbox"]')].filter(el => visible(el) || visible(el.closest('label')))) { if (mark(box)) checkboxCount += 1; }

          // submit
          const forms = [...document.querySelectorAll('form')].filter(el => !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length));
          let submitClicked = false;
          for (const form of forms) { const s = form.querySelector('button[type="submit"], input[type="submit"]'); if (s && visible(s) && !s.disabled && s.getAttribute('aria-disabled') !== 'true') { s.scrollIntoView({block:'center'}); s.click(); submitClicked = true; break; } }
          if (!submitClicked) { const buttons = [...document.querySelectorAll('button,input[type="submit"],[role="button"]')].filter(visible); const scored = buttons.map((el,idx)=>{const t=[el.innerText,el.textContent,el.value,el.getAttribute('aria-label'),el.type].join(' ').toLowerCase(); let score=0; if(el.disabled||el.getAttribute('aria-disabled')==='true')score=-100; else if((el.type||'').toLowerCase()==='submit')score=95; else if(/(continue|next|done|submit|create|start|继续|下一步|完成|提交)/i.test(t))score=90; return {el,score,text:(el.innerText||el.textContent||el.value||'').trim()};}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score); if(scored.length){scored[0].el.scrollIntoView({block:'center'});scored[0].el.click();submitClicked=true;} }

          return { ok: Boolean((filled.name || filled.firstName) && birthMode), submitted: submitClicked, birthMode, filled, checkboxCount, url: location.href };
        }
        """,
        {"name": name, "birthday": birth_date, "year": year, "month": month, "day": day, "age": age},
    )
    print(f"[*] about-you 填写结果: {result}")
    _humanize(2, 4)


def run_single_registration(output_path: str, cfg: dict) -> dict:
    gpt_cfg = cfg.get("gpt", {})
    register_password = gpt_cfg.get("register_password") or gen_password()
    display_name = gpt_cfg.get("display_name") or ("User" + "".join(random.choices(string.ascii_letters, k=5)))
    birth_date = gpt_cfg.get("birth_date") or random_adult_birthdate()

    _page.goto(LOGIN_URL, wait_until="domcontentloaded")
    _humanize(2, 4)

    # 1. 邮箱
    print(f"[*] 等待邮箱（收信方式: {MAIL_MODE}）…")
    email = None
    jwt = None
    if MAIL_MODE == "cloudflare":
        email, jwt = get_email_and_token()
    else:
        email = get_manual_email()
        if not email and MAIL_MODE == "auto":
            email, jwt = get_email_and_token()
    if not email:
        raise Exception("获取邮箱失败")

    if not fill_input(EMAIL_SELECTORS, email):
        _t = _page.title()
        _u = _page.url
        _b = _page.evaluate("() => (document.body ? document.body.innerText : '').slice(0,200)")
        raise Exception(f"未找到邮箱输入框 | title={_t} url={_u} body={_b}")
    _humanize(0.5, 1.2)
    print(f"[*] 已填写邮箱: {email}")

    # 通过页内 fetch 调 signin 拿 authorize URL，跳转 auth.openai.com（不依赖 UI 按钮）
    sig = signin_openai_fetch(email)
    if sig.get("ok") and sig.get("url"):
        print("[*] signin 成功，跳转 auth.openai.com")
        _page.goto(sig["url"], wait_until="domcontentloaded")
    else:
        print(f"[*] signin fetch 失败: {sig}，回退 UI 提交")
        click_submit()
    _humanize(2, 4)

    # 2. 等待跳转到 auth.openai.com（email-verification / log-in-password / about-you / chatgpt）
    state = wait_auth_transition(timeout=40)

    # 邮箱已注册/不可用 → 登录密码页
    if state == "login_password":
        raise Exception("邮箱已注册/不可用（进入登录密码页）")

    # 仍停留邮箱页 → 重试一次提交
    if state == "email_page":
        print("[*] 仍停留邮箱页，重试提交一次…")
        if fill_input(EMAIL_SELECTORS, email):
            click_submit()
            _humanize(2, 4)
        state = wait_auth_transition(timeout=40)

    if state == "login_password":
        raise Exception("邮箱已注册/不可用（进入登录密码页）")

    # 3. 邮箱验证码（OTP-only，无密码页）
    if state == "email_verification":
        code = None
        if MAIL_MODE == "cloudflare" and jwt:
            print("[*] Cloudflare 收信：等待验证码邮件…")
            code = get_oai_code(jwt, email, timeout=180)
        else:
            print("[*] 等待验证码：优先从手动验证码队列获取…")
            code = get_manual_code()
            if not code and jwt:
                code = get_oai_code(jwt, email, timeout=180)
        if not code:
            raise Exception("获取验证码失败")
        code = str(code).replace("-", "")
        if not fill_input(OTP_SELECTORS, code):
            raise Exception("未找到验证码输入框")
        click_submit()
        print("[*] 已提交邮箱验证码")
        _humanize(3, 6)
    else:
        print(f"[*] 邮箱提交后状态: {state}，继续后续流程")

    # 4. about-you（姓名 + 生日 + 同意协议）
    # 提交验证码后需等待页面跳转并加载完成，严格判断进入 about-you 再填表
    _pdeadline = time.time() + 45
    entered_about = False
    while time.time() < _pdeadline:
        state = detect_auth_state()
        # 严格判断：URL 已进入 about-you/profile，或已回到 chatgpt 主页
        if state in ("about_you", "chatgpt"):
            entered_about = True
            break
        # about-you 专属控件出现才认为页面就绪（年龄 spinbutton / 生日 / 姓名）
        if _first_locator(['[role="spinbutton"]', 'input[name="age"]', 'input[autocomplete="bday"]', 'input[type="date"]', 'input[autocomplete="name"]']):
            entered_about = True
            break
        time.sleep(1)

    if not entered_about:
        _cur_url = _page.url or ""
        raise Exception(f"验证码提交后未进入 about-you（当前: {_cur_url}），验证码可能错误或已过期")

    fill_about_you(display_name, birth_date)

    # 5. about-you 提交后，等待账号创建完成，然后主动回 chatgpt.com 读取 accessToken
    print("[*] about-you 已提交，等待账号创建完成...")
    time.sleep(8)
    access_token = None
    session_full = None
    _tdeadline = time.time() + 90
    while time.time() < _tdeadline:
        try:
            # 主动导航到 chatgpt.com 首页（触发 session 建立）
            _page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)
            # 再导航到 session API 读取完整 JSON 响应体
            _page.goto("https://chatgpt.com/api/auth/session", wait_until="domcontentloaded", timeout=15000)
            time.sleep(1)
            session_text = _page.evaluate("() => document.body.innerText || document.body.textContent || ''")
            if session_text:
                import json
                session_data = json.loads(session_text)
                access_token = session_data.get("accessToken") or session_data.get("access_token")
                if access_token:
                    session_full = session_data
                    print(f"[*] 成功读取 accessToken（长度 {len(access_token)}）")
                    break
                else:
                    print("[*] session 暂无 accessToken，继续等待...")
        except Exception as e:
            pass
        time.sleep(5)
    if not access_token:
        raise Exception("未能读取 accessToken（可能注册未完成或页面结构变化）")

    # 5.5 处理登录后延迟出现的 onboarding 引导（Continue/Next 按钮）
    if click_onboarding_continue(timeout=30):
        print("[*] 已自动点击登录后的 Continue 引导按钮")

    # 6. Plus 试用资格检测
    plus_eligible: bool | None = None
    plus_reason = ""
    if gpt_cfg.get("payment", {}).get("plusTrialCheck", True):
        plus_eligible, plus_reason = detect_plus_trial(access_token)
        if plus_eligible is True:
            print("[PLUS] eligible")
        else:
            print(f"[PLUS] not-eligible {plus_reason}")

    # 7. 输出 token（完整 session JSON，供提炼支付链接使用）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    session_output = json.dumps(session_full or {}, ensure_ascii=False)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(session_output + "\n")

    print(f"[ACCOUNT] password={register_password}")
    print(f"注册完成，邮箱: {email}")
    return {"email": email, "password": register_password, "token": access_token, "session": session_full, "plusEligible": plus_eligible}


def main():
    global run_logger
    run_logger = setup_run_logger()
    cfg = load_config()
    config_count = int((cfg.get("run", {}) or {}).get("count", 1))

    parser = argparse.ArgumentParser(description="GPT 自动注册机")
    parser.add_argument("--count", type=int, default=config_count)
    parser.add_argument("--output", default="gpt_tokens.txt")
    args = parser.parse_args()

    total = args.count if args.count > 0 else "∞"
    print("")
    print("══════════════════════════════════════")
    print(f"  GPT 注册机启动 | 计划轮数: {total}")
    print("══════════════════════════════════════")

    current_round = 0
    success_count = 0
    fail_count = 0
    try:
        start_browser()
        while True:
            if args.count > 0 and current_round >= args.count:
                break
            current_round += 1
            print("")
            print(f"─── 第 {current_round}/{total} 轮 ────────────────────────")
            try:
                result = run_single_registration(args.output, cfg)
                success_count += 1
                print(f"✔ 第 {current_round} 轮成功 | {result['email']}")
            except KeyboardInterrupt:
                print("[Info] 收到中断信号，停止后续轮次。")
                break
            except Exception as error:
                fail_count += 1
                print(f"✘ 第 {current_round} 轮失败 | {error}")
            finally:
                stop_browser()
                if args.count == 0 or current_round < args.count:
                    start_browser()
    finally:
        stop_browser()
        print("")
        print("══════════════════════════════════════")
        print(f"  注册机运行结束 | 成功: {success_count} 失败: {fail_count}")
        print("══════════════════════════════════════")


if __name__ == "__main__":
    main()
