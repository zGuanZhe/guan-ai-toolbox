# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Restore Engine
恢复引擎总控：注册 6 大专属适配器，负责系统探测与分发调度。
"""

from typing import List, Optional
from core.base_adapter import BaseRestoreAdapter

class RestoreEngine:
    def __init__(self):
        self._adapters = {}

    def register_adapter(self, adapter: BaseRestoreAdapter):
        self._adapters[adapter.tool_id.lower()] = adapter

    def get_adapter(self, tool_id: str) -> Optional[BaseRestoreAdapter]:
        return self._adapters.get(tool_id.lower())

    def list_all_adapters(self) -> List[BaseRestoreAdapter]:
        return list(self._adapters.values())

    def list_installed_adapters(self) -> List[BaseRestoreAdapter]:
        return [a for a in self._adapters.values() if a.is_installed()]
