# -*- coding: utf-8 -*-
from .workbuddy_adapter import WorkBuddyRestoreAdapter
from .trae_adapter import TraeRestoreAdapter
from .zcode_adapter import ZCodeRestoreAdapter
from .claudecode_adapter import ClaudeCodeRestoreAdapter
from .antigravity_adapter import AntigravityRestoreAdapter
from .gpt_adapter import GptRestoreAdapter

def get_registered_adapters():
    return [
        WorkBuddyRestoreAdapter(),
        TraeRestoreAdapter(),
        ZCodeRestoreAdapter(),
        ClaudeCodeRestoreAdapter(),
        AntigravityRestoreAdapter(),
        GptRestoreAdapter(),
    ]
