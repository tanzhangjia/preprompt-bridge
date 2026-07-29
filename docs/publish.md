# 发布到 NPM

## 一次性准备

```bash
npm login
```

## 发布

```bash
npm publish
```

## 更新

```bash
# 改 version
npm version patch
npm publish
```

或者发布为 scoped package（如果你有组织）：

```bash
# 改 package.json 的 name 为 @yourname/preprompt-bridge
npm publish --access public
```
