"""
主入口 handler — 基于拼接规则系统

全部逻辑委托给 context + rules + templates，自己不处理任何具体业务。
"""
from .context import Context
from .rules import build_blocks, get_order
from . import templates


def handler(params: dict) -> dict:
    ctx = Context(params)
    order = get_order(ctx)
    blocks = build_blocks(ctx, order)

    prompt = templates.render_blocks(
        template=ctx.template,
        blocks=blocks,
        lang=ctx.lang,
        ctx=ctx,
    )

    meta = {
        "has_question": bool(blocks.get("question")),
        "history_rounds": len(ctx.his) if isinstance(ctx.his, list) else 0,
        "has_sys_prompt": bool(blocks.get("sys_prompt")),
        "has_context": bool(blocks.get("context")),
        "mode": ctx.mode,
        "lang": ctx.lang,
        "role": ctx.role,
        "prompt_length": len(prompt),
        "rules_applied": order,
    }

    return {"prompt": prompt, "meta": meta}
