# PrePrompt Bridge

工作流中的 Prompt 预处理器。

## 解决什么场景

在工作流引擎（n8n / Dify / Langflow / ComfyUI / 自建服务…）里调 LLM 时，经常需要根据同一个场景做多份配置：

| 场景 | 问题 |
|------|------|
| **多语言** | 中文用户一个 prompt，英文用户另一个 prompt，模板几乎一样只是语言不同 |
| **深度思考 vs 普通** | 需要深度推理时 prompt 要多给思维链引导，普通问答时又嫌啰嗦 |
| **角色切换** | 同一套接口，有时当客服、有时当翻译、有时当代码审查 |
| **上下文历史** | 每个工作流节点都在手拼 `{{history}}`，代码重复 |
| **参数拼装** | LLM 节点里塞一大段 `{{sys_prompt}}\n\n历史：{{history}}\n\n问题：{{question}}`，维护困难 |

**PrePrompt Bridge 就是代替你做这件事的：** 在工作流里放一个代码节点，把原始输入丢进去，拿到整理好的 prompt 再给 LLM。

## 快速开始

```python
from preprompt import handler

result = handler({
    "question": "帮我写个简介",
    "his": [
        {"query": "你是谁", "answer": "我是 AI 助手"},
    ],
    "sys_prompt": "你是一个专业文案写手",
})

print(result["prompt"])
```

## 安装

```bash
pip install preprompt-bridge
# 或直接拷贝 preprompt/handler.py 到项目里
```

## 核心能力

### 1. 多语言自适应

```python
handler({
    "question": "Write an introduction",
    "lang": "en",   # 自动注入英文模板
    "sys_prompt": "You are a professional copywriter",
})
```

### 2. 深度思考模式

```python
handler({
    "question": "推演核战争后的全球供应链变化",
    "mode": "deep",  # 自动加上思维链引导
})
# vs
handler({
    "question": "今天天气怎么样",
    "mode": "fast",  # 简洁 prompt，省 token
})
```

### 3. 角色切换

```python
handler({
    "question": "这段代码有 bug 吗",
    "role": "code_review",
})
# 自动注入：你是一个资深代码审查专家，关注安全性、性能、可维护性
```

### 4. 历史管理

```python
handler({
    "question": "继续",
    "his": history_array,  # 自动拼接、控制轮数
    "max_history": 10,     # 只保留最近 10 轮
})
```

## API

### `handler(params) -> dict`

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `question` | str | `""` | 用户当前问题 |
| `quesion` | str | — | 兼容拼写错误 |
| `his` | list | `[]` | 历史对话 `[{query, answer}]` |
| `sys_prompt` | str | `""` | 系统指令 |
| `lang` | str | `"zh"` | 语言：`zh` / `en` / `ja` / `auto` |
| `mode` | str | `"normal"` | 模式：`normal` / `deep` / `fast` / `creative` |
| `role` | str | `""` | 预置角色：`assistant` / `code_review` / `translator` / `writer` / `teacher` |
| `context` | dict | `{}` | 额外上下文键值对 |
| `template` | str | — | 自定义模板 |
| `max_history` | int | `20` | 最大历史轮数 |
| `trim_history` | bool | `False` | 是否对历史做 token 估算截断 |
| `safe_mode` | bool | `False` | 是否过滤敏感信息 |
| `style_rules` | str | `""` | 补充风格指令（如"用口语化表达"） |

返回 `{"prompt": str, "meta": dict}`。

## 在工作流中使用

### n8n

Code 节点：

```python
from preprompt import handler
return handler({
    "question": $json.input.question,
    "his": $json.input.history,
    "lang": $json.input.lang or "zh",
})
```

### Dify / Langflow

复制 `preprompt/handler.py` 到代码节点中，用 `handler(your_input)`。

### 自建服务

```python
from flask import Flask, request, jsonify
from preprompt import handler

app = Flask(__name__)

@app.route("/preprompt", methods=["POST"])
def preprompt():
    result = handler(request.json)
    return jsonify(result)
```

## 完整的场景对比

### 改造前（工作流里直接拼）

你需要在每个 LLM 节点里写：

```
{% if lang == "zh" %}你是一个助手{% else %}You are an assistant{% endif %}
历史：{{history}}
问题：{{question}}
{% if mode == "deep" %}请逐步推理{% endif %}
```

4 个 LLM 节点就要写 4 次，改模板要改 4 个地方。

### 改造后（一个代码节点搞定）

所有参数集中到一个节点：

```python
from preprompt import handler
result = handler({
    "question": node_input,
    "his": node_history,
    "lang": node_lang,    # 来自配置
    "mode": node_mode,    # 来自配置
    "role": node_role,    # 来自配置
})
# 把 result["prompt"] 传给 LLM 节点作为唯一输入
```

LLM 节点只需要 `{{prompt}}` 一个变量，切换语言/模式/角色只需改参数，不碰 prompt 模板。

## 许可证

MIT
