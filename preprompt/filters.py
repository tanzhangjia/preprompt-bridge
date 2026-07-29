"""
过滤系统 — 内容过滤规则

职责：
- 敏感信息过滤（safe_mode）
- 输出格式指令
- 可扩展的过滤规则注册
- 用户自定义 filter_rules 支持

过滤规则是插件式的：
  filters.register_rule("no_pii", my_filter_function)
"""

# ── 敏感信息模式（先长后短，兼容中文语境） ──
_DEFAULT_PATTERNS = [
    (r"(?<![\d])\d{17}[\dXx](?![\d])", "[身份证]"),
    (r"(?<![\d])1[3-9]\d{9}(?![\d])", "[手机号]"),
    (r"[\w.-]+@[\w.-]+\.\w{2,4}", "[邮箱]"),
]

# ── 全局规则注册表 ──
_RULES = {}


def register_rule(name: str, fn: callable):
    """注册自定义过滤规则。

    Args:
        name: 规则名（用于 filter_rules 引用）
        fn: callable(text: str) -> str
    """
    _RULES[name] = fn


def clean(text: str, safe_mode: bool = False) -> str:
    """文本清洗"""
    import re
    if not isinstance(text, str):
        return ""
    if not safe_mode:
        return text

    t = text
    for pattern, replacement in _DEFAULT_PATTERNS:
        t = re.sub(pattern, replacement, t)
    return t


def resolve(ctx) -> str:
    """根据 Context 解析过滤规则，返回注入到 prompt 中的过滤标签"""
    from . import sanitize
    if not ctx:
        return ""

    tags = []

    # 输出格式
    if ctx.output_format:
        tags.append(f"输出格式：{ctx.output_format}")

    # 自定义过滤规则
    if ctx.filter_rules:
        rules = ctx.filter_rules if isinstance(ctx.filter_rules, list) else [ctx.filter_rules]
        for r in rules:
            if isinstance(r, str) and r in _RULES:
                tags.append(_RULES[r](ctx))
            elif callable(r):
                tags.append(r(ctx))

    return "\n".join(tags) if tags else ""
