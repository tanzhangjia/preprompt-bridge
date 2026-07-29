"""
PrePrompt Bridge — 工作流 Prompt 预处理器

设计为插件架构，每个功能模块可独立替换/扩展。
"""
from .handler import handler
from . import filters, roles, modes, templates, sanitize
from .context import Context
from .history import HistoryBuilder
