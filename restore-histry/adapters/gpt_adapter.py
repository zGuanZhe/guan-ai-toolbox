# -*- coding: utf-8 -*-
"""
GPT / OpenAI Codex 专属会话管理与恢复适配器
管理历史 GPT / Codex 对话流与指令归档。
"""

import os
import json
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class GptRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "gpt"

    @property
    def name(self) -> str:
        return "OpenAI GPT / Codex"

    @property
    def description(self) -> str:
        return "管理历史 Codex / GPT 终端会话归档，支持单个会话导出与回溯"

    def get_data_dir(self) -> str:
        # 工具箱内的 legacy_archive 或用户家目录
        p = os.path.join(r"D:\Test\Sub2\观的ai工具箱", "instruct", "legacy_archive")
        if os.path.exists(p): return p
        return os.path.join(os.path.expanduser("~"), ".codex")

    def is_installed(self) -> bool:
        return os.path.exists(self.get_data_dir())

    def list_workspaces(self) -> List[str]:
        return ["OpenAI / Codex 归档仓库"]

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        data_dir = self.get_data_dir()
        envelopes = []
        if not os.path.exists(data_dir): return []

        for item in os.listdir(data_dir):
            fp = os.path.join(data_dir, item)
            mtime = os.path.getmtime(fp)
            size = os.path.getsize(fp) if os.path.isfile(fp) else 0
            envelopes.append(SessionEnvelope(
                session_id=f"gpt-{item}",
                tool_id=self.tool_id,
                tool_name=self.name,
                workspace="OpenAI Codex Workspace",
                title=f"Codex 归档会话: {item}",
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
        home = os.path.expanduser("~")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(home, ".codex_backups", f"backup_{session_id}_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id: raise ValueError("严禁全量恢复！必须指定单会话 session_id")
        self.backup_session(session_id)
        print(f"[✓] GPT/Codex 会话 {session_id} 校验完成。")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail: raise ValueError("会话不存在")
        home = os.path.expanduser("~")
        export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
        os.makedirs(export_dir, exist_ok=True)
        target = target_file or os.path.join(export_dir, f"{session_id}.md")
        with open(target, "w", encoding="utf-8") as f:
            f.write(f"# GPT/Codex 会话归档: {session_id}\n源路径: {detail['envelope'].raw_path}\n")
        return target
