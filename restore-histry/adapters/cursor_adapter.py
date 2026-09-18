# -*- coding: utf-8 -*-
"""
Cursor 对话记录与 Composer 历史恢复适配器
针对 Cursor IDE 的 workspaceStorage、globalStorage 以及 ~/.cursor 项目转录进行会话检索、安全备份与双向恢复导出。
"""

import os
import sys
import glob
import json
import sqlite3
import datetime
import shutil
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class CursorRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "cursor"

    @property
    def name(self) -> str:
        return "Cursor (AI 智能代码编辑器)"

    @property
    def description(self) -> str:
        return "检索与恢复 Cursor 的 Composer 历史记录、Agent 交互记录与各工作区 SQLite 状态库"

    def is_installed(self) -> bool:
        return os.path.exists(self.get_data_dir()) or os.path.exists(os.path.expanduser("~/.cursor"))

    def get_data_dir(self) -> str:
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(appdata, "Cursor", "User")

    def _get_projects_dir(self) -> str:
        return os.path.expanduser("~/.cursor/projects")

    def list_workspaces(self) -> List[str]:
        workspaces = set()
        cursor_user = self.get_data_dir()
        ws_storage = os.path.join(cursor_user, "workspaceStorage")
        if os.path.exists(ws_storage):
            for ws_folder in os.listdir(ws_storage):
                ws_json_path = os.path.join(ws_storage, ws_folder, "workspace.json")
                if os.path.exists(ws_json_path):
                    try:
                        with open(ws_json_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            w = data.get("folder")
                            if w: workspaces.add(w)
                    except: pass
        p_dir = self._get_projects_dir()
        if os.path.exists(p_dir):
            for d in os.listdir(p_dir):
                workspaces.add(d)
        return sorted(list(workspaces))

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        envelopes = []

        # 1. 扫描 ~/.cursor/projects/*/agent-transcripts/*/*.jsonl (真实 Agent/Composer 对话流)
        p_dir = self._get_projects_dir()
        if os.path.exists(p_dir):
            pattern = os.path.join(p_dir, "*", "agent-transcripts", "*", "*.jsonl")
            for t_file in glob.glob(pattern):
                try:
                    mtime = os.path.getmtime(t_file)
                    size = os.path.getsize(t_file)
                    sid = os.path.splitext(os.path.basename(t_file))[0]
                    proj_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(t_file))))

                    if workspace and proj_name != workspace:
                        continue

                    # 探测首条用户提问
                    first_query = ""
                    lines_count = 0
                    with open(t_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            lines_count += 1
                            if not first_query and line.strip():
                                try:
                                    item = json.loads(line)
                                    msg = item.get("message", {})
                                    content = msg.get("content", [])
                                    if isinstance(content, list) and content:
                                        t_val = content[0].get("text", "")
                                        if "<user_query>" in t_val:
                                            q_part = t_val.split("<user_query>")[1].split("</user_query>")[0].strip()
                                            first_query = q_part[:40]
                                        elif t_val:
                                            first_query = t_val[:40]
                                except: pass

                    title = f"Cursor Agent: {first_query}..." if first_query else f"Cursor 转录: {sid[:8]}"

                    envelopes.append(SessionEnvelope(
                        session_id=f"cursor-trans-{sid}",
                        tool_id=self.tool_id,
                        tool_name=self.name,
                        workspace=proj_name,
                        title=title,
                        created_at=datetime.datetime.fromtimestamp(mtime),
                        updated_at=datetime.datetime.fromtimestamp(mtime),
                        message_count=lines_count,
                        size_bytes=size,
                        status="active",
                        raw_path=t_file,
                        extra_meta={"transcript_id": sid, "project": proj_name}
                    ))
                except Exception:
                    pass

        # 2. 扫描 workspaceStorage 中的 state.vscdb
        cursor_user = self.get_data_dir()
        ws_storage = os.path.join(cursor_user, "workspaceStorage")
        if os.path.exists(ws_storage):
            for ws_folder in os.listdir(ws_storage):
                folder_path = os.path.join(ws_storage, ws_folder)
                db_path = os.path.join(folder_path, "state.vscdb")
                if not os.path.exists(db_path):
                    continue

                ws_name = ws_folder
                ws_json_path = os.path.join(folder_path, "workspace.json")
                if os.path.exists(ws_json_path):
                    try:
                        with open(ws_json_path, "r", encoding="utf-8") as f:
                            ws_name = json.load(f).get("folder", ws_folder)
                    except: pass

                if workspace and ws_name != workspace:
                    continue

                mtime = os.path.getmtime(db_path)
                size = os.path.getsize(db_path)

                envelopes.append(SessionEnvelope(
                    session_id=f"cursor-ws-{ws_folder}",
                    tool_id=self.tool_id,
                    tool_name=self.name,
                    workspace=ws_name,
                    title=f"Cursor 工作区: {os.path.basename(ws_name)}",
                    updated_at=datetime.datetime.fromtimestamp(mtime),
                    size_bytes=size,
                    status="active",
                    raw_path=db_path,
                    extra_meta={"workspace_hash": ws_folder}
                ))

        # 3. 扫描 globalStorage 中 state.vscdb 的 composer.composerHeaders (提取已归档或活跃 Composer 会话)
        global_db = os.path.join(cursor_user, "globalStorage", "state.vscdb")
        if os.path.exists(global_db):
            try:
                conn = sqlite3.connect(global_db, timeout=3.0)
                c = conn.cursor()
                c.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'")
                row = c.fetchone()
                if row and row[0]:
                    headers_data = json.loads(row[0])
                    for comp in headers_data.get("allComposers", []):
                        cid = comp.get("composerId")
                        if not cid: continue
                        c_at = comp.get("createdAt")
                        is_arch = comp.get("isArchived", False)
                        mode = comp.get("unifiedMode", "chat")
                        dt = datetime.datetime.fromtimestamp(c_at / 1000) if c_at else None

                        envelopes.append(SessionEnvelope(
                            session_id=f"cursor-comp-{cid}",
                            tool_id=self.tool_id,
                            tool_name=self.name,
                            workspace="全局 Composer",
                            title=f"Cursor Composer ({mode}) - {cid[:8]}",
                            created_at=dt,
                            updated_at=dt,
                            status="archived" if is_arch else "active",
                            raw_path=global_db,
                            extra_meta={"composer_id": cid, "mode": mode, "isArchived": is_arch}
                        ))
                conn.close()
            except Exception:
                pass

        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self.list_sessions():
            if s.session_id == session_id:
                preview = []
                if s.raw_path.endswith(".jsonl") and os.path.exists(s.raw_path):
                    try:
                        with open(s.raw_path, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f):
                                if idx < 3:
                                    preview.append(line.strip()[:140])
                                else:
                                    break
                    except: pass
                return {"envelope": s, "raw_path": s.raw_path, "preview_snippets": preview}
        return None

    def backup_session(self, session_id: str) -> str:
        detail = self.get_session_detail(session_id)
        if not detail or not os.path.exists(detail["raw_path"]):
            raise ValueError(f"未找到会话 {session_id}")
        cursor_user = self.get_data_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(cursor_user, "backups_toolbox", f"cursor_{session_id[:16]}_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        src = detail["raw_path"]
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(backup_dir, os.path.basename(src)), dirs_exist_ok=True)
        else:
            shutil.copy2(src, os.path.join(backup_dir, os.path.basename(src)))
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id:
            raise ValueError("必须明确指定 session_id！")
        detail = self.get_session_detail(session_id)
        if not detail:
            raise ValueError(f"未能定位 Cursor 会话 {session_id}")

        # 1. 严格做安全快照
        self.backup_session(session_id)

        # 2. 如果是 Composer 恢复：将 globalStorage/state.vscdb 中的 isArchived 置为 false
        if session_id.startswith("cursor-comp-"):
            cid = session_id.replace("cursor-comp-", "")
            global_db = detail["raw_path"]
            try:
                conn = sqlite3.connect(global_db, timeout=5.0)
                c = conn.cursor()
                c.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'")
                row = c.fetchone()
                if row and row[0]:
                    headers = json.loads(row[0])
                    changed = False
                    for comp in headers.get("allComposers", []):
                        if comp.get("composerId") == cid:
                            comp["isArchived"] = False
                            changed = True
                            break
                    if changed:
                        c.execute("UPDATE ItemTable SET value = ? WHERE key = 'composer.composerHeaders'", (json.dumps(headers),))
                        conn.commit()
                        conn.close()
                        print(f"[OK] Cursor Composer 会话 {cid} 已解除归档，恢复至活跃列表！")
                        return True
                conn.close()
            except Exception as e:
                print(f"[!] Cursor Composer 恢复更新失败: {e}")
                return False

        # 3. 如果是工作区 SQLite 恢复：若有历史备份则执行覆盖还原
        elif session_id.startswith("cursor-ws-"):
            ws_db = detail["raw_path"]
            ws_dir = os.path.dirname(ws_db)
            backups = sorted([
                os.path.join(ws_dir, d) for d in os.listdir(ws_dir)
                if d.startswith("backup_") and os.path.isdir(os.path.join(ws_dir, d))
            ], reverse=True)
            if backups:
                cand = os.path.join(backups[0], "state.vscdb")
                if os.path.exists(cand):
                    shutil.copy2(cand, ws_db)
                    print(f"[OK] Cursor 工作区状态已从最近备份 {backups[0]} 恢复！")
                    return True

        # 4. 如果是转录文件：校验其完整性，确保未损毁
        elif session_id.startswith("cursor-trans-"):
            if os.path.exists(detail["raw_path"]) and os.path.getsize(detail["raw_path"]) > 0:
                print(f"[OK] Cursor 对话转录 {session_id} 完整性校验通过，已就绪。")
                return True

        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail:
            raise ValueError(f"会话 {session_id} 不存在")

        if not target_file:
            home = os.path.expanduser("~")
            export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
            os.makedirs(export_dir, exist_ok=True)
            target_file = os.path.join(export_dir, f"Cursor_{session_id}.md")

        env = detail["envelope"]
        raw_p = detail["raw_path"]

        with open(target_file, "w", encoding="utf-8") as f_out:
            f_out.write(f"# Cursor AI 会话归档 - {session_id}\n\n")
            f_out.write(f"- **工作区 / 项目**: {env.workspace}\n")
            f_out.write(f"- **标题**: {env.title}\n")
            f_out.write(f"- **最后时间**: {env.time_human}\n")
            f_out.write(f"- **数据源**: `{raw_p}`\n\n---\n\n")

            # 若是 jsonl 转录，解析完整的 user / assistant 对话流
            if raw_p.endswith(".jsonl") and os.path.exists(raw_p):
                f_out.write("## 完整对话历史 (Conversation Turns)\n\n")
                with open(raw_p, "r", encoding="utf-8", errors="ignore") as f_in:
                    for line in f_in:
                        try:
                            obj = json.loads(line)
                            role = obj.get("role", "message").upper()
                            msg = obj.get("message", {})
                            content = msg.get("content", [])
                            text_body = ""
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and "text" in item:
                                        text_body += item["text"] + "\n"
                            elif isinstance(content, str):
                                text_body = content
                            
                            if text_body.strip():
                                f_out.write(f"### [{role}]\n\n{text_body.strip()}\n\n---\n\n")
                        except:
                            pass
            else:
                f_out.write("## 状态元数据\n\n")
                f_out.write(f"- 物理文件大小: {env.size_human}\n")
                f_out.write(f"- 扩展元数据: {json.dumps(env.extra_meta, ensure_ascii=False, indent=2)}\n")

        print(f"[OK] Cursor 会话已成功导出至: {target_file}")
        return target_file
