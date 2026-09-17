# -*- coding: utf-8 -*-
"""
WorkBuddy 多账号管理与一键切换器
参考 Antigravity-Manager 的 Token/Account 管理模式，
支持在多个 WorkBuddy 账号（如腾讯云/个人多邮箱账号）间一键秒级切换登录态。
"""

import os
import json
import time
import shutil
import datetime
import subprocess
from typing import List, Optional
from core.base_account_pool import BaseAccountPool, AccountRecord

class WorkBuddyAccountSwitcher:
    def __init__(self):
        self.pool = BaseAccountPool("workbuddy")
        self.home = os.path.expanduser("~")
        self.wb_dir = os.path.join(self.home, ".workbuddy-ai")
        self.snapshot_file = os.path.join(self.wb_dir, "storage", "skeleton", "account-snapshot.json")
        self._sync_current_live_account()

    def _sync_current_live_account(self):
        """将当前活跃客户端的账号自动同步进账号池"""
        if not os.path.exists(self.snapshot_file):
            return
        try:
            with open(self.snapshot_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                primary = data.get("primary", {})
                uid = primary.get("uid")
                if uid:
                    email = primary.get("nickname") or uid
                    rec = AccountRecord(
                        id=uid,
                        provider="workbuddy",
                        email=email,
                        uid=uid,
                        nickname=primary.get("nickname", ""),
                        edition=primary.get("editionType", "free"),
                        is_active=True,
                        updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        extra=data
                    )
                    self.pool.add_or_update_account(rec)
        except Exception:
            pass

    def list_accounts(self) -> List[AccountRecord]:
        return self.pool.load_accounts()

    def add_account(self, uid: str, email: str, edition: str = "free", extra: dict = None) -> AccountRecord:
        rec = AccountRecord(
            id=uid,
            provider="workbuddy",
            email=email,
            uid=uid,
            nickname=email,
            edition=edition,
            is_active=False,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            extra=extra or {}
        )
        self.pool.add_or_update_account(rec)
        return rec

    def switch_to(self, target_account_id_or_email: str, restart_app: bool = False) -> bool:
        accounts = self.pool.load_accounts()
        target = None
        for a in accounts:
            if a.id == target_account_id_or_email or a.email.lower() == target_account_id_or_email.lower():
                target = a
                break

        if not target:
            print(f"[!] 账号池中未找到账号: {target_account_id_or_email}")
            return False

        print(f"[*] 准备切换至 WorkBuddy 账号: {target.email} (UID: {target.uid}) ...")

        # 1. 备份当前 snapshot
        if os.path.exists(self.snapshot_file):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            bak_path = self.snapshot_file + f".bak_{ts}"
            shutil.copy2(self.snapshot_file, bak_path)

        # 2. 构造新的 snapshot 数据
        if target.extra and "primary" in target.extra:
            new_data = target.extra
            new_data["primary"]["savedAt"] = int(time.time() * 1000)
        else:
            new_data = {
                "primary": {
                    "version": 1,
                    "uid": target.uid,
                    "nickname": target.email,
                    "type": "personal",
                    "editionType": target.edition,
                    "isPro": (target.edition.lower() == "pro"),
                    "isAdmin": False,
                    "oneidAccountId": "",
                    "savedAt": int(time.time() * 1000)
                }
            }

        os.makedirs(os.path.dirname(self.snapshot_file), exist_ok=True)
        with open(self.snapshot_file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        # 3. 标记激活状态
        self.pool.set_active_account(target.id)
        print(f"[✓] 登录凭证已置换为: {target.email}！")

        # 4. 可选重启客户端以使界面重载
        if restart_app:
            self._restart_workbuddy()
        else:
            print("💡 提示: 请在 WorkBuddy 窗口按 Ctrl+R 刷新，或重启客户端即可加载该账号！")
        return True

    def _restart_workbuddy(self):
        try:
            print("[*] 正在平滑重启 WorkBuddy 客户端...")
            subprocess.run("taskkill /F /IM WorkBuddyAI.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
            candidate_exes = [
                r"D:\yingyong\新建文件夹\WorkBuddyAI\WorkBuddyAI.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\WorkBuddyAI\WorkBuddyAI.exe")
            ]
            for exe in candidate_exes:
                if os.path.exists(exe):
                    subprocess.Popen([exe], shell=False)
                    print("[✓] WorkBuddy 客户端已启动，已进入新账号登录态！")
                    return
        except Exception as e:
            print(f"[!] 重启客户端提示: {e}")
