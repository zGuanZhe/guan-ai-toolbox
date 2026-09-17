#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Register & Account Manager Main Entrypoint
多厂家自动注册与多工具账号池管理中枢。
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

cur_dir = os.path.dirname(os.path.abspath(__file__))
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from cli.register_ui import RegisterUI

def main():
    ui = RegisterUI()
    ui.run()

if __name__ == "__main__":
    main()
