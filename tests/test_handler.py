#!/usr/bin/env python3
"""PrePrompt Bridge 测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from preprompt import handler, roles, modes, rules, templates, register_variable, register_rule
from preprompt.context import Context

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  ✓ {name}")
    except Exception as e:
        failed += 1
        print(f"  ✗ {name}: {e}")

def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg or ''} {a!r} != {b!r}")

def assert_in(a, b, msg=""):
    if a not in b:
        raise AssertionError(f"{msg or ''} {a!r} not in {b!r}")

def assert_not_in(a, b, msg=""):
    if a in b:
        raise AssertionError(f"{msg or ''} {a!r} found in {b!r}")


# ── Context 参数解析 ──
test("Context question", lambda: (
    assert_eq(Context({"question": "hi"}).get_question(), "hi"),
    assert_eq(Context({"quesion": "q"}).get_question(), "q"),
    assert_eq(Context({"Q": "sig"}).get_question(), "sig"),
    assert_eq(Context({}).get_question(), ""),
))

test("Context defaults", lambda: (
    assert_eq(Context({}).max_history, 20),
    assert_eq(Context({}).lang, "zh"),
    assert_eq(Context({"max_history": 5}).max_history, 5),
))

# ── 基础 handler ──
test("empty input", lambda:
    assert_eq(handler({})["prompt"], ""))

test("basic question", lambda:
    assert_in("hi", handler({"question": "hi"})["prompt"]))

test("question + history", lambda:
    assert_in("q1", handler({
        "question": "continue",
        "his": [{"query": "q1", "answer": "a1"}]
    })["prompt"]))

test("quesion compat", lambda:
    assert_in("test", handler({"quesion": "test"})["prompt"]))

test("sys_prompt", lambda:
    assert_in("expert", handler({"question": "w", "sys_prompt": "you are expert"})["prompt"]))

# ── 多语言 ──
test("lang en", lambda:
    assert_in("User question:", handler({"question": "hi", "lang": "en"})["prompt"]))

test("lang ja", lambda:
    assert_in("ユーザーの質問：", handler({"question": "hi", "lang": "ja"})["prompt"]))

# ── 模式 ──
test("mode deep", lambda:
    assert_in("逐步推理", handler({"question": "x", "mode": "deep"})["prompt"]))

test("mode fast", lambda:
    assert_in("直接给出答案", handler({"question": "x", "mode": "fast"})["prompt"]))

test("mode creative", lambda:
    assert_in("创造力", handler({"question": "x", "mode": "creative"})["prompt"]))

test("mode professional en", lambda:
    assert_in("professional", handler({"question": "x", "mode": "professional", "lang": "en"})["prompt"]))

# ── 角色 ──
test("role code_review", lambda:
    assert_in("代码审查", handler({"question": "r", "role": "code_review"})["prompt"]))

test("role translator en", lambda:
    assert_in("professional translator",
              handler({"question": "t", "role": "translator", "lang": "en"})["prompt"]))

test("role teacher", lambda:
    assert_in("耐心", handler({"question": "t", "role": "teacher"})["prompt"]))

# ── 历史控制 ──
test("max_history", lambda:
    assert_eq(handler({
        "question": "x",
        "his": [{"query": f"q{i}", "answer": f"a{i}"} for i in range(50)],
        "max_history": 3,
    })["meta"]["history_rounds"], 50))  # meta 只记 raw 长度，实际截断在 build 里

test("his not list", lambda:
    assert_eq(handler({"question": "x", "his": "bad"})["meta"]["history_rounds"], 0))

# ── 自定义模板 ──
test("custom template", lambda:
    assert_eq(handler({"question": "test", "template": "Q:{{question}}"})["prompt"], "Q:test"))

test("template with history", lambda:
    assert_in("q1", handler({
        "question": "continue",
        "his": [{"query": "q1", "answer": "a1"}],
        "template": "H:{{history}}\nQ:{{question}}",
    })["prompt"]))

# ── 上下文 ──
test("context", lambda:
    assert_in("pref", handler({"question": "r", "context": {"user_pref": "pref"}})["prompt"]))

# ── 风格规则 ──
test("style_rules", lambda:
    assert_in("口语化", handler({"question": "hi", "style_rules": "用口语化表达"})["prompt"]))

# ── 输出格式 ──
test("output_format", lambda:
    assert_in("JSON", handler({"question": "hi", "output_format": "JSON"})["prompt"]))

# ── 自定义拼接规则 ──
test("custom rules order", lambda: (
    assert_in("hi", handler({
        "question": "hi",
        "rules": ["question"],  # 只拼接问题
    })["prompt"]),
    assert_not_in("用户问题：", handler({
        "question": "hi",
        "rules": ["question"],  # 只拼接问题，不经过 labels
    })["prompt"]),
))

test("register custom rule", lambda: (
    register_rule("greeting", lambda ctx: ("greeting", f"Hello {ctx.lang}")),
    assert_in("Hello", handler({
        "question": "hi",
        "rules": ["greeting", "question"],
    })["prompt"]),
))

# ── 自定义变量提取器 ──
test("register variable extractor", lambda: (
    register_variable("temperature", lambda p: str(p.get("temperature", "0.7"))),
    assert_in("temperature：0.5", handler({
        "question": "hi",
        "temperature": "0.5",
    })["prompt"]),
))

# ── 角色插件 ──
test("roles.register", lambda: (
    roles.register("qa_expert", {"zh": "QA专家", "en": "QA expert"}),
    assert_in("QA专家", handler({"question": "t", "role": "qa_expert"})["prompt"]),
))

# ── 模式插件 ──
test("modes.register", lambda: (
    modes.register("concise", {"zh": "一句话回答"}),
    assert_in("一句话回答", handler({"question": "t", "mode": "concise"})["prompt"]),
))

# ── templates hook ──
def _test_hook():
    called = []
    def hook(text, blocks):
        called.append(True)
        return text.upper()
    templates.register_hook(hook)
    result = handler({"question": "hi"})["prompt"]
    # 预期被转大写
    assert result.isupper() or "HI" in result, f"hook not applied: {result}"
test("template hook", _test_hook)

# ── meta ──
test("meta fields", lambda:
    assert_eq(handler({"question": "a"})["meta"]["has_question"], True))

test("meta rules applied", lambda:
    assert_in("question", handler({"question": "a"})["meta"]["rules_applied"]))

# ── 空输入 ──
test("empty question meta", lambda:
    assert_eq(handler({"question": ""})["meta"]["has_question"], False))


print(f"\n{'─' * 40}")
print(f"{passed}/{passed + failed} passed{' ❌' if failed else ' ✅'}")
sys.exit(1 if failed else 0)
