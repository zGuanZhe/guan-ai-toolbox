#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Codex Instruct Forwarder
Directs execution to the safe and verified codex-instruct-v2.py engine.
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
v2_script = os.path.join(script_dir, "codex-instruct-v2.py")

if __name__ == "__main__":
    import runpy
    sys.path.insert(0, script_dir)
    runpy.run_path(v2_script, run_name="__main__")
