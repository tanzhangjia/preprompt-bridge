# 发布到 PyPI

## 准备

```bash
pip install build twine
```

## 构建 + 发布

```bash
python3 -m build
python3 -m twine upload dist/*
```

## 测试发布（TestPyPI）

```bash
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
