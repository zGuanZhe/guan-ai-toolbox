# -*- coding: utf-8 -*-
"""
Tavily 搜索 API 自动化批量注册引擎
整合原有 tavily-register 流水线，批量产出 Search API Keys。
"""

import os
import subprocess
from typing import Dict, Any, Optional
from core.base_register import BaseRegisterEngine

class TavilyRegisterEngine(BaseRegisterEngine):
    @property
    def provider(self) -> str:
        return "tavily"

    @property
    def name(self) -> str:
        return "Tavily Search API"

    def register_one(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        print("[*] 正在启动 Tavily 批量开户引擎...")
        tavily_script = os.path.join(r"D:\Test\Sub2\观的ai工具箱", "register", "modules", "tavily_register", "signup.py")
        if os.path.exists(tavily_script):
            try:
                cmd = ["python", tavily_script]
                subprocess.Popen(cmd, shell=False)
                return {"success": True, "provider": "tavily", "message": "Tavily 注册流水线已拉起。"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "未找到 tavily signup.py 脚本"}
