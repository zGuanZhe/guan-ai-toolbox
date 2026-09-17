# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Session Envelope (会话元数据统一契约)
参考 ccswitch 与现代 AI 终端会话管理架构，定义跨工具通用的会话对象。
"""

import os
import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

@dataclass
class SessionEnvelope:
    """标准会话元数据信封"""
    session_id: str                      # 会话唯一标识符 (UUID 或 Hash)
    tool_id: str                         # 所属工具 ID (workbuddy, trae, zcode, claudecode, antigravity, gpt)
    tool_name: str                       # 所属工具名称
    workspace: str                       # 关联的项目路径或工作区 (CWD)
    title: str                           # 会话标题或首条指令摘要
    created_at: Optional[datetime.datetime] = None  # 创建时间
    updated_at: Optional[datetime.datetime] = None  # 最后活跃时间
    message_count: int = 0               # 消息总行数/轮次
    size_bytes: int = 0                  # 物理文件大小 (字节)
    status: str = "active"               # 状态: active(正常), hidden(跨账号隐藏), deleted(软删除), archived(已归档)
    raw_path: str = ""                   # 物理源文件路径 (如 jsonl, sqlite 路径)
    extra_meta: Dict[str, Any] = field(default_factory=dict) # 工具特定扩展元数据

    @property
    def size_human(self) -> str:
        """格式化物理大小"""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_bytes / (1024 * 1024):.1f} MB"

    @property
    def time_human(self) -> str:
        """格式化更新时间"""
        if self.updated_at:
            return self.updated_at.strftime("%Y-%m-%d %H:%M")
        elif self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M")
        return "未知时间"

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.created_at:
            d["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            d["updated_at"] = self.updated_at.isoformat()
        return d
