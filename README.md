# PrePrompt Bridge

把 Prompt 从"每节点一坨"变成"一个 LLM 节点 + N 个可插拔模块"。

## 一句话

1 个 LLM 节点 + 改参数 = 无限场景，不动模板。

## 为什么会有这个项目

先看一个常见的工作流：

```
工作流里有 5 个 LLM 节点：翻译、客服、代码审查、文案写作、教学助手
每个节点的 prompt 都差不多：系统指令 + 历史 + 问题
但每个节点都要单独维护一份 prompt 模板
```

然后需求来了：

```
加英文版    → 每个 LLM 节点复制一份改标签
加深度思考  → 每个 LLM 节点追加推理引导语
换角色      → 复制出来改角色设定
改模板格式  → 所有 LLM 节点逐个同步
```

5 个节点变成 15 个，每次改模板要改 15 次。这是把团队逼疯的东西。

**preprompt-bridge 的做法：** 把 prompt 拆成独立模块（问题、历史、角色、模式、上下文、输出格式…），每个模块是可插拔的规则。用户只需要 **1 个 LLM 节点**，场景差异通过参数进去：

```
                              ┌─ lang=zh, mode=deep, role=teacher
用户输入 + 配置参数 → 这个项目 ── lang=en, mode=fast, role=translator
                              └─ lang=ja, mode=creative, role=writer
                              → 同一个 prompt 模板，输出不同场景的 prompt
```

## 这是一套架构，不是一个函数

| 传统做法 | preprompt-bridge |
|----------|-----------------|
| 每个 LLM 节点一坨 prompt 模板 | 1 个 LLM 节点 + 参数 |
| 增加场景 = 复制 LLM 节点 | 增加场景 = 改参数 |
| 改模板要同步 N 个节点 | 改模板就是改 rules 配置 |
| 新角色要写死进模板 | `roles.register()` |
| 新模式要在每个节点的手动加 | `modes.register()` |
| 新参数要改所有节点的模板变量 | `register_variable()` |
| 拼接顺序硬编码在模板里 | `rules` 参数控制 |

**简单说：传统做法是「每场景每 LLM 节点 = 每 prompt」，这个项目是「N 场景 = 1 LLM 节点 + N 参数」。**

## 快速上手

```python
from preprompt import handler

# 同一个函数，不同参数 = 不同场景
result = handler({
    "question": "帮我写个简介",
    "lang": "zh",
    "mode": "deep",
    "role": "writer",
})
```

场景切换只改参数，不碰代码不碰模板。

## 核心概念

### 1. 拼接规则（Rules）

prompt 由哪些模块按什么顺序拼接，由 `rules` 参数控制：

```python
handler({
    "question": "hi",
    "his": [...],
    "sys_prompt": "你是助手",
    "rules": ["sys_prompt", "history", "question"],
})
```

默认顺序：`["sys_prompt", "history", "context", "output_format", "question", "mode_suffix", "extra_vars"]`

### 2. 可插拔的模块

**角色不够用？**

```python
from preprompt import roles

roles.register("qa_expert", {
    "zh": "你是一个QA专家",
    "en": "You are a QA expert",
})
handler({"role": "qa_expert", ...})
```

**模式不够用？**

```python
from preprompt import modes

modes.register("concise", {
    "zh": "\n用一句话回答",
    "en": "\nAnswer in one sentence",
})
handler({"mode": "concise", ...})
```

**入参不够用？**

```python
from preprompt import register_variable

register_variable("temperature", lambda params: str(params.get("temperature", "0.7")))
handler({"temperature": "0.9", ...})
```

**拼接顺序不够用？**

```python
from preprompt import register_rule

register_rule("weather", lambda ctx: ("weather", f"天气：{ctx._raw.get('weather')}"))
handler({"weather": "晴天", "rules": ["weather", "question"]})
```

### 3. 实现方式

面向工作流引擎设计——本质是一个纯函数 `handler(params) → {prompt, meta}`，不依赖任何框架。

- **在 n8n 里**：Code 节点里 `from preprompt import handler` 直接调用
- **在 Dify 里**：作为 Dify Plugin 安装（`dify/` 目录）
- **在自建服务里**：作为独立 Python 模块使用
- **在 OpenClaw 里**：SKILL.md 加载即可

```
工作流节点 → handler(params) → prompt 字符串 → LLM 节点（只收一个变量）
```

## API 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `question` | str | `""` | 用户问题 |
| `quesion` | str | — | 兼容拼写错误 |
| `his` | list | `[]` | 历史 `[{query, answer}]` |
| `sys_prompt` | str | `""` | 系统指令 |
| `lang` | str | `"zh"` | 语言 `zh`/`en`/`ja` |
| `mode` | str | `""` | 模式 `deep`/`fast`/`creative`/`professional`/`simple` |
| `role` | str | `""` | 角色 `assistant`/`code_review`/`translator`/`writer`/`teacher` |
| `context` | dict | `{}` | 额外上下文 |
| `template` | str | — | 自定义模板（`{{question}}`、`{% if history %}`） |
| `rules` | list | — | 自定义拼接顺序 |
| `max_history` | int | `20` | 最大历史轮数 |
| `style_rules` | str | `""` | 风格指令 |
| `output_format` | str | `""` | 输出格式要求 |
| `...` | any | — | 自定义参数（通过 `register_variable` 提取） |

返回 `{"prompt": str, "meta": dict}`。

## 作为 Dify 插件使用

`dify/` 目录包含完整的 Dify Plugin 定义：

```bash
cd dify && dify plugin install .
```

在工作流中拖一个 **PrePrompt Bridge** 节点，配置参数后把输出传给 LLM。

## 许可证

MIT

---

**GitHub:** https://github.com/tanzhangjia/preprompt-bridge
