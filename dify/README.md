# Dify Plugin: PrePrompt Bridge

Dify 插件包，用于将工作流输入整理为结构化 prompt，减少 LLM 节点配置重复。

## 安装

### 方法 1：源码安装

```bash
git clone https://github.com/tanzhangjia/preprompt-bridge
cd preprompt-bridge/dify
pip install -r ../requirements.txt  # 无外部依赖，只需核心库
dify plugin install .
```

### 方法 2：从 Dify Marketplace 安装

搜索 "PrePrompt Bridge" 安装即可。

## 使用

在工作流中添加 **PrePrompt Bridge** 节点，配置参数后将输出的 `prompt` 传给 LLM 节点作为唯一输入。

**典型配置：**

| 参数 | 值 | 说明 |
|------|----|------|
| question | `{{节点.用户输入}}` | 用户当前问题 |
| lang | `zh` | 语言 |
| mode | `deep` | 深度思考模式 |
| role | `writer` | 写手角色 |
| sys_prompt | `你是一个文案专家` | 系统指令 |

## 开发

```bash
cd dify/
# 修改后重新打包
dify plugin package .
```

## 输出

- `prompt` — 组装好的完整 prompt 字符串，可直接传给 LLM
- `meta` — 元信息 JSON，包含 `has_question`、`history_rounds` 等调试字段
