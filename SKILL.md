---
name: preprompt-bridge
description: "工作流中的 Prompt 预处理器 — 把问题、历史、角色、模式、上下文拼成结构化 prompt，减少 LLM 节点配置重复。纯 Python 3，零依赖，插件架构。"
metadata:
  openclaw:
    emoji: 🔗
    requires:
      bins: [python3]
---

# 🔗 PrePrompt Bridge — OpenClaw Skill

在工作流引擎（n8n / Dify / OpenClaw / 自建）里调 LLM 时，把杂乱的输入整理成结构化 prompt。

**纯 Python 3，零外部依赖。直接用在 AI Agent 中作为 prompt 预处理步骤。**

## 使用方式

作为 Python 库调用：

```python
from preprompt import handler

result = handler({
    "question": "帮我写个简介",
    "his": [{"query": "你是谁", "answer": "我是 AI 助手"}],
    "sys_prompt": "你是一个专业文案写手",
    "lang": "zh",
    "mode": "deep",
    "role": "writer",
})

# 把 result["prompt"] 传给 LLM
```

## 参数

| 参数 | 说明 |
|------|------|
| `question` | 用户当前问题 |
| `his` | 历史对话 [{query, answer}] |
| `sys_prompt` | 系统指令 |
| `lang` | 语言：`zh` / `en` / `ja` |
| `mode` | 模式：`deep` / `fast` / `creative` |
| `role` | 角色：`code_review` / `translator` / `writer` / `teacher` |
| `context` | 额外上下文键值对 |
| `template` | 自定义模板 |
| `rules` | 自定义拼接顺序 |
| `max_history` | 最大历史轮数 |

返回 `{"prompt": str, "meta": dict}`。

## 插件注册

```python
from preprompt import roles, modes, register_rule, register_variable

roles.register("qa_expert", {"zh": "你是QA专家", "en": "You are a QA expert"})
modes.register("concise", {"zh": "用一句话回答"})
register_rule("weather", lambda ctx: ("weather", f"天气：{ctx._raw.get('weather')}"))
register_variable("temperature", lambda p: str(p.get("temperature", "0.7")))
```

## 作为 Dify 插件

`dify/` 目录包含了完整的 Dify Plugin 定义，可在 Dify 中直接安装使用。

## 链接

- GitHub: https://github.com/tanzhangjia/preprompt-bridge
- 核心库文档: `preprompt/` 各模块
- Dify 插件: `dify/manifest.yaml`
