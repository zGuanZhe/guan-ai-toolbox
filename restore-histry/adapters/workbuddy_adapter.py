# -*- coding: utf-8 -*-
"""
WorkBuddy AI 专属会话管理与恢复适配器
严格禁止全量恢复，仅支持按工作区过滤及精准单会话恢复/导出。
"""

import os
import glob
import json
import shutil
import sqlite3
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class WorkBuddyRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "workbuddy"

    @property
    def name(self) -> str:
        return "WorkBuddy AI (腾讯)"

    @property
    def description(self) -> str:
        return "基于 SQLite+WAL 及 JSONL 消息流。解决切换账号隐藏、软删除误删解除，支持精准单会话恢复"

    def _get_candidates(self):
        home = os.path.expanduser("~")
        return [os.path.join(home, ".workbuddy-ai"), os.path.join(home, ".workbuddy")]

    def is_installed(self) -> bool:
        return any(os.path.exists(d) for d in self._get_candidates())

    def get_data_dir(self) -> str:
        for d in self._get_candidates():
            if os.path.exists(d):
                return d
        return self._get_candidates()[0]

    def _get_current_uid(self) -> str:
        snap_path = os.path.join(self.get_data_dir(), "storage", "skeleton", "account-snapshot.json")
        if os.path.exists(snap_path):
            try:
                with open(snap_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("primary", {}).get("uid", "")
            except Exception:
                pass
        return ""

    def list_workspaces(self) -> List[str]:
        db_path = os.path.join(self.get_data_dir(), "workbuddy.db")
        if not os.path.exists(db_path):
            return []
        try:
            conn = sqlite3.connect(f"file:{db_path.replace(os.sep, '/')}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT cwd FROM sessions WHERE cwd IS NOT NULL AND cwd != ''")
            cwds = [r[0] for r in cursor.fetchall()]
            conn.close()
            return cwds
        except Exception:
            return []

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        wb_dir = self.get_data_dir()
        db_path = os.path.join(wb_dir, "workbuddy.db")
        if not os.path.exists(db_path):
            return []

        cur_uid = self._get_current_uid()
        conn = sqlite3.connect(f"file:{db_path.replace(os.sep, '/')}?mode=ro", uri=True)
        cursor = conn.cursor()

        query = "SELECT id, user_id, title, status, created_at, updated_at, deleted_at, cwd FROM sessions"
        params = []
        if workspace:
            query += " WHERE cwd = ?"
            params.append(workspace)
        query += " ORDER BY updated_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        proj_base = os.path.join(wb_dir, "projects")
        envelopes = []
        for r in rows:
            sid, uid, title, status, c_at, u_at, d_at, cwd = r
            jsonl_matches = glob.glob(os.path.join(proj_base, "*", f"{sid}.jsonl"))
            raw_path = jsonl_matches[0] if jsonl_matches else ""
            size = os.path.getsize(raw_path) if raw_path else 0

            # 统计消息行数
            lines = 0
            if raw_path and size < 100 * 1024 * 1024:
                try:
                    with open(raw_path, "rb") as f:
                        for _ in f: lines += 1
                except: pass

            is_cur = (uid == cur_uid)
            is_del = (d_at is not None)
            stat = "active"
            if not is_cur and is_del:
                stat = "hidden_and_deleted"
            elif not is_cur:
                stat = "hidden_cross_account"
            elif is_del:
                stat = "deleted"

            envelopes.append(SessionEnvelope(
                session_id=sid,
                tool_id=self.tool_id,
                tool_name=self.name,
                workspace=cwd or "未知工作区",
                title=title or "无标题会话",
                created_at=datetime.datetime.fromtimestamp(c_at / 1000) if c_at else None,
                updated_at=datetime.datetime.fromtimestamp(u_at / 1000) if u_at else None,
                message_count=lines,
                size_bytes=size,
                status=stat,
                raw_path=raw_path,
                extra_meta={"user_id": uid, "current_user_id": cur_uid, "deleted_at": d_at}
            ))
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self.list_sessions():
            if s.session_id == session_id:
                # 预览前几行与最后几行
                preview = []
                if s.raw_path and os.path.exists(s.raw_path):
                    try:
                        with open(s.raw_path, "r", encoding="utf-8", errors="ignore") as f:
                            all_lines = f.readlines()
                            preview = [l.strip()[:180] for l in (all_lines[:2] + all_lines[-2:])]
                    except: pass
                return {
                    "envelope": s,
                    "preview_snippets": preview,
                    "raw_path": s.raw_path
                }
        return None

    def backup_session(self, session_id: str) -> str:
        wb_dir = self.get_data_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(wb_dir, "backups", f"single_session_{session_id[:8]}_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        # 备份数据库文件
        for fn in ["workbuddy.db", "workbuddy.db-wal", "workbuddy.db-shm"]:
            fp = os.path.join(wb_dir, fn)
            if os.path.exists(fp):
                shutil.copy2(fp, os.path.join(backup_dir, fn))
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id:
            raise ValueError("[安全拦截] restore_session 必须明确指定 session_id，严禁批量/全量恢复！")

        wb_dir = self.get_data_dir()
        db_path = os.path.join(wb_dir, "workbuddy.db")
        if not os.path.exists(db_path):
            return False

        # 先做专属快照
        self.backup_session(session_id)

        target_uid = (options or {}).get("target_uid") or self._get_current_uid()
        if not target_uid:
            print("[!] 未能获取当前账号 UID，无法挂载。")
            return False

        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        try:
            # 严格只 UPDATE 这一条记录
            cursor.execute("""
                UPDATE sessions 
                SET user_id = ?, deleted_at = NULL, updated_at = ?
                WHERE id = ?
            """, (target_uid, int(datetime.datetime.now().timestamp() * 1000), session_id))
            affected = cursor.rowcount
            conn.commit()
            cursor.execute("PRAGMA wal_checkpoint(FULL)")
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"[!] WorkBuddy 单会话恢复失败: {e}")
            conn.rollback()
            conn.close()
            return False

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail or not detail.get("raw_path"):
            raise ValueError(f"未找到会话 {session_id} 的物理文件")
        
        raw_path = detail["raw_path"]
        if not target_file:
            home = os.path.expanduser("~")
            export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
            os.makedirs(export_dir, exist_ok=True)
            target_file = os.path.join(export_dir, f"WorkBuddy_Session_{session_id[:8]}.md")

        with open(raw_path, "r", encoding="utf-8", errors="ignore") as f_in,              open(target_file, "w", encoding="utf-8") as f_out:
            f_out.write(f"# WorkBuddy 会话归档 - {session_id}\n\n")
            f_out.write(f"- **工作区**: {detail['envelope'].workspace}\n")
            f_out.write(f"- **标题**: {detail['envelope'].title}\n")
            f_out.write(f"- **最后时间**: {detail['envelope'].time_human}\n\n---\n\n")
            for line in f_in:
                try:
                    obj = json.loads(line)
                    role = obj.get("role", "message")
                    content = obj.get("content", [])
                    text = ""
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and "text" in c:
                                text += c["text"] + "\n"
                    elif isinstance(content, str):
                        text = content
                    if text.strip():
                        f_out.write(f"### [{role.upper()}]\n{text.strip()}\n\n")
                except:
                    pass
        return target_file
