"""
PrePrompt Bridge — 工作流 Prompt 预处理器

插件架构，每个模块可独立扩展。
"""
from .handler import handler
from . import roles, modes, templates, rules
from .context import Context, register_variable
from .rules import register_rule
