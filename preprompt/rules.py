"""
拼接规则系统 — 定义 prompt 由哪些模块按什么顺序拼接

预置规则 + 用户自定义。规则是一个 dict，描述一个模块的输出。
"""
from . import roles, modes
from .history import HistoryBuilder


# ── 预置规则 ──
# 每个规则是一个 callable(ctx) -> (block_name, text)
# block_name 用于模板中的条件判断

def _rule_sys_prompt(ctx):
    """系统指令：角色 + sys_prompt + style_rules"""
    parts = []
    role_text = roles.get(ctx.role, ctx.lang)
    if role_text:
        parts.append(role_text)
    if ctx.sys_prompt:
        parts.append(ctx.sys_prompt)
    if ctx.style_rules:
        parts.append(ctx.style_rules)
    return ("sys_prompt", "\n".join(parts).strip())


def _rule_history(ctx):
    """历史对话"""
    h = HistoryBuilder(ctx)
    text = h.build()
    return ("history", text)


def _rule_context(ctx):
    """额外上下文"""
    if not isinstance(ctx.context, dict):
        return ("context", "")
    pairs = []
    for k, v in ctx.context.items():
        if v is not None:
            pairs.append(f"{k}：{v}")
    return ("context", "\n".join(pairs))


def _rule_question(ctx):
    """用户问题"""
    return ("question", ctx.get_question())


def _rule_mode_suffix(ctx):
    """模式引导后缀"""
    return ("mode_suffix", modes.get_suffix(ctx.mode, ctx.lang))


def _rule_extra_vars(ctx):
    """自定义变量"""
    ev = ctx.get_extra_variables()
    return ("extra_vars", ev)


def _rule_output_format(ctx):
    """输出格式要求"""
    if ctx.output_format:
        return ("output_format", f"输出格式：{ctx.output_format}")
    return ("output_format", "")


# ── 默认规则集合 ──
BUILTIN_RULES = {
    "sys_prompt": _rule_sys_prompt,
    "history": _rule_history,
    "context": _rule_context,
    "question": _rule_question,
    "mode_suffix": _rule_mode_suffix,
    "extra_vars": _rule_extra_vars,
    "output_format": _rule_output_format,
}

# 默认拼接顺序
DEFAULT_ORDER = [
    "sys_prompt",
    "history",
    "context",
    "output_format",
    "question",
    "mode_suffix",
    "extra_vars",
]


# ── 用户自定义规则注册 ──
_USER_RULES = {}


def register_rule(name: str, fn: callable):
    """注册自定义拼接规则。

    Args:
        name: 规则名
        fn: callable(ctx) -> (block_name, text_or_dict)
            返回 (名称, 内容)，内容为空则跳过该块
    """
    _USER_RULES[name] = fn


def get_order(ctx) -> list:
    """获取最终执行顺序"""
    if ctx.rules:
        return ctx.rules
    return DEFAULT_ORDER


def build_blocks(ctx, order: list = None) -> dict:
    """按顺序执行规则，返回 {block_name: text} 的字典"""
    order = order or get_order(ctx)
    all_rules = {**BUILTIN_RULES, **_USER_RULES}
    blocks = {}

    for name in order:
        rule_fn = all_rules.get(name)
        if not rule_fn:
            continue
        try:
            block_name, text = rule_fn(ctx)
            if text:
                blocks[block_name] = text
        except Exception:
            continue

    return blocks
