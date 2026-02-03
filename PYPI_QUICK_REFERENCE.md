# PyPI 发布快速参考

## 📦 已构建完成

```
dist/
├── litenetlib_python-0.9.5.2-py3-none-any.whl  (17 KB)
└── litenetlib_python-0.9.5.2.tar.gz           (18 KB)
```

## ✅ 本地测试通过

```bash
# 安装测试
pip install dist/litenetlib_python-0.9.5.2-py3-none-any.whl

# 验证
python -c "from litenetlib.core.constants import NetConstants; print('PROTOCOL_ID:', NetConstants.PROTOCOL_ID)"
# 输出: PROTOCOL_ID: 11 ✅

# 卸载
pip uninstall litenetlib-python -y
```

## 🚀 发布到 PyPI（一键命令）

### 第一次发布（需要 API Token）

```bash
# 1. 创建 PyPI API Token: https://pypi.org/manage/account/token/
# 2. 配置 token
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-xxxxxxxxxxxxx

# 3. 检查包
python -m twine check dist/*

# 4. 发布
python -m twine upload dist/*
```

### 后续更新（假设已配置 token）

```bash
# 更新版本号 -> 构建 -> 发布
python -m build && python -m twine upload dist/*
```

## 📋 包信息

| 项目 | 内容 |
|------|------|
| 包名 | litenetlib-python |
| 版本 | 0.9.5.2 |
| PyPI URL | https://pypi.org/project/litenetlib-python/ |
| 仓库 | https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2 |

## ⚠️ 重要提示

1. **版本号不要重复**: 每次发布前必须更新版本号
2. **TestPyPI 先测试**: 推荐先发布到 TestPyPI 验证
3. **Tag 版本**: 发布后记得在 GitHub 创建 tag
4. **不可删除**: PyPI 上的包一旦发布无法删除，只能 yank

## 📚 相关文档

- 完整发布指南: `PYPI_PUBLISHING_GUIDE.md`
- PyPI 文档: https://packaging.python.org/tutorials/packaging-projects/
