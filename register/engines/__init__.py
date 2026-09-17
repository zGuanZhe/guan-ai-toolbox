# -*- coding: utf-8 -*-
from typing import List
from core.base_register import BaseRegisterEngine
from engines.workbuddy_reg import WorkBuddyRegisterEngine
from engines.qoder_reg import QoderRegisterEngine
from engines.openai_reg import OpenAiRegisterEngine
from engines.tavily_reg import TavilyRegisterEngine
from engines.grok_reg import GrokRegisterEngine

def get_registered_engines() -> List[BaseRegisterEngine]:
    return [
        WorkBuddyRegisterEngine(),
        QoderRegisterEngine(),
        OpenAiRegisterEngine(),
        TavilyRegisterEngine(),
        GrokRegisterEngine()
    ]
