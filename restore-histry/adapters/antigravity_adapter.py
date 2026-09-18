# -*- coding: utf-8 -*-
"""
Google Antigravity (AGY / Gemini) 专属会话管理与恢复适配器
管理 ~/.gemini/antigravity/brain/ 下的多达 37+ 个独立会话目录，支持按 task 检索与导出。
"""

import os
import glob
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class AntigravityRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "antigravity"

    @property
    def name(self) -> str:
        return "Google Antigravity (AGY / Gemini)"

    @property
    def description(self) -> str:
        return "管理 brain/<conv_id> 目录架构。精确透视 task.md、步数、运行日志与思维链，支持单会话激活"

    def get_data_dir(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "brain")

    def is_installed(self) -> bool:
        return os.path.exists(self.get_data_dir())

    def list_workspaces(self) -> List[str]:
        # Antigravity 会话可能分布在全局或不同工作区
        return ["Google Antigravity Brain 统一工作区"]

    def _get_db_path(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "conversation_summaries.db")

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        brain_dir = self.get_data_dir()
        db_path = self._get_db_path()
        db_info = {}

        # 1. 优先从 conversation_summaries.db 获取精准活跃状态与元数据
        if os.path.exists(db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(db_path, timeout=3.0)
                c = conn.cursor()
                rows = c.execute("SELECT conversation_id, title, preview, step_count, last_modified_time, status, killed, workspace_uris FROM conversation_summaries").fetchall()
                for r in rows:
                    cid, title, prev, steps, l_time, stat, killed, ws_uris = r
                    db_info[cid] = {
                        "title": title or prev or f"Antigravity 会话 {cid[:8]}",
                        "step_count": steps or 0,
                        "last_modified_time": l_time,
                        "status": "killed" if killed else ("active" if "IDLE" in str(stat) or "RUNNING" in str(stat) else str(stat).lower()),
                        "workspace": ws_uris or "Antigravity Workspace"
                    }
                conn.close()
            except Exception:
                pass

        envelopes = []
        # 扫描 brain 目录下的会话
        if os.path.exists(brain_dir):
            for conv_id in os.listdir(brain_dir):
                conv_path = os.path.join(brain_dir, conv_id)
                if not os.path.isdir(conv_path): continue

                meta = db_info.get(conv_id, {})
                title = meta.get("title")
                status = meta.get("status", "active")
                steps = meta.get("step_count", 0)

                # 若 DB 未命中，回退读取 task.md 获取真实任务标题
                if not title:
                    task_file = os.path.join(conv_path, "task.md")
                    title = f"Antigravity 会话 {conv_id[:8]}"
                    if os.path.exists(task_file):
                        try:
                            with open(task_file, "r", encoding="utf-8", errors="ignore") as f:
                                for line in f:
                                    if line.strip().startswith("#"):
                                        title = line.strip().lstrip("#").strip()
                                        break
                        except: pass

                # 统计步数与大小
                transcript = os.path.join(conv_path, ".system_generated", "logs", "transcript.jsonl")
                size = 0
                if os.path.exists(transcript):
                    size = os.path.getsize(transcript)
                    if steps == 0:
                        try:
                            with open(transcript, "rb") as f:
                                for _ in f: steps += 1
                        except: pass

                mtime = os.path.getmtime(conv_path)

                envelopes.append(SessionEnvelope(
                    session_id=conv_id,
                    tool_id=self.tool_id,
                    tool_name=self.name,
                    workspace=meta.get("workspace", "Antigravity Workspace"),
                    title=title,
                    updated_at=datetime.datetime.fromtimestamp(mtime),
                    message_count=steps,
                    size_bytes=size,
                    status=status,
                    raw_path=conv_path,
                    extra_meta={"killed": (status == "killed"), "db_recorded": conv_id in db_info}
                ))

        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        conv_path = os.path.join(self.get_data_dir(), session_id)
        if not os.path.exists(conv_path): return None
        task_md = ""
        tf = os.path.join(conv_path, "task.md")
        if os.path.exists(tf):
            try:
                with open(tf, "r", encoding="utf-8", errors="ignore") as f:
                    task_md = f.read(1000)
            except: pass
        return {
            "session_id": session_id,
            "path": conv_path,
            "task_preview": task_md
        }

    def backup_session(self, session_id: str) -> str:
        src = os.path.join(self.get_data_dir(), session_id)
        if not os.path.exists(src): raise ValueError("会话目录不存在")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "backups", f"brain_{session_id[:8]}_{ts}")
        shutil.copytree(src, backup_dir, dirs_exist_ok=True)
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id:
            raise ValueError("必须明确指定 session_id！")
        conv_path = os.path.join(self.get_data_dir(), session_id)

        # 1. 严格创建安全快照
        if os.path.exists(conv_path):
            self.backup_session(session_id)
        else:
            # 若 brain 目录已不存在该会话，尝试从历史备份中恢复目录
            backups_base = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "backups")
            found_bak = None
            if os.path.exists(backups_base):
                for d in sorted(os.listdir(backups_base), reverse=True):
                    if session_id[:8] in d:
                        found_bak = os.path.join(backups_base, d)
                        break
            if found_bak and os.path.exists(found_bak):
                shutil.copytree(found_bak, conv_path, dirs_exist_ok=True)

        # 2. 真实更新 conversation_summaries.db：将 killed 状态解除，恢复为 IDLE 活跃态
        db_path = self._get_db_path()
        if os.path.exists(db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(db_path, timeout=5.0)
                c = conn.cursor()
                now_ts = int(datetime.datetime.now().timestamp())
                c.execute("""
                    UPDATE conversation_summaries
                    SET killed = 0, status = 'CASCADE_RUN_STATUS_IDLE', last_modified_time = ?
                    WHERE conversation_id = ?
                """, (str(now_ts), session_id))
                affected = c.rowcount
                conn.commit()
                conn.close()
                print(f"[OK] Antigravity 会话索引表已更新 (affected rows: {affected})，会话已重新激活！")
            except Exception as e:
                print(f"[!] 更新 Antigravity 索引表错误: {e}")

        print(f"[OK] Antigravity 会话 {session_id} 恢复完成。")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        src = os.path.join(self.get_data_dir(), session_id)
        home = os.path.expanduser("~")
        export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
        os.makedirs(export_dir, exist_ok=True)
        target = target_file or os.path.join(export_dir, f"Antigravity_{session_id[:8]}.md")

        task_f = os.path.join(src, "task.md")
        plan_f = os.path.join(src, "implementation_plan.md")
        walk_f = os.path.join(src, "walkthrough.md")
        transcript_f = os.path.join(src, ".system_generated", "logs", "transcript.jsonl")

        with open(target, "w", encoding="utf-8") as f_out:
            f_out.write(f"# Google Antigravity 会话完整档案 - {session_id}\n\n")
            f_out.write(f"- **会话 ID**: `{session_id}`\n")
            f_out.write(f"- **归档时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")

            for name, p in [("任务定义 (Task)", task_f), ("实施计划 (Implementation Plan)", plan_f), ("成果总览 (Walkthrough)", walk_f)]:
                if os.path.exists(p):
                    f_out.write(f"## {name}\n\n")
                    with open(p, "r", encoding="utf-8", errors="ignore") as f_in:
                        f_out.write(f_in.read() + "\n\n---\n\n")

            # 导出真实用户提问与模型交互对话流
            if os.path.exists(transcript_f):
                f_out.write("## 真实对话交互流 (Conversation Transcript)\n\n")
                with open(transcript_f, "r", encoding="utf-8", errors="ignore") as f_tr:
                    turn_idx = 1
                    for line in f_tr:
                        try:
                            import json
                            step = json.loads(line)
                            step_type = step.get("type", "")
                            content = step.get("content", "")
                            if step_type == "USER_INPUT" and content:
                                f_out.write(f"### [USER Turn #{turn_idx}]\n\n{content.strip()}\n\n")
                                turn_idx += 1
                            elif step_type == "PLANNER_RESPONSE" and content:
                                f_out.write(f"### [ANTIGRAVITY]\n\n{content.strip()}\n\n---\n\n")
                        except:
                            pass

        print(f"[OK] Antigravity 会话已成功导出至: {target}")
        return target
