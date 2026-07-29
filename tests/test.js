#!/usr/bin/env node
/**
 * PrePrompt Bridge 测试
 */

const { handler } = require('../src/index.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed++;
    console.log(`  ✗ ${name}: ${e.message}`);
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg || 'assertion failed');
}

// ── 基础功能 ──

test('空输入', () => {
  const r = handler({});
  assert(typeof r.prompt === 'string', 'prompt should be string');
  assert(r.prompt.includes('用户问题：'), 'should include default template');
  assert(typeof r.meta === 'object', 'should have meta');
});

test('只有问题', () => {
  const r = handler({ question: '你好' });
  assert(r.prompt.includes('你好'), 'should include question');
  assert(r.meta.has_question === true);
  assert(r.meta.history_rounds === 0);
});

test('问题 + 历史', () => {
  const r = handler({
    question: '继续',
    his: [
      { query: '你是谁', answer: 'AI助手' },
      { query: '吃什么', answer: '随便' },
    ],
  });
  assert(r.prompt.includes('继续'), 'should have question');
  assert(r.prompt.includes('你是谁'), 'should have history query');
  assert(r.prompt.includes('AI助手'), 'should have history answer');
  assert(r.meta.history_rounds === 2);
});

test('历史中的文件', () => {
  const r = handler({
    question: '分析这个',
    his: [{
      query: '帮我看看',
      answer: '好的',
      files: [{ name: 'report.pdf', type: 'pdf' }],
    }],
  });
  assert(r.prompt.includes('report.pdf'), 'should mention file');
});

// ── 拼写兼容 ──

test('quesion 拼写兼容', () => {
  const r = handler({ quesion: '兼容测试' });
  assert(r.prompt.includes('兼容测试'), 'should accept misspelled key');
});

// ── 系统指令 ──

test('系统指令', () => {
  const r = handler({
    question: '写文案',
    sys_prompt: '你是文案专家',
  });
  assert(r.prompt.includes('文案专家'), 'sys_prompt should appear');
  assert(r.prompt.includes('文案专家'), 'sys_prompt should render');
  assert(r.meta.has_sys_prompt === true);
});

// ── 额外上下文 ──

test('额外上下文', () => {
  const r = handler({
    question: '推荐',
    context: { 用户偏好: '辣的食物', 预算: '50元' },
  });
  assert(r.prompt.includes('辣的食物'), 'context value should appear');
  assert(r.prompt.includes('用户偏好'), 'context key should appear');
  assert(r.meta.has_context === true);
});

// ── 自定义模板 ──

test('自定义模板', () => {
  const r = handler({
    question: 'test',
    template: 'Q: {{question}}',
  });
  assert(r.prompt === 'Q: test', `got: "${r.prompt}"`);
});

test('模板条件块', () => {
  const r = handler({
    question: 'hi',
    template: '{{#if sys_prompt}}{{sys_prompt}}{{/if}}{{question}}',
  });
  assert(r.prompt === 'hi', 'without sys_prompt block should vanish');

  const r2 = handler({
    question: 'hi',
    sys_prompt: '你是',
    template: '{{#if sys_prompt}}{{sys_prompt}}{{/if}}{{question}}',
  });
  assert(r2.prompt === '你是hi', 'with sys_prompt block should render');
});

// ── max_history ──

test('max_history 限制', () => {
  const his = [];
  for (let i = 0; i < 50; i++) {
    his.push({ query: `q${i}`, answer: `a${i}` });
  }
  const r = handler({ question: 'x', his, max_history: 3 });
  assert(r.meta.history_rounds === 3, `got ${r.meta.history_rounds}`);
  assert(r.prompt.includes('q47'), 'should include latest');
  assert(!r.prompt.includes('q0'), 'should not include oldest');
});

// ── safe_mode ──

test('safe_mode 过滤手机号', () => {
  const r = handler({
    question: '手机13800138000和身份证110101199001011234',
    safe_mode: true,
  });
  assert(!r.prompt.includes('13800138000'), 'phone should be masked');
  assert(!r.prompt.includes('110101199001011234'), 'id should be masked');
  assert(r.prompt.includes('[手机号]'), 'should show phone placeholder');
  assert(r.prompt.includes('[身份证]'), 'should show id placeholder');
});

// ── 边界 ──

test('his 非数组', () => {
  const r = handler({ question: 'x', his: 'not an array' });
  assert(r.prompt.includes('x'), 'should not crash');
  assert(r.meta.history_rounds === 0);
});

test('history item 空对象', () => {
  const r = handler({ question: 'x', his: [{}, { query: 'a', answer: 'b' }] });
  assert(r.meta.history_rounds === 2);
});

test('question 为空字符串', () => {
  const r = handler({ question: '' });
  assert(r.meta.has_question === false);
});

test('question 为 undefined', () => {
  const r = handler({});
  assert(r.meta.has_question === false);
});

// ── 多历史累积 ──

test('大量历史数据', () => {
  const his = [];
  for (let i = 0; i < 100; i++) {
    his.push({ query: `用户提问第${i}轮`, answer: `AI回答第${i}轮` });
  }
  const r = handler({ question: '总结一下', his });
  assert(r.meta.history_rounds === 20, `expected 20 got ${r.meta.history_rounds}`);
  assert(r.prompt.includes('第99轮'), 'should include latest');
  assert(!r.prompt.includes('第0轮'), 'should trim old');
});

// ── 完整默认模板输出 ──

test('默认模板完整输出', () => {
  const r = handler({
    question: '你好',
    his: [{ query: 'hi', answer: 'hello' }],
    sys_prompt: '助手',
    context: { lang: '中文' },
  });
  const lines = r.prompt.split('\n').map(l => l.trim());
  assert(lines.some(l => l.includes('助手')), 'should have sys');
  assert(lines.some(l => l.includes('hi')), 'should have history');
  assert(lines.some(l => l.includes('中文')), 'should have context');
  assert(lines.some(l => l.includes('你好')), 'should have question');
});

// ── meta 信息完整性 ──

test('meta 字段完整', () => {
  const r = handler({ question: 'a', his: [{ query: 'q', answer: 'a' }], sys_prompt: 's', context: { x: 'y' }, safe_mode: true });
  const m = r.meta;
  assert(m.has_question === true);
  assert(m.history_rounds === 1);
  assert(m.has_sys_prompt === true);
  assert(m.has_context === true);
  assert(m.safe_mode === true);
  assert(typeof m.prompt_length === 'number');
});

console.log(`\n${'─'.repeat(40)}\n${passed} passed, ${failed} failed${failed > 0 ? ' ❌' : ' ✅'}`);
process.exit(failed > 0 ? 1 : 0);
