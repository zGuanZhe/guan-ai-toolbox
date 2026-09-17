# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Base Restore Adapter
严禁任何“一键全量恢复”！定义严格按工具隔离、按单会话操作的通用抽象基类。
"""

import abc
from typing import List, Optional, Dict, Any
from .session_envelope import SessionEnvelope

class BaseRestoreAdapter(abc.ABC):
    """
    通用 AI 编程工具会话管理与恢复适配器基类
    设计原则：
    1. 工具之间物理隔离，互不串联；
    2. 严格按工作区/项目索引分级定位；
    3. 严禁全量无差别覆盖，必须指定单一或特定 session_id；
    4. 两阶段安全机制：单会话快照 -> 单会话恢复/导出。
    """

    @property
    @abc.abstractmethod
    def tool_id(self) -> str:
        """工具唯一标识符 (例如: 'workbuddy', 'trae', 'zcode', 'claudecode', 'antigravity', 'gpt')"""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """工具显示名称"""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """工具特性与存储机制说明"""
        pass

    @abc.abstractmethod
    def is_installed(self) -> bool:
        """检测当前系统是否安装了该工具或存在其数据存储目录"""
        pass

    @abc.abstractmethod
    def get_data_dir(self) -> str:
        """获取该工具的数据存储根路径"""
        pass

    @abc.abstractmethod
    def list_workspaces(self) -> List[str]:
        """
        获取该工具下管理的所有独立工作区或项目列表 (CWD / Project Paths)
        让用户可以按项目过滤，避免全局会话混杂。
        """
        pass

    @abc.abstractmethod
    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        """
        检索该工具的历史会话列表
        :param workspace: 可选的工作区过滤条件
        :return: 结构化会话元数据信封列表
        """
        pass

    @abc.abstractmethod
    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定会话的完整上下文预览与元数据
        供用户在执行恢复前预览确认，杜绝盲操。
        """
        pass

    @abc.abstractmethod
    def backup_session(self, session_id: str) -> str:
        """
        仅对指定的单一会话或其所在上下文创建安全时间戳快照
        :return: 备份保存路径
        """
        pass

    @abc.abstractmethod
    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """
        【严禁全量恢复】仅针对指定的单一 session_id 执行恢复
        :param session_id: 必须提供明确的会话 ID
        :param options: 附加参数 (如目标用户 UID, 覆盖确认等)
        :return: bool 是否执行成功
        """
        pass

    @abc.abstractmethod
    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        """
        将指定会话导出为标准可读的 Markdown 或 JSONL 归档文档
        :return: 导出的文件完整路径
        """
        pass
