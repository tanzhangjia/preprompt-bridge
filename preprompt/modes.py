"""
模式系统 — deep / fast / creative 等模式引导

职责：
- 预置模式引导文本（多语言）
- 支持外部注册自定义模式
- 支持用户自定义模式

模式是插件式的：
  modes.register("concise", {"zh": "\n请用一句话回答", "en": "\nAnswer in one sentence"})
"""

_MODE_REGISTRY = {}

_BUILTIN = {
    "deep": {
        "zh": "\n【请逐步推理】先分析问题，拆解关键点，再给出结论。",
        "en": "\n【Think step by step】Analyze the problem, break down key points, then conclude.",
        "ja": "\n【段階的に推論】問題を分析し、重要なポイントを分解してから結論を出してください。",
    },
    "fast": {
        "zh": "\n请直接给出答案，不需要推理过程。",
        "en": "\nGive the answer directly, no reasoning needed.",
        "ja": "\n直接回答してください。推論は不要です。",
    },
    "creative": {
        "zh": "\n请发挥创造力，给出有想象力的回答。",
        "en": "\nBe creative and imaginative in your response.",
        "ja": "\n創造性を発揮して、想像力豊かな回答をしてください。",
    },
    "professional": {
        "zh": "\n请用专业、正式的语言回答。",
        "en": "\nRespond in a professional, formal tone.",
    },
    "simple": {
        "zh": "\n请用通俗易懂的语言解释，好像我是个新手。",
        "en": "\nExplain in simple terms as if I'm a beginner.",
    },
}

_MODE_REGISTRY.update(_BUILTIN)


def register(name: str, prompts: dict):
    """注册自定义模式。

    Args:
        name: 模式名
        prompts: {lang_code: suffix_text, ...}
    """
    _MODE_REGISTRY[name] = prompts


def get_suffix(name: str, lang: str = "zh") -> str:
    """获取模式的引导后缀"""
    if not name:
        return ""
    entry = _MODE_REGISTRY.get(name)
    if not entry:
        return ""
    text = entry.get(lang)
    if text:
        return text
    for v in entry.values():
        return v
    return ""


def list_modes() -> dict:
    """列出所有模式"""
    return dict(_MODE_REGISTRY)
