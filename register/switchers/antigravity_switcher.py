# -*- coding: utf-8 -*-
"""
Antigravity / Gemini 账号池与一键轮换器
参考 Antigravity-Manager，管理多 Google / Gemini 账号凭证切换。
"""

import os
import json
import shutil
import datetime
from typing import List, Optional
from core.base_account_pool import BaseAccountPool, AccountRecord

class AntigravityAccountSwitcher:
    def __init__(self):
        self.pool = BaseAccountPool("antigravity")
        self.gemini_dir = os.path.join(os.path.expanduser("~"), ".gemini")
        self.oauth_file = os.path.join(self.gemini_dir, "oauth_creds.json")
        self.accounts_file = os.path.join(self.gemini_dir, "google_accounts.json")
        self._sync_current_account()

    def _sync_current_account(self):
        cur_email = ""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    accs = json.load(f)
                    if isinstance(accs, dict):
                        cur_email = accs.get("active", "")
                    elif isinstance(accs, list) and accs:
                        cur_email = accs[0].get("email", "")
            except Exception:
                pass

        if cur_email:
            tok = ""
            if os.path.exists(self.oauth_file):
                try:
                    with open(self.oauth_file, "r", encoding="utf-8") as f:
                        oc = json.load(f)
                        tok = oc.get("access_token", "")
                except Exception:
                    pass

            self.pool.add_or_update_account(AccountRecord(
                id=f"gemini-{cur_email}",
                provider="antigravity",
                email=cur_email,
                token=tok,
                is_active=True,
                updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

    def list_accounts(self) -> List[AccountRecord]:
        self._sync_current_account()
        return self.pool.load_accounts()

    def switch_to(self, email_or_id: str) -> bool:
        accounts = self.list_accounts()
        target = None
        for a in accounts:
            if a.id == email_or_id or a.email.lower() == email_or_id.lower() or a.id.replace("gemini-", "").lower() == email_or_id.lower():
                target = a
                break

        if not target:
            print(f"[!] Antigravity 账号池中未找到: {email_or_id}")
            return False

        target_email = target.email
        print(f"[*] 正在轮换 Antigravity 账号至: {target_email} ...")

        # 1. 备份当前活跃凭据到其个人档案目录
        profiles_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gemini_profiles")
        os.makedirs(profiles_base, exist_ok=True)

        cur_email = ""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    cur_data = json.load(f)
                    cur_email = cur_data.get("active", "")
            except Exception:
                pass

        if cur_email:
            cur_prof = os.path.join(profiles_base, cur_email)
            os.makedirs(cur_prof, exist_ok=True)
            if os.path.exists(self.oauth_file):
                shutil.copy2(self.oauth_file, os.path.join(cur_prof, "oauth_creds.json"))
            if os.path.exists(self.accounts_file):
                shutil.copy2(self.accounts_file, os.path.join(cur_prof, "google_accounts.json"))

        # 2. 从目标档案目录恢复或写入目标凭据
        tgt_prof = os.path.join(profiles_base, target_email)
        tgt_oauth = os.path.join(tgt_prof, "oauth_creds.json")
        tgt_accs = os.path.join(tgt_prof, "google_accounts.json")

        if os.path.exists(tgt_oauth):
            shutil.copy2(tgt_oauth, self.oauth_file)
        elif target.token:
            # 写入目标 token
            try:
                new_oauth = {
                    "access_token": target.token,
                    "refresh_token": target.extra.get("refresh_token", ""),
                    "token_type": "Bearer",
                    "expiry_date": int(datetime.datetime.now().timestamp() * 1000) + 3600000
                }
                with open(self.oauth_file, "w", encoding="utf-8") as f:
                    json.dump(new_oauth, f, indent=2)
            except Exception as e:
                print(f"[!] 写入 oauth_creds.json 错误: {e}")

        if os.path.exists(tgt_accs):
            shutil.copy2(tgt_accs, self.accounts_file)
        else:
            try:
                new_acc = {"active": target_email, "old": [cur_email] if cur_email and cur_email != target_email else []}
                with open(self.accounts_file, "w", encoding="utf-8") as f:
                    json.dump(new_acc, f, indent=2)
            except Exception as e:
                print(f"[!] 写入 google_accounts.json 错误: {e}")

        self.pool.set_active_account(target.id)
        print(f"[OK] Antigravity 活跃账号已切换为: {target_email}！")
        return True

    switch_account = switch_to

