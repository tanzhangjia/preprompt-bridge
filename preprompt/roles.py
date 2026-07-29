"""
角色系统 — 预置角色 prompt

职责：
- 提供预置角色 prompt（多语言）
- 支持外部注册自定义角色

角色 prompt 是插件式的：
  roles.register("qa_expert", {"zh": "你是一个QA专家", "en": "You are a QA expert"})
"""

# ── 全局角色注册表 ──
_ROLE_REGISTRY = {}

# ── 预置角色 ──
_BUILTIN = {
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

_ROLE_REGISTRY.update(_BUILTIN)


def register(name: str, prompts: dict):
    """注册自定义角色。

    Args:
        name: 角色名
        prompts: {lang_code: prompt_text, ...}
    """
    _ROLE_REGISTRY[name] = prompts


def get(name: str, lang: str = "zh") -> str:
    """获取角色的指定语言 prompt，fallback 到第一个可用语言"""
    if not name:
        return ""
    entry = _ROLE_REGISTRY.get(name)
    if not entry:
        return ""
    text = entry.get(lang)
    if text:
        return text
    # fallback 到任何可用语言
    for v in entry.values():
        return v
    return ""


def list_roles() -> dict:
    """列出所有已注册的角色"""
    return dict(_ROLE_REGISTRY)
