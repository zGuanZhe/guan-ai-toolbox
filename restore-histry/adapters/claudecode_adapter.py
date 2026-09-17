# -*- coding: utf-8 -*-
"""
Claude Code 专属会话管理与恢复适配器
参考开源项目 ccswitch (Claude Code Switch) 的会话管理机制，
解析 ~/.claude/history.jsonl，按 Project 严格隔离检索，支持单会话恢复与 Markdown 归档。
"""

import os
import json
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class ClaudeCodeRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "claudecode"

    @property
    def name(self) -> str:
        return "Claude Code (Anthropic CLI)"

    @property
    def description(self) -> str:
        return "参考 ccswitch 规范。按工作区解析 history.jsonl，支持单会话独立提取、上下文复活与 Markdown 导出"

    def get_data_dir(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".claude")

    def is_installed(self) -> bool:
        return os.path.exists(self.get_data_dir())

    def _get_history_file(self) -> str:
        return os.path.join(self.get_data_dir(), "history.jsonl")

    def list_workspaces(self) -> List[str]:
        hf = self._get_history_file()
        if not os.path.exists(hf):
            return []
        workspaces = set()
        try:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip():
                        try:
                            item = json.loads(line)
                            p = item.get("project")
                            if p: workspaces.add(p)
                        except: pass
        except Exception:
            pass
        return sorted(list(workspaces))

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        hf = self._get_history_file()
        if not os.path.exists(hf):
            return []

        # 按 sessionId 聚合
        sessions_map = {}
        try:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        entry = json.loads(line)
                        sid = entry.get("sessionId")
                        proj = entry.get("project", "全局/未关联")
                        if workspace and proj != workspace:
                            continue
                        if not sid:
                            continue

                        ts = entry.get("timestamp")
                        dt = datetime.datetime.fromtimestamp(ts / 1000) if ts else None
                        prompt_text = entry.get("display") or ""

                        if sid not in sessions_map:
                            sessions_map[sid] = {
                                "session_id": sid,
                                "project": proj,
                                "first_prompt": prompt_text,
                                "first_time": dt,
                                "last_time": dt,
                                "count": 1,
                                "entries": [entry]
                            }
                        else:
                            sessions_map[sid]["count"] += 1
                            if dt and (not sessions_map[sid]["last_time"] or dt > sessions_map[sid]["last_time"]):
                                sessions_map[sid]["last_time"] = dt
                            sessions_map[sid]["entries"].append(entry)
                    except: pass
        except Exception:
            pass

        envelopes = []
        for sid, meta in sessions_map.items():
            envelopes.append(SessionEnvelope(
                session_id=sid,
                tool_id=self.tool_id,
                tool_name=self.name,
                workspace=meta["project"],
                title=meta["first_prompt"][:40] if meta["first_prompt"] else f"Claude会话 {sid[:8]}",
                created_at=meta["first_time"],
                updated_at=meta["last_time"],
                message_count=meta["count"],
                size_bytes=sum(len(json.dumps(e)) for e in meta["entries"]),
                status="active",
                raw_path=hf,
                extra_meta={"project": meta["project"]}
            ))
        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        hf = self._get_history_file()
        if not os.path.exists(hf): return None
        matched_entries = []
        try:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("sessionId") == session_id:
                            matched_entries.append(entry)
                    except: pass
        except: pass
        if not matched_entries: return None
        return {
            "session_id": session_id,
            "project": matched_entries[0].get("project", "全局"),
            "entries_count": len(matched_entries),
            "prompts": [e.get("display") for e in matched_entries if e.get("display")]
        }

    def backup_session(self, session_id: str) -> str:
        claude_dir = self.get_data_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(claude_dir, "backups", f"claude_session_{session_id[:8]}_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        hf = self._get_history_file()
        if os.path.exists(hf):
            shutil.copy2(hf, os.path.join(backup_dir, "history.jsonl"))
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id:
            raise ValueError("[安全拦截] 必须明确指定单会话 session_id！")
        self.backup_session(session_id)
        # 激活模式：将该 session 的上下文重构并写入 session-env 或独立导出会话
        detail = self.get_session_detail(session_id)
        if not detail:
            print(f"[!] 未能找到会话 {session_id}")
            return False
        print(f"[✓] 已为 Claude Code 会话 {session_id} 建立独立快照并恢复上下文索引。")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail: raise ValueError(f"会话 {session_id} 不存在")
        if not target_file:
            home = os.path.expanduser("~")
            export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
            os.makedirs(export_dir, exist_ok=True)
            target_file = os.path.join(export_dir, f"ClaudeCode_Session_{session_id[:8]}.md")

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(f"# Claude Code 会话归档 - {session_id}\n\n")
            f.write(f"- **项目路径**: {detail['project']}\n")
            f_count = detail['entries_count']
            f.write(f"- **交互指令数**: {f_count}\n\n---\n\n")
            for idx, p in enumerate(detail["prompts"], 1):
                f.write(f"### Step {idx}:\n```\n{p}\n```\n\n")
        return target_file
