# -*- coding: utf-8 -*-
"""
Grok (x.ai) 自动化注册引擎
整合原有 grok-register 流水线，调用 YesCaptcha 与邮箱服务自动产出 Grok SSO Token。
"""

import os
import subprocess
from typing import Dict, Any, Optional
from core.base_register import BaseRegisterEngine

class GrokRegisterEngine(BaseRegisterEngine):
    @property
    def provider(self) -> str:
        return "grok"

    @property
    def name(self) -> str:
        return "xAI Grok"

    def register_one(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        print("[*] 正在启动 Grok 自动化注册引擎...")
        script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules", "grok_register")
        grok_script = os.path.join(script_dir, "grok.py")
        if os.path.exists(grok_script):
            try:
                print(f"[*] 运行 Grok 脚本: {grok_script}")
                cmd = ["python", grok_script]
                subprocess.Popen(cmd, cwd=script_dir, shell=False)
                return {"success": True, "provider": "grok", "message": "Grok 注册流程已在独立进程中拉起。"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "未找到 grok.py 脚本"}
