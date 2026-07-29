#!/usr/bin/env python3
"""
PrePrompt Bridge 测试
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from preprompt import handler

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
        raise AssertionError(f"{msg or ''} expected {b!r}, got {a!r}")


def assert_in(a, b, msg=""):
    if a not in b:
        raise AssertionError(f"{msg or ''} {a!r} not in {b!r}")


def assert_not_in(a, b, msg=""):
    if a in b:
        raise AssertionError(f"{msg or ''} {a!r} should not be in {b!r}")


# ── 基础 ──

test("空输入", lambda: (
    assert_eq(handler({})["meta"]["has_question"], False)
))

test("只有问题", lambda: (
    assert_in("你好", handler({"question": "你好"})["prompt"]),
    assert_eq(handler({"question": "你好"})["meta"]["has_question"], True),
    assert_eq(handler({"question": "你好"})["meta"]["history_rounds"], 0),
))

test("问题 + 历史", lambda: (
    assert_in("继续", handler({"question": "继续", "his": [
        {"query": "你是谁", "answer": "AI助手"},
    ]})["prompt"]),
    assert_in("你是谁", handler({"question": "继续", "his": [
        {"query": "你是谁", "answer": "AI助手"},
    ]})["prompt"]),
))

# ── 拼写兼容 ──

test("quesion 拼写兼容", lambda: (
    assert_in("兼容测试", handler({"quesion": "兼容测试"})["prompt"])
))

# ── 系统指令 ──

test("系统指令", lambda:
    assert_in("文案专家", handler({"question": "写文案", "sys_prompt": "你是文案专家"})["prompt"])
)

# ── 多语言 ──

test("英文模板", lambda: (
    assert_in("User question:", handler({"question": "hi", "lang": "en"})["prompt"])
))

test("日文模板", lambda: (
    assert_in("ユーザーの質問：", handler({"question": "こんにちは", "lang": "ja"})["prompt"])
))

# ── 模式 ──

test("deep 模式带推理引导", lambda: (
    assert_in("逐步推理", handler({"question": "分析一下", "mode": "deep"})["prompt"])
))

test("deep 模式英文引导", lambda: (
    assert_in("step by step", handler({"question": "analyze", "mode": "deep", "lang": "en"})["prompt"])
))

test("fast 模式", lambda: (
    assert_in("直接给出答案", handler({"question": "hi", "mode": "fast"})["prompt"])
))

test("creative 模式", lambda: (
    assert_in("创造力", handler({"question": "讲故事", "mode": "creative"})["prompt"])
))

# ── 角色 ──

test("角色 code_review", lambda: (
    assert_in("代码审查", handler({"question": "review this", "role": "code_review"})["prompt"])
))

test("角色 translator 英文", lambda: (
    assert_in("professional translator", handler({
        "question": "translate", "role": "translator", "lang": "en"
    })["prompt"])
))

test("角色 teacher", lambda: (
    assert_in("耐心", handler({"question": "教教我", "role": "teacher"})["prompt"])
))

# ── 安全模式 ──

test("safe_mode 过滤", lambda: (
    assert_not_in("13800138000", handler({
        "question": "手机13800138000",
        "safe_mode": True,
    })["prompt"]),
    assert_in("[手机号]", handler({
        "question": "手机13800138000",
        "safe_mode": True,
    })["prompt"]),
))

test("safe_mode 身份证 + 手机号", lambda: (
    assert_in("[身份证]", handler({
        "question": "身份证110101199001011234",
        "safe_mode": True,
    })["prompt"]),
    assert_in("[手机号]", handler({
        "question": "手机13800138000身份证110101199001011234",
        "safe_mode": True,
    })["prompt"]),
))

# ── history 控制 ──

test("max_history 限制", lambda: (
    assert_eq(handler({
        "question": "x",
        "his": [{"query": f"q{i}", "answer": f"a{i}"} for i in range(50)],
        "max_history": 3,
    })["meta"]["history_rounds"], 3)
))

test("大量历史默认 20", lambda: (
    assert_eq(handler({
        "question": "x",
        "his": [{"query": f"q{i}", "answer": f"a{i}"} for i in range(100)],
    })["meta"]["history_rounds"], 20)
))

# ── 自定义模板 ──

test("自定义模板", lambda: (
    assert_eq(handler({
        "question": "test",
        "template": "Q: {{question}}",
    })["prompt"], "Q: test")
))

test("自定义模板条件", lambda: (
    assert_eq(
        handler({"question": "hi", "template": "{% if sys_prompt %}{{sys_prompt}}{% endif %}{{question}}"})["prompt"],
        "hi"
    ),
    assert_eq(
        handler({"question": "hi", "sys_prompt": "你是", "template": "{% if sys_prompt %}{{sys_prompt}}{% endif %}{{question}}"})["prompt"],
        "你是hi"
    ),
))

# ── 上下文 ──

test("额外上下文", lambda: (
    assert_in("辣的食物", handler({
        "question": "推荐",
        "context": {"用户偏好": "辣的食物", "预算": "50元"},
    })["prompt"])
))

# ── 风格规则 ──

test("风格规则", lambda: (
    assert_in("口语化", handler({
        "question": "hi",
        "style_rules": "用口语化表达",
    })["prompt"])
))

# ── meta ──

def _check_meta():
    m = handler({
        "question": "a",
        "his": [{"query": "q", "answer": "a"}],
        "sys_prompt": "s",
        "context": {"x": "y"},
        "safe_mode": True,
        "mode": "deep",
        "lang": "en",
        "role": "translator",
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

test("meta 字段完整", _check_meta)

# ── 边界 ──

test("his 非列表", lambda:
    assert_eq(handler({"question": "x", "his": "not a list"})["meta"]["history_rounds"], 0)
)

test("空字符串问题", lambda:
    assert_eq(handler({"question": ""})["meta"]["has_question"], False)
)


print(f"\n{'─' * 40}")
print(f"{passed} passed, {failed} failed{' ❌' if failed else ' ✅'}")
sys.exit(1 if failed else 0)
