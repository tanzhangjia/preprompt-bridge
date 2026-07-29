"""
sanitize — 敏感信息清洗

独立模块，不依赖其他模块。
"""
from . import filters


def clean(text: str, safe_mode: bool = False) -> str:
    """清理文本中的敏感信息，委托给 filters.clean"""
    return filters.clean(text, safe_mode)
