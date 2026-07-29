#!/usr/bin/env python3
"""PrePrompt Bridge 测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from preprompt import handler, roles, modes, filters
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


# Context
test("Context question", lambda: (
    assert_eq(Context({"question": "hi"}).get_question(), "hi"),
    assert_eq(Context({"quesion": "q"}).get_question(), "q"),
    assert_eq(Context({"Q": "sig"}).get_question(), "sig"),
    assert_eq(Context({}).get_question(), ""),
))

test("Context defaults", lambda: (
    assert_eq(Context({}).safe_mode, False),
    assert_eq(Context({}).max_history, 20),
    assert_eq(Context({}).lang, "zh"),
))

test("Context extra", lambda: (
    assert_eq(Context({"temperature": 0.7}).extra["temperature"], 0.7),
))

# Handler
def _test_empty():
    p = handler({})["prompt"]
    assert_eq(p, "")
test("empty input", _test_empty)

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

# Multi-lang
test("lang en", lambda:
    assert_in("User question:", handler({"question": "hi", "lang": "en"})["prompt"]))

test("lang ja", lambda:
    assert_in("ユーザーの質問：", handler({"question": "hi", "lang": "ja"})["prompt"]))

# Modes
test("mode deep", lambda:
    assert_in("逐步推理", handler({"question": "x", "mode": "deep"})["prompt"]))

test("mode fast", lambda:
    assert_in("直接给出答案", handler({"question": "x", "mode": "fast"})["prompt"]))

test("mode creative", lambda:
    assert_in("创造力", handler({"question": "x", "mode": "creative"})["prompt"]))

test("mode professional en", lambda:
    assert_in("professional", handler({"question": "x", "mode": "professional", "lang": "en"})["prompt"]))

test("mode simple", lambda:
    assert_in("通俗易懂", handler({"question": "x", "mode": "simple"})["prompt"]))

# Roles
test("role code_review", lambda:
    assert_in("代码审查", handler({"question": "r", "role": "code_review"})["prompt"]))

test("role translator en", lambda:
    assert_in("professional translator",
              handler({"question": "t", "role": "translator", "lang": "en"})["prompt"]))

test("role teacher", lambda:
    assert_in("耐心", handler({"question": "t", "role": "teacher"})["prompt"]))

# Safe mode
test("safe_mode phone", lambda:
    assert_not_in("13800138000", handler({"question": "m13800138000", "safe_mode": True})["prompt"]))

test("safe_mode id + phone", lambda: (
    assert_in("[身份证]", handler({"question": "id110101199001011234", "safe_mode": True})["prompt"]),
    assert_in("[手机号]", handler({"question": "p13800138000", "safe_mode": True})["prompt"]),
))

# History control
test("max_history", lambda:
    assert_eq(handler({
        "question": "x",
        "his": [{"query": f"q{i}", "answer": f"a{i}"} for i in range(50)],
        "max_history": 3,
    })["meta"]["history_rounds"], 3))

test("default max 20", lambda:
    assert_eq(handler({
        "question": "x",
        "his": [{"query": f"q{i}", "answer": f"a{i}"} for i in range(100)],
    })["meta"]["history_rounds"], 20))

# Custom template
test("custom template", lambda:
    assert_eq(handler({"question": "test", "template": "Q:{{question}}"})["prompt"], "Q:test"))

# Context
test("additional context", lambda:
    assert_in("pref",
              handler({"question": "r", "context": {"user_pref": "pref"}})["prompt"]))

# Style rules
test("style_rules", lambda:
    assert_in("口语化", handler({"question": "hi", "style_rules": "用口语化表达"})["prompt"]))

# Output format
test("output_format", lambda:
    assert_in("JSON", handler({"question": "hi", "output_format": "JSON"})["prompt"]))

# Meta
def _meta_check():
    m = handler({
        "question": "a", "his": [{"query": "q", "answer": "a"}],
        "sys_prompt": "s", "context": {"x": "y"},
        "safe_mode": True, "mode": "deep", "lang": "en", "role": "translator",
    })["meta"]
    assert_eq(m["has_question"], True)
    assert_eq(m["history_rounds"], 1)
    assert_eq(m["has_sys_prompt"], True)
    assert_eq(m["has_context"], True)
    assert_eq(m["safe_mode"], True)
    assert_eq(m["mode"], "deep")
    assert_eq(m["lang"], "en")
    assert_eq(m["role"], "translator")
    assert isinstance(m["prompt_length"], int)
test("meta fields", _meta_check)

# Plugin: custom roles
test("roles.register", lambda: (
    roles.register("qa_expert", {"zh": "QA专家", "en": "QA expert"}),
    assert_in("QA专家", handler({"question": "t", "role": "qa_expert"})["prompt"]),
    assert_in("QA expert", handler({"question": "t", "role": "qa_expert", "lang": "en"})["prompt"]),
))

# Plugin: custom modes
test("modes.register", lambda: (
    modes.register("concise", {"zh": "一句话回答", "en": "one sentence"}),
    assert_in("一句话", handler({"question": "t", "mode": "concise"})["prompt"]),
    assert_in("one sentence", handler({"question": "t", "mode": "concise", "lang": "en"})["prompt"]),
))

# Plugin: custom filters
test("filters.register_rule", lambda: (
    filters.register_rule("no_numbers", lambda ctx: "不要输出数字"),
    assert_in("不要输出数字", handler({"question": "hi", "filter_rules": "no_numbers"})["prompt"]),
))

# Edge cases
test("his not list", lambda:
    assert_eq(handler({"question": "x", "his": "bad"})["meta"]["history_rounds"], 0))

test("empty question", lambda:
    assert_eq(handler({"question": ""})["meta"]["has_question"], False))

test("extra pass through", lambda:
    assert_eq(Context({"temperature": 0.7}).extra["temperature"], 0.7))

# Print summary
total = passed + failed
print(f"\n{'─' * 40}")
print(f"{passed}/{total} passed{' ❌' if failed else ' ✅'}")
sys.exit(1 if failed else 0)
