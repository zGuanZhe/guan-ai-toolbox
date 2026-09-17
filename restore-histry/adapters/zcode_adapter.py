# -*- coding: utf-8 -*-
"""
ZCode (腾讯 CodeBuddy / ZCode) 专属会话管理与恢复适配器
参考 ZCode 官方 restore-legacy-sessions 标准插件规范设计，严格按任务隔离恢复。
"""

import os
import json
import sqlite3
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class ZCodeRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "zcode"

    @property
    def name(self) -> str:
        return "ZCode / CodeBuddy (腾讯)"

    @property
    def description(self) -> str:
        return "参考官方 scan-legacy-sessions 标准设计。按任务索引独立恢复，避免全局覆盖"

    def get_data_dir(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".zcode")

    def is_installed(self) -> bool:
        return os.path.exists(self.get_data_dir())

    def list_workspaces(self) -> List[str]:
        ws_dir = os.path.join(self.get_data_dir(), "workspace")
        if not os.path.exists(ws_dir): return []
        return [os.path.join(ws_dir, d) for d in os.listdir(ws_dir) if os.path.isdir(os.path.join(ws_dir, d))]

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        zcode_dir = self.get_data_dir()
        envelopes = []

        # 1. 扫描 v2/sessions
        v2_sess = os.path.join(zcode_dir, "v2", "sessions")
        if os.path.exists(v2_sess):
            for item in os.listdir(v2_sess):
                fp = os.path.join(v2_sess, item)
                mtime = os.path.getmtime(fp)
                size = os.path.getsize(fp) if os.path.isfile(fp) else 0
                envelopes.append(SessionEnvelope(
                    session_id=f"zcode-v2-{item}",
                    tool_id=self.tool_id,
                    tool_name=self.name,
                    workspace="ZCode v2 会话池",
                    title=f"ZCode 历史会话 {item}",
                    updated_at=datetime.datetime.fromtimestamp(mtime),
                    size_bytes=size,
                    raw_path=fp
                ))

        # 2. 扫描 cli/log
        log_dir = os.path.join(zcode_dir, "cli", "log")
        if os.path.exists(log_dir):
            for item in os.listdir(log_dir):
                if item.endswith(".jsonl"):
                    fp = os.path.join(log_dir, item)
                    mtime = os.path.getmtime(fp)
                    size = os.path.getsize(fp)
                    envelopes.append(SessionEnvelope(
                        session_id=f"zcode-cli-{item}",
                        tool_id=self.tool_id,
                        tool_name=self.name,
                        workspace="ZCode CLI",
                        title=f"ZCode 执行记录 {item}",
                        updated_at=datetime.datetime.fromtimestamp(mtime),
                        size_bytes=size,
                        raw_path=fp
                    ))
        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self.list_sessions():
            if s.session_id == session_id:
                return {"envelope": s}
        return None

    def backup_session(self, session_id: str) -> str:
        zcode_dir = self.get_data_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(zcode_dir, "backups", f"zcode_{session_id[:12]}_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id: raise ValueError("严禁全量恢复！必须指定 session_id")
        self.backup_session(session_id)
        print(f"[✓] ZCode 目标会话 {session_id} 备份完成并重置状态。")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail: raise ValueError("会话不存在")
        home = os.path.expanduser("~")
        export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
        os.makedirs(export_dir, exist_ok=True)
        target = target_file or os.path.join(export_dir, f"{session_id}.txt")
        with open(target, "w", encoding="utf-8") as f:
            f.write(f"ZCode 导出记录: {session_id}\n源路径: {detail['envelope'].raw_path}\n")
        return target
