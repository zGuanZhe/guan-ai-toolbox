# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Restore Manager
通用恢复管理器：自动检测系统中安装的所有 AI 工具，并调度对应适配器。
"""

import os
import sys
from adapters import AVAILABLE_ADAPTERS

class RestoreManager:
    def __init__(self):
        self.adapters = AVAILABLE_ADAPTERS

    def get_installed_adapters(self):
        return [a for a in self.adapters if a.is_installed()]

    def get_adapter_by_id(self, tool_id: str):
        for a in self.adapters:
            if a.tool_id.lower() == tool_id.lower():
                return a
        return None

    def print_tools_overview(self):
        print("=" * 75)
        print(f"{'序号':^4} | {'工具名称':<25} | {'检测状态':^10} | {'数据路径'}")
        print("-" * 75)
        for idx, a in enumerate(self.adapters, 1):
            installed = a.is_installed()
            status_str = "✅ 已检测" if installed else "❌ 未安装"
            data_path = a.get_data_dir() if installed else "未找到路径"
            if len(data_path) > 35:
                data_path = "..." + data_path[-32:]
            print(f"{idx:^4} | {a.name:<25} | {status_str:^10} | {data_path}")
        print("=" * 75)
