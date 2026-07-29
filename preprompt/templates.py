"""
模板系统 — prompt 模板渲染

基于 blocks 字典渲染。支持默认模板和自定义模板。
"""
import re

_TEMPLATE_HOOKS = []


def register_hook(fn: callable):
    """注册后期处理钩子"""
    _TEMPLATE_HOOKS.append(fn)


def get_labels(lang: str = "zh") -> dict:
    """获取语言标签"""
    labels = {
        "zh": {
            "history": "历史对话：",
            "context": "额外信息：",
            "question": "用户问题：",
            "output_format": "输出格式：",
        },
        "en": {
            "history": "Conversation history:",
            "context": "Additional context:",
            "question": "User question:",
            "output_format": "Output format:",
        },
        "ja": {
            "history": "会話履歴：",
            "context": "追加情報：",
            "question": "ユーザーの質問：",
            "output_format": "出力形式：",
        },
    }
    return labels.get(lang, labels["zh"])


def render_blocks(template: str = None, blocks: dict = None, lang: str = "zh", ctx=None) -> str:
    """渲染 blocks 为 prompt 字符串"""
    from . import rules

    blocks = blocks or {}
    labels = get_labels(lang)

    if template:
        vars = dict(blocks)
        extra_vars = vars.pop("extra_vars", {})
        if isinstance(extra_vars, dict):
            for k, v in extra_vars.items():
                vars[k] = v
        return _render_custom(template, vars)

    # 如果用户指定了自定义 rules，默认模板按裸 block 名渲染
    if ctx and ctx.rules:
        parts = []
        for name in ctx.rules:
            val = blocks.get(name)
            if val is None:
                continue
            # extra_vars 是 dict，flatten
            if isinstance(val, dict):
                for k, v in val.items():
                    if v:
                        parts.append(f"{k}：{v}")
            elif isinstance(val, str) and val.strip():
                parts.append(val.strip())
        result = "\n".join(parts)
        for hook in _TEMPLATE_HOOKS:
            result = hook(result, blocks)
        return result

    # 默认模板：按 labels 组织
    parts = []
    if blocks.get("sys_prompt"):
        parts.append(blocks["sys_prompt"])
        parts.append("")
    if blocks.get("history"):
        parts.append(labels["history"])
        parts.append(blocks["history"])
        parts.append("")
    if blocks.get("context"):
        parts.append(labels["context"])
        parts.append(blocks["context"])
        parts.append("")
    if blocks.get("output_format"):
        parts.append(blocks["output_format"])
        parts.append("")
    if blocks.get("question"):
        parts.append(f"{labels['question']}{blocks['question']}")
    if blocks.get("mode_suffix"):
        parts.append(blocks["mode_suffix"])
    extra_vars = blocks.get("extra_vars", {})
    if isinstance(extra_vars, dict):
        for k, v in extra_vars.items():
            parts.append(f"{k}：{v}")

    result = "\n".join(parts).strip()
    for hook in _TEMPLATE_HOOKS:
        result = hook(result, blocks)
    return result


def _render_custom(tpl: str, vars: dict) -> str:
    """自定义模板渲染"""
    # 条件块
    result = re.sub(
        r"\{% if (\w+) %\}([\s\S]*?)\{% endif %\}",
        lambda m: m.group(2) if vars.get(m.group(1)) else "",
        tpl,
    )

    # 变量替换
    result = re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: str(vars.get(m.group(1), "")),
        result,
    )

    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result
