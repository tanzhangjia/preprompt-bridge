/**
 * PrePrompt Bridge — 工作流 Prompt 预处理器
 *
 * 纯 JS，零依赖，适用于任何工作流引擎（n8n / Dify / Langflow / OpenClaw / 自建…）。
 *
 * @param {Object} params
 * @param {string|undefined} params.question
 * @param {string|undefined} params.quesion  // 兼容拼写错误
 * @param {Array<{query:string,answer:string,files?:Array}>} params.his
 * @param {string|undefined} params.sys_prompt  // 系统指令
 * @param {Object|undefined} params.context     // 额外上下文
 * @param {string|undefined} params.template    // 自定义模板
 * @param {number|undefined} params.max_history // 最大历史轮数
 * @param {boolean|undefined} params.safe_mode  // 敏感信息过滤
 * @returns {{prompt:string, meta:Object}}
 */
function handler(params) {
  // ── 默认值 ──
  const safe_mode = !!params?.safe_mode;
  const max_history = typeof params?.max_history === 'number'
    ? Math.max(0, params.max_history) : 20;

  // ── 提取问题 ──
  const rawQuestion = (
    params?.question ??
    params?.quesion ??
    params?.Q ??  // 兼容单字母缩写
    ""
  ).trim();
  const question = _cleanText(rawQuestion, safe_mode);

  // ── 组装历史对话 ──
  let hisLines = [];
  let usedHistoryCount = 0;
  const hisArr = Array.isArray(params?.his) ? params.his : [];

  // 倒序取最新的最多 max_history 轮
  const slice = hisArr.slice(-max_history);
  usedHistoryCount = slice.length;

  for (const item of slice) {
    if (!item || typeof item !== 'object') continue;

    const query = _cleanText(item.query ?? "", safe_mode);
    const answer = _cleanText(item.answer ?? "", safe_mode);
    const files = Array.isArray(item.files) ? item.files : [];

    hisLines.push(`用户：${query}`);
    if (files.length > 0) {
      const fileNames = files
        .map(f => f?.name ?? "")
        .filter(Boolean)
        .join("、");
      if (fileNames) hisLines.push(`（附带文件：${fileNames}）`);
    }
    hisLines.push(`AI：${answer}`);
  }

  const historyStr = hisLines.join("\n");

  // ── 拼装系统指令 ──
  let sysPrompt = "";
  if (params?.sys_prompt) {
    sysPrompt = _cleanText(params.sys_prompt, safe_mode);
  }

  // ── 拼装额外上下文 ──
  let contextStr = "";
  if (params?.context && typeof params.context === 'object') {
    const pairs = [];
    for (const [k, v] of Object.entries(params.context)) {
      if (v !== undefined && v !== null) {
        pairs.push(`${k}：${_cleanText(String(v), safe_mode)}`);
      }
    }
    contextStr = pairs.join("\n");
  }

  // ── 渲染模板 ──
  const template = params?.template || _defaultTemplate();
  const prompt = _renderTemplate(template, {
    question,
    history: historyStr,
    sys_prompt: sysPrompt,
    context: contextStr,
    his_count: String(usedHistoryCount),
  });

  // ── 元信息（方便调试和日志） ──
  const meta = {
    has_question: question.length > 0,
    history_rounds: usedHistoryCount,
    has_sys_prompt: sysPrompt.length > 0,
    has_context: contextStr.length > 0,
    safe_mode,
    prompt_length: prompt.length,
  };

  return { prompt, meta };
}

// ── 默认模板 ──
function _defaultTemplate() {
  return [
    "{{#if sys_prompt}}",
    "{{sys_prompt}}",
    "",
    "{{/if}}",
    "{{#if history}}",
    "历史对话：",
    "{{history}}",
    "",
    "{{/if}}",
    "{{#if context}}",
    "额外信息：",
    "{{context}}",
    "",
    "{{/if}}",
    "用户问题：{{question}}",
  ].join("\n");
}

// ── 极简模板渲染（支持 {{var}} 和 {{#if var}}...{{/if}}） ──
function _renderTemplate(tpl, vars) {
  // 先处理条件块
  let result = tpl.replace(
    /\{\{#if (\w+)\}\}([\s\S]*?)\{\{\/if\}\}/g,
    (_, key, body) => {
      return vars[key] ? body : "";
    }
  );

  // 再替换变量
  result = result.replace(/\{\{(\w+)\}\}/g, (_, key) => {
    return vars[key] !== undefined ? vars[key] : "";
  });

  // 清理多余空行
  result = result.replace(/\n{3,}/g, "\n\n").trim();

  return result;
}

// ── 文本清洗（可选敏感信息过滤） ──
function _cleanText(text, safe) {
  if (typeof text !== 'string') return "";
  let t = text.trim();

  if (safe) {
    // 基本敏感信息模式（仅供示意，实际应接入更完善的过滤规则）
    // 身份证（18位，先匹配避免被手机号规则截断）
    t = t.replace(/\b\d{17}[\dXx]\b/g, "[身份证]");
    // 手机号
    t = t.replace(/\b1[3-9]\d{9}\b/g, "[手机号]");
    // 邮箱
    t = t.replace(/\b[\w.-]+@[\w.-]+\.\w{2,4}\b/g, "[邮箱]");
  }

  return t;
}

// ── 兼容浏览器/Node/工作流引擎 ──
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { handler };
} else if (typeof define === 'function' && define.amd) {
  define([], () => ({ handler }));
} else if (typeof window !== 'undefined') {
  window.PrePrompt = { handler };
}
