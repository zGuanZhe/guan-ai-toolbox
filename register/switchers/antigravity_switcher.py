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
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    accs = json.load(f)
                    if isinstance(accs, list) and accs:
                        for acc in accs:
                            email = acc.get("email") or "current_google"
                            self.pool.add_or_update_account(AccountRecord(
                                id=f"gemini-{email}",
                                provider="antigravity",
                                email=email,
                                is_active=True,
                                updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ))
            except: pass

    def list_accounts(self) -> List[AccountRecord]:
        return self.pool.load_accounts()

    def switch_to(self, email: str) -> bool:
        print(f"[*] 正在轮换 Antigravity 账号至: {email} ...")
        self.pool.set_active_account(f"gemini-{email}")
        print(f"[✓] Antigravity 活跃账号已切换为: {email}！")
        return True
