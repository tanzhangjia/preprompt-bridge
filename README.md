# PrePrompt Bridge

工作流中的 Prompt 预处理器。

**纯 Python 3，零外部依赖。插件架构，拼接规则和入参完全可自定义。**

## 场景

在工作流引擎里调 LLM，一个场景要配好几个 LLM 节点——多语言、深度/快速模式、不同角色，模板类似但参数不同。  
PrePrompt Bridge 把这一切集中到一个代码节点：按 `lang`、`mode`、`role` 自动拼装，切语言/模式/角色只需改参数，不碰模板。

```
原始输入 → PrePrompt Bridge → 整理好的 prompt → LLM 节点（只收一个变量）
```

## 快速开始

```bash
pip install preprompt-bridge
```

```python
from preprompt import handler

result = handler({
    "question": "帮我写个简介",
    "lang": "zh",
    "mode": "normal",
    "role": "writer",
})
```

## 核心概念：拼接规则

项目不硬编码 prompt 的拼装顺序。每个模块（系统指令、历史、上下文、问题、模式后缀）都是一个 **可插拔的规则**，由 `rules` 参数控制顺序：

```python
handler({
    "question": "hi",
    "rules": ["sys_prompt", "history", "question"],  # 只拼接这三块
})
```

默认顺序：`["sys_prompt", "history", "context", "output_format", "question", "mode_suffix", "extra_vars"]`

### 自定义规则

```python
from preprompt import register_rule

register_rule("weather_context", lambda ctx: (
    "weather_context", f"当前天气：{ctx._raw.get('weather', '未知')}"
))

handler({
    "question": "适合出门吗",
    "weather": "晴天 25°C",
    "rules": ["weather_context", "question"],
})
```

## 核心概念：自定义变量

除了预置变量外，可以注册任意自定义变量提取器：

```python
from preprompt import register_variable

register_variable("temperature", lambda params: str(params.get("temperature", "0.7")))

handler({
    "question": "写首诗",
    "temperature": "0.9",
    "template": "创作要求：创造力{{temperature}}\n问题：{{question}}",
})
```

## API

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `question` | str | `""` | 用户问题 |
| `quesion` | str | — | 兼容拼写错误 |
| `his` | list | `[]` | 历史 `[{query, answer}]` |
| `sys_prompt` | str | `""` | 系统指令 |
| `lang` | str | `"zh"` | 语言：`zh` / `en` / `ja` |
| `mode` | str | `""` | 模式：`deep` / `fast` / `creative` / `professional` / `simple` |
| `role` | str | `""` | 角色：`assistant` / `code_review` / `translator` / `writer` / `teacher` |
| `context` | dict | `{}` | 额外上下文 |
| `template` | str | — | 自定义模板（`{{question}}`、`{% if history %}`） |
| `rules` | list | — | 自定义拼接顺序 |
| `max_history` | int | `20` | 最大历史轮数 |
| `style_rules` | str | `""` | 风格指令 |
| `output_format` | str | `""` | 输出格式要求 |
| `...` | any | — | 任意自定义参数（通过 register_variable 提取） |

## 插件系统

| 模块 | 注册函数 | 说明 |
|------|----------|------|
| 角色 | `roles.register("name", {"zh": "...", "en": "..."})` | 预置角色 prompt |
| 模式 | `modes.register("name", {"zh": "...", "en": "..."})` | 模式引导后缀 |
| 拼接规则 | `register_rule("name", lambda ctx: ("block_name", text))` | 自定义拼装块 |
| 变量提取 | `register_variable("name", lambda params: value)` | 自定义模板变量 |
| 模板钩子 | `templates.register_hook(lambda text, blocks: new_text)` | 后期处理 |

## 架构

```
preprompt/
├── handler.py    # 主入口（极薄，全委托）
├── context.py    # 参数解析 + 变量提取器注册
├── rules.py      # 拼接规则注册与执行
├── history.py    # 历史对话组装
├── roles.py      # 角色系统
├── modes.py      # 模式系统
└── templates.py  # 模板渲染（默认/自定义）
```

## 工作流用法

复制 `preprompt/` 目录到项目中即可使用，不依赖任何第三方库。

```python
# n8n Code 节点 / Dify 代码节点 / 自建服务
from preprompt import handler
result = handler({
    "question": $json.input.question,
    "lang": $json.input.lang or "zh",
    "mode": $json.input.mode or "normal",
})
# 把 result["prompt"] 传给 LLM
```

## 许可证

MIT
