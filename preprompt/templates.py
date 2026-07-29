"""
模板系统 — prompt 模板渲染

职责：
- 默认模板（多语言）
- 自定义模板渲染（{{var}}、{% if %}）
- 支持外部提供模板函数
"""

# ── 全局模板钩子 ──
_TEMPLATE_HOOKS = []


def register_hook(fn):
    """注册模板后期处理函数。

    Args:
        fn: callable(prompt: str, ctx: dict) -> str
            ctx 包含渲染后的全部变量
    """
    _TEMPLATE_HOOKS.append(fn)


def default(lang: str = "zh") -> str:
    """获取默认模板（多语言分段结构）"""
    labels = {
        "zh": {
            "history": "历史对话：",
            "context": "额外信息：",
            "question": "用户问题：",
        },
        "en": {
            "history": "Conversation history:",
            "context": "Additional context:",
            "question": "User question:",
        },
        "ja": {
            "history": "会話履歴：",
            "context": "追加情報：",
            "question": "ユーザーの質問：",
        },
    }
    ls = labels.get(lang, labels["zh"])

    parts = []
    parts.append("{{sys_prompt}}")
    parts.append("")
    parts.append("{% if history %}")
    parts.append(ls["history"])
    parts.append("{{history}}")
    parts.append("")
    parts.append("{% endif %}")
    parts.append("{% if context %}")
    parts.append(ls["context"])
    parts.append("{{context}}")
    parts.append("")
    parts.append("{% endif %}")
    parts.append("{% if filter_tags %}")
    parts.append("{{filter_tags}}")
    parts.append("")
    parts.append("{% endif %}")
    parts.append("{% if question %}")
    parts.append(f"{ls['question']}{{{{question}}}}")
    parts.append("{% endif %}")
    parts.append("{{mode_suffix}}")

    return "\n".join(parts)


def render(
    template: str = None,
    question: str = "",
    history: str = "",
    sys_prompt: str = "",
    context: str = "",
    mode_suffix: str = "",
    lang: str = "zh",
    filter_tags: str = "",
    his_count: str = "0",
) -> str:
    """渲染模板"""
    import re

    tpl = template if template else default(lang)

    vars = {
        "question": question,
        "history": history,
        "sys_prompt": sys_prompt,
        "context": context,
        "mode_suffix": mode_suffix,
        "filter_tags": filter_tags,
        "his_count": his_count,
    }

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

    # 清理多余空行
    result = re.sub(r"\n{3,}", "\n\n", result).strip()

    # 执行模板钩子
    for hook in _TEMPLATE_HOOKS:
        result = hook(result, vars)

    return result
