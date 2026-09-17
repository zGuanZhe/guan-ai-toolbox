# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Base Account Pool Manager
参考 Antigravity-Manager 的账号池设计，管理多工具账号存储、活性、配额与一键切换。
"""

import os
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class AccountRecord:
    id: str                       # 唯一标识符
    provider: str                 # 厂商标识 (workbuddy, trae, antigravity, qoder, openai)
    email: str                    # 登录邮箱 / 账号
    token: str = ""               # 授权 Token / Session 凭证
    uid: str = ""                 # 平台内部用户 ID
    nickname: str = ""            # 昵称
    edition: str = "free"         # 版本/等级 (free, pro, team)
    is_active: bool = False       # 当前客户端是否正处于该账号登录态
    fingerprint_id: str = ""      # 独立环境指纹 ID
    profile_dir: str = ""         # 独立 Profile 目录
    proxy: str = ""               # 隔离网络代理
    notes: str = ""               # 备注说明
    created_at: str = ""          # 创建/录入时间
    updated_at: str = ""          # 最后活跃时间
    extra: Dict[str, Any] = None  # 额外配置 (例如 raw JSON 快照)

class BaseAccountPool:
    def __init__(self, provider: str, storage_file: Optional[str] = None):
        self.provider = provider.lower()
        if not storage_file:
            home = os.path.expanduser("~")
            base_dir = os.path.join(r"D:\Test\Sub2\观的ai工具箱", "register", "config", "account_pools")
            os.makedirs(base_dir, exist_ok=True)
            self.storage_file = os.path.join(base_dir, f"{self.provider}_pool.json")
        else:
            self.storage_file = storage_file

    def load_accounts(self) -> List[AccountRecord]:
        if not os.path.exists(self.storage_file):
            return []
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                valid_keys = AccountRecord.__dataclass_fields__.keys()
                result = []
                for item in data:
                    filtered = {k: v for k, v in item.items() if k in valid_keys}
                    result.append(AccountRecord(**filtered))
                return result
        except Exception as e:
            print(f"[!] Error loading {self.storage_file}: {e}")
            return []

    def save_accounts(self, accounts: List[AccountRecord]):
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in accounts], f, ensure_ascii=False, indent=2)

    def add_or_update_account(self, record: AccountRecord):
        accounts = self.load_accounts()
        for idx, a in enumerate(accounts):
            if a.email.lower() == record.email.lower() or (a.uid and a.uid == record.uid):
                accounts[idx] = record
                self.save_accounts(accounts)
                return
        accounts.append(record)
        self.save_accounts(accounts)

    def set_active_account(self, account_id_or_email: str) -> Optional[AccountRecord]:
        accounts = self.load_accounts()
        target = None
        for a in accounts:
            if a.id == account_id_or_email or a.email.lower() == account_id_or_email.lower():
                a.is_active = True
                target = a
            else:
                a.is_active = False
        if target:
            self.save_accounts(accounts)
        return target
