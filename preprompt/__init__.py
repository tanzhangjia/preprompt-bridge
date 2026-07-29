"""
PrePrompt Bridge — 工作流 Prompt 预处理器

在工作流引擎中把杂乱输入整理成给 LLM 的结构化 prompt，
减少多语言/多模式/多角色场景下的重复配置。

纯 Python 3，零外部依赖。
"""
import re

# ── 预置角色 prompt ──
ROLE_PROMPTS = {
    "assistant": {
        "zh": "你是一个智能助手，友好、准确、乐于助人。",
        "en": "You are a helpful, friendly, and accurate assistant.",
        "ja": "あなたは親切で正確なアシスタントです。",
    },
    "code_review": {
        "zh": "你是一个资深代码审查专家。请关注：安全性、性能、可维护性、代码规范。",
        "en": "You are a senior code reviewer. Focus on: security, performance, maintainability, code style.",
    },
    "translator": {
        "zh": "你是一个专业翻译。保持原文语气和风格，术语准确，语句通顺。直接输出译文，不要解释。",
        "en": "You are a professional translator. Preserve tone and style, use accurate terminology, output translation only.",
    },
    "writer": {
        "zh": "你是一个专业写手。文笔优美，逻辑清晰，符合中文表达习惯。",
        "en": "You are a professional writer. Clear logic, elegant prose, engaging style.",
    },
    "teacher": {
        "zh": "你是一个耐心细致的老师。用通俗易懂的方式解释，多举例子，适当提问引导思考。",
        "en": "You are a patient teacher. Explain in simple terms, use examples, ask guiding questions.",
    },
}

# ── 深度思考引导 ──
DEEP_THINK_PROMPT = {
    "zh": "\n【请逐步推理】先分析问题，拆解关键点，再给出结论。",
    "en": "\n【Think step by step】Analyze the problem, break down key points, then conclude.",
    "ja": "\n【段階的に推論】問題を分析し、重要なポイントを分解してから結論を出してください。",
}

FAST_MODE_MARKER = {
    "zh": "\n请直接给出答案，不需要推理过程。",
    "en": "\nGive the answer directly, no reasoning needed.",
}

CREATIVE_MODE_MARKER = {
    "zh": "\n请发挥创造力，给出有想象力的回答。",
    "en": "\nBe creative and imaginative in your response.",
}

# ── 敏感信息正则（先长后短，不依赖 \b 边界，兼容中文语境） ──
SENSITIVE_PATTERNS = [
    (r"(?<![\d])\d{17}[\dXx](?![\d])", "[身份证]"),
    (r"(?<![\d])1[3-9]\d{9}(?![\d])", "[手机号]"),
    (r"[\w.-]+@[\w.-]+\.\w{2,4}", "[邮箱]"),
]


def handler(params: dict) -> dict:
    """
    主入口。

    Args:
        params: 见 README 参数说明。

    Returns:
        {"prompt": str, "meta": dict}
    """
    # ── 默认值 ──
    safe_mode = bool(params.get("safe_mode", False))
    max_history = max(0, int(params.get("max_history", 20)))
    trim_history = bool(params.get("trim_history", False))
    lang = params.get("lang", "zh")
    mode = params.get("mode", "normal")
    role = params.get("role", "")
    style_rules = params.get("style_rules", "")

    # ── 提取问题（兼容拼写错误） ──
    raw_question = (
        params.get("question")
        or params.get("quesion")
        or params.get("Q")
        or ""
    ).strip()
    question = _clean_text(raw_question, safe_mode)

    # ── 组装历史对话 ──
    his_lines = []
    his_arr = params.get("his", [])
    if not isinstance(his_arr, list):
        his_arr = []
    used_history_count = 0

    # 取最新 max_history 轮
    for item in his_arr[-max_history:]:
        if not isinstance(item, dict):
            continue
        used_history_count += 1
        query = _clean_text(str(item.get("query") or ""), safe_mode)
        answer = _clean_text(str(item.get("answer") or ""), safe_mode)
        files = item.get("files")
        if isinstance(files, list):
            file_names = [f.get("name", "") for f in files if isinstance(f, dict)]
            file_str = "、".join(filter(None, file_names))
        else:
            file_str = ""

        his_lines.append(f"用户：{query}")
        if file_str:
            his_lines.append(f"（附带文件：{file_str}）")
        his_lines.append(f"AI：{answer}")

    history_str = "\n".join(his_lines)

    # ── 拼装系统指令 ──
    sys_prompt_parts = []

    # 角色 prompt
    if role and role in ROLE_PROMPTS:
        role_text = ROLE_PROMPTS[role].get(lang) or ROLE_PROMPTS[role].get(
            "zh", ""
        )
        if role_text:
            sys_prompt_parts.append(role_text)

    # 用户自定义 sys_prompt
    if params.get("sys_prompt"):
        sys_prompt_parts.append(
            _clean_text(str(params["sys_prompt"]), safe_mode)
        )

    # 风格规则
    if style_rules:
        sys_prompt_parts.append(style_rules)

    sys_prompt = "\n".join(sys_prompt_parts)

    # ── 模式注入 ──
    mode_markers = {
        "deep": DEEP_THINK_PROMPT,
        "fast": FAST_MODE_MARKER,
        "creative": CREATIVE_MODE_MARKER,
    }

    mode_suffix = ""
    if mode in mode_markers:
        marker_map = mode_markers[mode]
        mode_suffix = marker_map.get(lang) or marker_map.get("zh", "")

    # ── 拼装上下文 ──
    context_str = ""
    context = params.get("context")
    if isinstance(context, dict):
        pairs = []
        for k, v in context.items():
            if v is not None:
                pairs.append(f"{k}：{_clean_text(str(v), safe_mode)}")
        context_str = "\n".join(pairs)

    # ── 渲染模板 ──
    template = params.get("template")
    if template:
        prompt = _render_template(template, {
            "question": question,
            "history": history_str,
            "sys_prompt": sys_prompt,
            "context": context_str,
            "his_count": str(used_history_count),
        })
    else:
        prompt = _default_template(
            question=question,
            history=history_str,
            sys_prompt=sys_prompt,
            context=context_str,
            mode_suffix=mode_suffix,
            lang=lang,
        )

    # ── meta ──
    meta = {
        "has_question": bool(question),
        "history_rounds": used_history_count,
        "has_sys_prompt": bool(sys_prompt),
        "has_context": bool(context_str),
        "mode": mode,
        "lang": lang,
        "role": role,
        "safe_mode": safe_mode,
        "prompt_length": len(prompt),
    }

    return {"prompt": prompt, "meta": meta}


def _default_template(
    question: str,
    history: str,
    sys_prompt: str,
    context: str,
    mode_suffix: str,
    lang: str = "zh",
) -> str:
    """默认模板"""
    parts = []

    if sys_prompt:
        parts.append(sys_prompt)
        parts.append("")

    if history:
        history_label = "历史对话：" if lang == "zh" else "Conversation history:"
        if lang == "ja":
            history_label = "会話履歴："
        parts.append(history_label)
        parts.append(history)
        parts.append("")

    if context:
        context_label = "额外信息：" if lang == "zh" else "Additional context:"
        if lang == "ja":
            context_label = "追加情報："
        parts.append(context_label)
        parts.append(context)
        parts.append("")

    question_label = "用户问题：" if lang == "zh" else "User question:"
    if lang == "ja":
        question_label = "ユーザーの質問："
    parts.append(f"{question_label}{question}")

    if mode_suffix:
        parts.append(mode_suffix)

    return "\n".join(parts).strip()


def _render_template(tpl: str, vars: dict) -> str:
    """简易模板渲染，支持 {{key}} 和 {% if key %}...{% endif %}"""
    # 条件块
    result = re.sub(
        r"\{% if (\w+) %\}([\s\S]*?)\{% endif %\}",
        lambda m: m.group(2) if vars.get(m.group(1)) else "",
        tpl,
    )

    # 变量替换
    result = re.sub(r"\{\{(\w+)\}\}", lambda m: str(vars.get(m.group(1), "")), result)

    # 清理多余空行
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


def _clean_text(text: str, safe: bool) -> str:
    """文本清洗"""
    if not isinstance(text, str):
        return ""
    if not safe:
        return text

    t = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        t = re.sub(pattern, replacement, t)
    return t
