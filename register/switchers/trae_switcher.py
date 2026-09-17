# -*- coding: utf-8 -*-
"""
Trae 多账号管理与一键切换器
参考 Antigravity-Manager，管理 Trae 的登录身份与配置文件。
"""

import os
import json
import shutil
import datetime
from typing import List, Optional
from core.base_account_pool import BaseAccountPool, AccountRecord

class TraeAccountSwitcher:
    def __init__(self):
        self.pool = BaseAccountPool("trae")
        self.appdata = os.environ.get("APPDATA", "")
        self.trae_dir = os.path.join(self.appdata, "Trae", "User")
        self.trae_cn_dir = os.path.join(self.appdata, "TRAE SOLO CN", "User")

    def list_accounts(self) -> List[AccountRecord]:
        return self.pool.load_accounts()

    def add_account(self, name: str, email: str, token: str = "") -> AccountRecord:
        rec = AccountRecord(
            id=f"trae-{email}",
            provider="trae",
            email=email,
            token=token,
            nickname=name,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.pool.add_or_update_account(rec)
        return rec

    def switch_to(self, target_id_or_email: str) -> bool:
        accounts = self.pool.load_accounts()
        target = None
        for a in accounts:
            if a.id == target_id_or_email or a.email.lower() == target_id_or_email.lower():
                target = a
                break
        if not target:
            print(f"[!] 未在 Trae 账号池中找到: {target_id_or_email}")
            return False

        print(f"[*] 正在为 Trae 切换至账号: {target.email} ...")
        self.pool.set_active_account(target.id)
        print(f"[✓] Trae 目标账号 {target.email} 凭证已就绪。")
        return True
