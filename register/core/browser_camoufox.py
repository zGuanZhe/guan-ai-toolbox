# -*- coding: utf-8 -*-
r"""
Guan's AI Toolbox - Camoufox Fingerprint Browser Driver
集成 "D:\Test\Sub2\camoufox\camoufox.exe" 反检测指纹浏览器驱动。
具备 Canvas/WebGL 指纹混淆、字体伪装、WebRTC 保护与反自动化检测能力。
"""

import os
import subprocess
import time
from typing import Optional, List

class CamoufoxBrowser:
    DEFAULT_EXE = r"D:\Test\Sub2\camoufox\camoufox.exe"

    def __init__(self, exe_path: Optional[str] = None):
        self.exe_path = exe_path or self.DEFAULT_EXE
        if not os.path.exists(self.exe_path):
            raise FileNotFoundError(f"未找到 Camoufox 指纹浏览器可执行文件: {self.exe_path}")

    def is_available(self) -> bool:
        return os.path.exists(self.exe_path)

    def launch(self, 
               url: Optional[str] = None, 
               headless: bool = False, 
               user_data_dir: Optional[str] = None,
               extra_args: Optional[List[str]] = None) -> subprocess.Popen:
        """
        启动 Camoufox 指纹浏览器进程
        """
        cmd = [self.exe_path]
        
        if headless:
            cmd.append("--headless")
            
        if user_data_dir:
            os.makedirs(user_data_dir, exist_ok=True)
            cmd.extend(["-profile", user_data_dir])
            
        if extra_args:
            cmd.extend(extra_args)
            
        if url:
            cmd.append(url)
            
        print(f"[*] 正在拉起 Camoufox 指纹浏览器: {' '.join(cmd[:3])} ...")
        proc = subprocess.Popen(cmd, shell=False)
        return proc

    def test_run(self) -> bool:
        """测试指纹浏览器连通性"""
        try:
            p = self.launch("about:blank", headless=False)
            time.sleep(2)
            p.terminate()
            return True
        except Exception as e:
            print(f"[!] Camoufox 启动测试失败: {e}")
            return False
