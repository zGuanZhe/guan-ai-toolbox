#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""浏览器化验活：用 DrissionPage 打开 grok get-user，处理 Turnstile，输出用户 JSON 文本。"""
import sys
import os
import json
import time
import argparse
import glob
import platform

sys.path.insert(0, os.path.dirname(__file__))

from DrissionPage import Chromium, ChromiumOptions


def solve_turnstile(page, timeout=40):
    """拟人化处理 CF Turnstile：不需要验证就等待，出现验证框就点击。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            has = page.run_js(
                "return !!document.querySelector('iframe[src*=turnstile], [id*=turnstile], input[name=cf-turnstile-response]')"
            )
            if not has:
                return True
            resp = page.run_js("try { return turnstile.getResponse() } catch(e) { return null }")
            if resp:
                return True
            try:
                frame = page.ele("css:iframe[src*=turnstile]", timeout=2)
                if frame:
                    frame.run_js(
                        "window.dtp=1;"
                        "Object.defineProperty(MouseEvent.prototype,'screenX',{value:800+Math.random()*400});"
                        "Object.defineProperty(MouseEvent.prototype,'screenY',{value:400+Math.random()*200});"
                    )
                    frame.ele("tag:input", timeout=2).click()
            except Exception:
                pass
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sso", required=True)
    parser.add_argument("--proxy", default="")
    parser.add_argument("--timeout", type=int, default=50)
    args = parser.parse_args()

    co = ChromiumOptions()
    co.auto_port()
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-gpu")
    co.set_argument("--disable-dev-shm-usage")
    if args.proxy:
        co.set_proxy(args.proxy)
    if platform.system() == "Linux":
        pw = glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"))
        if pw:
            co.set_browser_path(pw[0])
        else:
            for c in ["/usr/bin/chromium-browser", "/usr/bin/chromium", "/usr/bin/google-chrome"]:
                if os.path.isfile(c):
                    co.set_browser_path(c)
                    break

    browser = None
    try:
        browser = Chromium(co)
        tab = browser.latest_tab
        tab.get("https://grok.com", timeout=30)
        try:
            tab.set.cookies([
                {"name": "sso", "value": args.sso, "domain": ".grok.com", "path": "/"},
                {"name": "sso-rw", "value": args.sso, "domain": ".grok.com", "path": "/"},
            ])
        except Exception:
            pass
        tab.get("https://grok.com/rest/auth/get-user", timeout=30)
        solve_turnstile(tab, args.timeout)
        # CF 验证通过后过渡页（"Waiting for grok.com to respond"）会在几秒后跳转到实际 JSON，
        # 因此耐心轮询等待真正的 JSON 响应
        body = ""
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                body = tab.ele("tag:body", timeout=5).text or ""
                if body.strip().startswith("{"):
                    break
            except Exception:
                pass
            time.sleep(1)
        try:
            parsed = json.loads(body)
            print(json.dumps(parsed, ensure_ascii=False))
        except Exception:
            print(body[:4000])
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if browser is not None:
            try:
                browser.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()
