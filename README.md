# PrePrompt Bridge

工作流中的 Prompt 预处理器。

把杂乱的输入（历史对话、上下文、变量）整理成给 LLM 的结构化 prompt，减少工作流引擎里堆砌 prompt 模板的烦恼。

纯 JavaScript，零依赖，跑在任何能运行 JS 的工作流引擎里（n8n、Dify、Langflow、OpenClaw、自建服务…）。

## 一句话

> 你工作流里那个写 prompt 的代码节点，就是它。

## 快速开始

```js
const { handler } = require('preprompt-bridge');

const result = handler({
  question: "帮我写个简介",
  his: [
    { query: "你是谁", answer: "我是 AI 助手" },
    { query: "你能做什么", answer: "回答问题、写文案、编程" }
  ],
  sys_prompt: "你是一个专业文案写手",
});

console.log(result.prompt);
```

## 安装

```bash
npm i preprompt-bridge
# 或者直接拷贝 src/index.js 到工作流节点里
```

## 使用方式

### 在工作流引擎中

直接把 `src/index.js` 的函数体拷贝到工作流的「代码节点」或「function node」里。

### 在 Node.js 中

```js
const { handler } = require('preprompt-bridge');
```

### 在浏览器中

```html
<script src="https://unpkg.com/preprompt-bridge"></script>
<script>
  const res = PrePrompt.handler({ question: "你好" });
</script>
```

## 设计

```
输入（杂乱）                 PrePrompt Bridge              输出（结构化的 prompt）
┌─────────────┐           ┌──────────────────┐            ┌──────────────────────┐
│ question     │ ──────▶  │ 文本合并与格式化   │ ──────▶  │ 系统指令（如有）      │
│ history[]    │           │ 历史对话拼接       │           │ 用户问题             │
│ context      │           │ 上下文注入         │           │ 历史会话（压缩）       │
│ sys_prompt   │           │ 模板渲染           │           │ 其他上下文            │
│ variables    │           │ 敏感信息过滤        │           └──────────────────────┘
└─────────────┘           └──────────────────┘
```

## API

### `handler(params)`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | string | 否 | 用户当前问题 |
| `his` | Array\<HistoryItem\> | 否 | 历史对话 |
| `sys_prompt` | string | 否 | 系统指令/角色设定 |
| `context` | object | 否 | 额外上下文键值对 |
| `template` | string | 否 | 自定义 prompt 模板（见下文） |
| `max_history` | number | 否 | 最大历史轮数（默认 20） |
| `safe_mode` | boolean | 否 | 是否开启敏感信息过滤 |
| `question` | string | 否 | 兼容 `question` 拼写错误 |

返回 `{ prompt: string, meta: object }`。

### `HistoryItem`

```ts
{
  query: string;    // 用户说
  answer: string;   // AI 回复
  files?: Array<{   // 附带文件（可选）
    name: string;
    type: string;
    url?: string;
  }>;
}
```

### 自定义模板

默认模板：

```
{{sys_prompt}}

以上是系统设定。

历史对话：
{{history}}

{% if context %}
额外信息：
{{context}}
{% endif %}

用户问题：{{question}}
```

你可以传自己的模板，使用 `{{placeholder}}` 语法：

```js
handler({
  question: "你好",
  template: "问题：{{question}}\n背景：{{history}}",
});
```

## 在内置工作流中使用

### n8n

在 Code 节点中：

```js
const { handler } = require('preprompt-bridge');
return handler({
  question: $input.first().json.question,
  his: $input.first().json.history,
});
```

### Dify

在 Code 节点中复制 `src/index.js` 的 `handler` 函数。

### OpenClaw Skill

见 `SKILL.md`。

## 许可证

MIT
