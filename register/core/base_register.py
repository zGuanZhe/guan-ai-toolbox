# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Base Register Interface
参考 any-auto-register 的平台注册抽象基类。
"""

import abc
from typing import Dict, Any, Optional

class BaseRegisterEngine(abc.ABC):
    @property
    @abc.abstractmethod
    def provider(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def register_one(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行单次自动化注册
        :return: 包含成功状态、email、token、uid 等结果字典
        """
        pass
