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
        self._sync_current_live_account()

    def _get_storage_files(self) -> List[str]:
        files = []
        for d in [self.trae_dir, self.trae_cn_dir]:
            p = os.path.join(d, "globalStorage", "storage.json")
            if os.path.exists(p):
                files.append(p)
        return files

    def _sync_current_live_account(self):
        for sf in self._get_storage_files():
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    usertag = data.get("iCubeAuthInfo://usertag")
                    cloudide = data.get("iCubeAuthInfo://icube.cloudide")
                    if usertag:
                        self.pool.add_or_update_account(AccountRecord(
                            id="trae-live-account",
                            provider="trae",
                            email="trae_current_account",
                            nickname="Trae 本地活跃凭证",
                            token=usertag[:24] + "...",
                            is_active=True,
                            updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            extra={"usertag": usertag, "cloudide": cloudide}
                        ))
                        break
            except Exception:
                pass

    def list_accounts(self) -> List[AccountRecord]:
        self._sync_current_live_account()
        return self.pool.load_accounts()

    def add_account(self, name: str, email: str, token: str = "", extra: dict = None) -> AccountRecord:
        rec = AccountRecord(
            id=f"trae-{email}",
            provider="trae",
            email=email,
            token=token,
            nickname=name,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            extra=extra or {}
        )
        self.pool.add_or_update_account(rec)
        return rec

    def switch_to(self, target_id_or_email: str) -> bool:
        accounts = self.list_accounts()
        target = None
        for a in accounts:
            if a.id == target_id_or_email or a.email.lower() == target_id_or_email.lower():
                target = a
                break
        if not target:
            print(f"[!] 未在 Trae 账号池中找到: {target_id_or_email}")
            return False

        print(f"[*] 正在为 Trae 切换至账号: {target.email} ...")

        # 1. 备份当前 Trae storage.json
        profiles_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trae_profiles")
        os.makedirs(profiles_base, exist_ok=True)

        for sf in self._get_storage_files():
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                cur_tag = s_data.get("iCubeAuthInfo://usertag", "")
                if cur_tag:
                    bak_f = os.path.join(profiles_base, "current_backup_storage.json")
                    shutil.copy2(sf, bak_f)

                # 2. 如果目标账号有专属认证 token/usertag，写回 storage.json
                if target.extra and "usertag" in target.extra:
                    s_data["iCubeAuthInfo://usertag"] = target.extra["usertag"]
                    if target.extra.get("cloudide"):
                        s_data["iCubeAuthInfo://icube.cloudide"] = target.extra["cloudide"]
                    with open(sf, "w", encoding="utf-8") as f:
                        json.dump(s_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[!] 写入 Trae 凭证错误 {sf}: {e}")

        self.pool.set_active_account(target.id)
        print(f"[OK] Trae 目标账号 {target.email} 凭证已就绪并同步。")
        return True

    switch_account = switch_to
