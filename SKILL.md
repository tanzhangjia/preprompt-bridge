---
name: preprompt-bridge
description: "把 prompt 从「每节点一坨」变成「1 个 LLM 节点 + N 个可插拔模块」—— 角色、模式、多语言、拼接规则全部可注册扩展，减少 LLM 节点配置重复。"
metadata:
  openclaw:
    emoji: 🔗
    requires:
      bins: [python3]
---

# 🔗 PrePrompt Bridge — OpenClaw Skill

把 prompt 拆成独立模块（问题、历史、角色、模式、上下文、输出格式…），每个模块是可插拔的规则。  
1 个 LLM 节点 + 改参数 = 无限场景，不动模板。

**传统做法：** 5 个 LLM 节点要复制 5 遍 prompt 模板，加英文版再翻倍。  
**这个项目：** 1 个 LLM 节点 + 参数 = 所有场景。

## 使用方式

```python
from preprompt import handler

# 同一套模板，不同参数 = 不同场景
handler({"question": "...", "lang": "zh", "mode": "deep", "role": "writer"})
handler({"question": "...", "lang": "en", "mode": "fast", "role": "translator"})
```

## 可插拔的模块

```python
from preprompt import roles, modes, register_rule, register_variable

roles.register("qa_expert", {"zh": "你是QA专家", "en": "You are a QA expert"})
modes.register("concise", {"zh": "用一句话回答"})
register_rule("weather", lambda ctx: ("weather", f"天气：{ctx._raw.get('weather')}"))
register_variable("temperature", lambda p: str(p.get("temperature", "0.7")))
```

## 参数

| 参数 | 说明 |
|------|------|
| `question` / `quesion` | 用户问题（兼容拼写） |
| `his` | 历史对话 [{query, answer}] |
| `sys_prompt` | 系统指令 |
| `lang` | 语言 `zh` / `en` / `ja` |
| `mode` | 模式 `deep` / `fast` / `creative` |
| `role` | 角色 `code_review` / `translator` / `writer` / `teacher` |
| `context` | 额外上下文 |
| `template` | 自定义模板 |
| `rules` | 自定义拼接顺序 |
| `max_history` | 最大历史轮数 |

作为 Dify 插件：`dify/` 目录包含完整 Plugin 定义。
