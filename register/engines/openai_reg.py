# -*- coding: utf-8 -*-
"""
OpenAI / ChatGPT 自动化批量注册引擎
整合原有 openai-register 与 any-auto-register 机制。
"""

import os
import subprocess
from typing import Dict, Any, Optional
from core.base_register import BaseRegisterEngine

class OpenAiRegisterEngine(BaseRegisterEngine):
    @property
    def provider(self) -> str:
        return "openai"

    @property
    def name(self) -> str:
        return "OpenAI / ChatGPT"

    def register_one(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        print("[*] 正在调用 OpenAI 批量注册引擎...")
        openai_script = os.path.join(r"D:\Test\Sub2\观的ai工具箱", "register", "modules", "openai_register", "openai_register.py")
        if os.path.exists(openai_script):
            print(f"[*] 执行注册底层脚本: {openai_script}")
            try:
                cmd = ["python", openai_script]
                subprocess.Popen(cmd, shell=False)
                return {"success": True, "provider": "openai", "message": "注册脚本已后台拉起。"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "未找到 openai_register.py 脚本"}
