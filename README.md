# PrePrompt Bridge

工作流中的 Prompt 预处理器。

**纯 Python 3，零外部依赖。插件架构，每个模块可独立扩展。**

## 解决什么场景

在工作流引擎里调 LLM，一个场景常常要配好几个 LLM 节点：

| 场景 | 问题 |
|------|------|
| **多语言** | 中文用户一套 prompt，英文用户另一套，模板一样只是语言不同 |
| **深度思考 vs 快速回复** | deep 模式要多给推理引导，fast 模式要简洁，本质上同一套逻辑 |
| **角色切换** | 同一接口，有时当客服、有时当翻译、有时当代码审查 |
| **重复配置** | 每个 LLM 节点都在手拼 `历史：{{history}}\n问题：{{question}}` |
| **参数传递** | prompt 里塞一大堆变量，改一个模板要改 N 个节点 |

**PrePrompt Bridge 把这一切集中到一个地方：**

```
原始输入 → PrePrompt Bridge → 整理好的 prompt → LLM 节点（只收一个变量）
```

## 快速开始

```bash
pip install preprompt-bridge
# 或直接拷贝 preprompt/ 目录
```

```python
from preprompt import handler

result = handler({
    "question": "帮我写个简介",
    "his": [{"query": "你是谁", "answer": "我是助手"}],
    "sys_prompt": "你是专业文案写手",
    "lang": "zh",
    "mode": "normal",
    "role": "writer",
})

print(result["prompt"])
```

## API

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `question` | str | `""` | 用户当前问题 |
| `quesion` | str | — | 兼容拼写错误 |
| `his` | list | `[]` | 历史 `[{query, answer}]` |
| `sys_prompt` | str | `""` | 系统指令 |
| `lang` | str | `"zh"` | 语言：`zh` / `en` / `ja` |
| `mode` | str | `""` | 模式：`deep` / `fast` / `creative` / `professional` / `simple` |
| `role` | str | `""` | 角色：`assistant` / `code_review` / `translator` / `writer` / `teacher` |
| `context` | dict | `{}` | 额外上下文键值对 |
| `template` | str | — | 自定义模板 |
| `max_history` | int | `20` | 最大历史轮数 |
| `trim_history` | bool | `False` | 字符数截断 |
| `safe_mode` | bool | `False` | 敏感信息过滤 |
| `style_rules` | str | `""` | 风格指令 |
| `output_format` | str | `""` | 输出格式要求 |
| `filter_rules` | list/str | — | 自定义过滤规则 |

返回 `{"prompt": str, "meta": dict}`。

## 插件系统

每个模块都是一个独立注册表，支持运行时扩展。

### 自定义角色

```python
from preprompt import roles

roles.register("qa_expert", {
    "zh": "你是一个QA专家",
    "en": "You are a QA expert",
})

# 然后直接用
handler({"question": "测这个", "role": "qa_expert"})
```

### 自定义模式

```python
from preprompt import modes

modes.register("concise", {
    "zh": "\n请用一句话回答",
    "en": "\nAnswer in one sentence",
})
```

### 自定义过滤规则

```python
from preprompt import filters

filters.register_rule("no_numbers", lambda ctx: "不要输出数字，用文字表示。")

handler({
    "question": "hi",
    "filter_rules": "no_numbers",
})
```

### 自定义模板

```python
handler({
    "question": "hi",
    "template": "系统：{{sys_prompt}}\n历史：{{history}}\n问题：{{question}}",
})
```

模板语法：
- `{{question}}`、`{{history}}`、`{{sys_prompt}}`、`{{context}}`、`{{mode_suffix}}`、`{{filter_tags}}`
- `{% if history %}...{% endif %}` 条件块

## 在工作流中使用

复制 `preprompt/` 目录到项目中，或 `pip install` 后：

```python
# n8n Code 节点
from preprompt import handler
return handler({
    "question": $json.input.q,
    "lang": $json.input.lang or "zh",
    "mode": $json.input.mode or "normal",
})
```

## 架构

```
preprompt/
├── __init__.py   # 导出
├── handler.py    # 主入口，协调各模块
├── context.py    # 参数解析与标准化
├── history.py    # 历史对话组装
├── roles.py      # 角色系统（插件注册表）
├── modes.py      # 模式系统（插件注册表）
├── filters.py    # 过滤规则（插件注册表）
├── templates.py  # 模板渲染
└── sanitize.py   # 敏感信息清洗
```

## 许可证

MIT
