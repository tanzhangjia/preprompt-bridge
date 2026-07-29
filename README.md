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

print(result["prompt"])
```

## 核心概念

### 1. 拼接规则（Rules）

prompt 的拼装顺序由 `rules` 参数控制，**不硬编码**：

```python
handler({
    "question": "hi",
    "rules": ["sys_prompt", "history", "question"],
})
```

默认顺序：`["sys_prompt", "history", "context", "output_format", "question", "mode_suffix", "extra_vars"]`

可以注册自定义拼装块：

```python
from preprompt import register_rule

register_rule("weather", lambda ctx: ("weather", f"天气：{ctx._raw.get('weather')}"))
handler({
    "question": "适合出门吗", "weather": "晴天 25°C",
    "rules": ["weather", "question"],
})
```

### 2. 自定义变量（Variables）

注册任意自定义变量提取器，在模板和 prompt 中使用：

```python
from preprompt import register_variable

register_variable("temperature", lambda p: str(p.get("temperature", "0.7")))
handler({"question": "写首诗", "temperature": "0.9"})
```

### 3. 角色 + 模式 + 多语言

```python
handler({
    "question": "review this code",
    "lang": "en",
    "mode": "deep",
    "role": "code_review",
})
# → "You are a senior code reviewer..."
#   "Conversation history:"
#   "User question: review this code"
#   "Think step by step..."
```

角色和模式都是插件式的：

```python
from preprompt import roles, modes

roles.register("qa_expert", {"zh": "你是QA专家", "en": "You are a QA expert"})
modes.register("concise", {"zh": "一句话回答", "en": "One sentence answer"})
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
| `template` | str | — | 自定义模板 |
| `rules` | list | — | 自定义拼接顺序 |
| `max_history` | int | `20` | 最大历史轮数 |
| `style_rules` | str | `""` | 风格指令 |
| `output_format` | str | `""` | 输出格式要求 |
| `...` | any | — | 自定义参数（通过 register_variable 提取） |

返回 `{"prompt": str, "meta": dict}`。

## 作为 Dify 插件使用

本项目提供 **Dify Plugin** 集成，可直接在 Dify Marketplace 搜索 "PrePrompt Bridge" 安装。

或手动安装：

```bash
git clone https://github.com/tanzhangjia/preprompt-bridge
cd preprompt-bridge/dify
dify plugin install .
```

在工作流中添加 **PrePrompt Bridge** 节点，配好参数后把输出的 `prompt` 传给 LLM 节点即可。

详见 `dify/` 目录。

## 架构

```
preprompt/
├── handler.py    # 主入口（全委托）
├── context.py    # 参数解析 + 变量提取器注册
├── rules.py      # 拼接规则注册与执行
├── history.py    # 历史对话组装
├── roles.py      # 角色系统
├── modes.py      # 模式系统
└── templates.py  # 模板渲染

dify/
├── manifest.yaml          # Dify 插件声明
├── icon.svg               # 插件图标
├── provider/
│   └── preprompt.yaml     # Provider + Tool 定义
└── tools/
    └── preprompt.py       # Dify 工具实现（桥接核心库）
```

## 在工作流中使用

复制 `preprompt/` 目录到项目中即可，不依赖任何第三方库。

```python
# n8n / Dify 代码节点 / 自建服务
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
