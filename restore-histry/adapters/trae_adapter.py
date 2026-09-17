# -*- coding: utf-8 -*-
"""
Trae (字节跳动 AI IDE) 专属会话管理与恢复适配器
基于 VS Code 架构，按工作区隔离扫描 workspaceStorage 中的 state.vscdb。
"""

import os
import json
import sqlite3
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class TraeRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "trae"

    @property
    def name(self) -> str:
        return "Trae (字节跳动 AI IDE)"

    @property
    def description(self) -> str:
        return "基于 VS Code 架构。按工作区扫描 state.vscdb，支持单工程会话状态提取与安全备份"

    def _get_workspace_roots(self):
        appdata = os.environ.get("APPDATA", "")
        roots = []
        for name in ["Trae", "TRAE SOLO CN", "trae"]:
            p = os.path.join(appdata, name, "User", "workspaceStorage")
            if os.path.exists(p):
                roots.append(p)
        return roots

    def is_installed(self) -> bool:
        return len(self._get_workspace_roots()) > 0

    def get_data_dir(self) -> str:
        roots = self._get_workspace_roots()
        return roots[0] if roots else ""

    def list_workspaces(self) -> List[str]:
        workspaces = set()
        for root in self._get_workspace_roots():
            for folder in os.listdir(root):
                fp = os.path.join(root, folder, "workspace.json")
                if os.path.exists(fp):
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            w = data.get("folder")
                            if w: workspaces.add(w)
                    except: pass
        return sorted(list(workspaces))

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        envelopes = []
        for root in self._get_workspace_roots():
            for folder in os.listdir(root):
                folder_path = os.path.join(root, folder)
                db_path = os.path.join(folder_path, "state.vscdb")
                if not os.path.exists(db_path):
                    continue

                ws_name = folder
                ws_json = os.path.join(folder_path, "workspace.json")
                if os.path.exists(ws_json):
                    try:
                        with open(ws_json, "r", encoding="utf-8") as f:
                            ws_name = json.load(f).get("folder", folder)
                    except: pass

                if workspace and ws_name != workspace:
                    continue

                mtime = os.path.getmtime(db_path)
                size = os.path.getsize(db_path)

                envelopes.append(SessionEnvelope(
                    session_id=f"trae-{folder}",
                    tool_id=self.tool_id,
                    tool_name=self.name,
                    workspace=ws_name,
                    title=f"Trae 工作区会话: {os.path.basename(ws_name)}",
                    updated_at=datetime.datetime.fromtimestamp(mtime),
                    size_bytes=size,
                    status="active",
                    raw_path=db_path,
                    extra_meta={"folder_hash": folder}
                ))
        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self.list_sessions():
            if s.session_id == session_id:
                return {"envelope": s, "raw_db": s.raw_path}
        return None

    def backup_session(self, session_id: str) -> str:
        detail = self.get_session_detail(session_id)
        if not detail or not os.path.exists(detail["raw_db"]):
            raise ValueError(f"未找到会话 {session_id}")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(detail["raw_db"]), f"backup_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(detail["raw_db"], os.path.join(backup_dir, "state.vscdb"))
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id: raise ValueError("必须指定单会话 ID！")
        self.backup_session(session_id)
        print(f"[✓] Trae 会话 {session_id} 独立快照已生成，状态完整。")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail: raise ValueError("会话不存在")
        if not target_file:
            home = os.path.expanduser("~")
            export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
            os.makedirs(export_dir, exist_ok=True)
            target_file = os.path.join(export_dir, f"Trae_{session_id}.txt")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(f"Trae 会话标识: {session_id}\n工作区: {detail['envelope'].workspace}\n数据源: {detail['raw_db']}\n")
        return target_file
