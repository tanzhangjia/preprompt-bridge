"""
主入口 handler — 协调各个模块工作
"""
from . import filters, roles, modes, templates, sanitize
from .context import Context
from .history import HistoryBuilder


def handler(params: dict) -> dict:
    """
    主入口。

    Args:
        params: 请求参数，见 README。

    Returns:
        {"prompt": str, "meta": dict}
    """
    # ── 解析参数 ──
    ctx = Context(params)

    # ── 问题 ──
    raw_question = ctx.get_question()
    question = sanitize.clean(raw_question, ctx.safe_mode) if raw_question else ""

    # ── 历史对话 ──
    history = HistoryBuilder(ctx).build() if ctx.his else ""

    # ── 系统指令 ──
    sys_prompt = _build_sys_prompt(ctx)

    # ── 模式注入 ──
    mode_suffix = modes.get_suffix(ctx.mode, ctx.lang) if ctx.mode else ""

    # ── 上下文 ──
    context_str = _build_context(ctx)

    # ── 过滤规则 ──
    filter_tags = filters.resolve(ctx)

    # ── 渲染 ──
    prompt = templates.render(
        template=ctx.template,
        question=question,
        history=history,
        sys_prompt=sys_prompt,
        context=context_str,
        mode_suffix=mode_suffix,
        lang=ctx.lang,
        filter_tags=filter_tags,
        his_count=str(history.count_rounds()) if hasattr(history, 'count_rounds') else "0",
    )

    history_rounds = history.count_rounds() if hasattr(history, 'count_rounds') else \
                     sum(1 for line in history.split("\n") if line.startswith("用户：")) if history else 0

    meta = {
        "has_question": bool(question),
        "history_rounds": history_rounds,
        "has_sys_prompt": bool(sys_prompt),
        "has_context": bool(context_str),
        "mode": ctx.mode,
        "lang": ctx.lang,
        "role": ctx.role,
        "filter_tags": filter_tags,
        "safe_mode": ctx.safe_mode,
        "prompt_length": len(prompt),
    }

    return {"prompt": prompt, "meta": meta}


def _build_sys_prompt(ctx) -> str:
    """拼装系统指令：角色 + 自定义 sys_prompt + 风格规则"""
    parts = []

    role_text = roles.get(ctx.role, ctx.lang)
    if role_text:
        parts.append(role_text)

    if ctx.sys_prompt:
        parts.append(sanitize.clean(str(ctx.sys_prompt), ctx.safe_mode))

    if ctx.style_rules:
        parts.append(ctx.style_rules)

    return "\n".join(parts)


def _build_context(ctx) -> str:
    """拼装额外上下文"""
    if not ctx.context or not isinstance(ctx.context, dict):
        return ""
    pairs = []
    for k, v in ctx.context.items():
        if v is not None:
            pairs.append(f"{k}：{sanitize.clean(str(v), ctx.safe_mode)}")
    return "\n".join(pairs)
