# TestPyPI 测试发布指南

## 🎯 TestPyPI vs PyPI

| 特性 | TestPyPI | PyPI |
|------|----------|------|
| URL | https://test.pypi.org | https://pypi.org |
| 用途 | 测试发布包 | 正式发布包 |
| 账号 | 独立注册 | 独立注册 |
| Token | 独立创建 | 独立创建 |
| 包索引 | https://test.pypi.org/simple | https://pypi.org/simple |

## 📋 TestPyPI 发布步骤

### 1. 注册 TestPyPI 账号

1. 访问: https://test.pypi.org/account/register/
2. 填写用户名、邮箱和密码
3. 验证邮箱
4. 完成注册

### 2. 启用 2FA（推荐但可选）

1. 登录 TestPyPI: https://test.pypi.org/manage/account/
2. 在 "Two-factor authentication" 部分配置 2FA

### 3. 创建 API Token（推荐）

1. 访问: https://test.pypi.org/manage/account/token/
2. Token name: "LiteNetLib-Python TestPyPI"
3. Scope: "Entire account"（仅用于测试）
4. 点击 "Create token"
5. **重要**: 立即复制 token（格式: `pypi-xxxxxxxxxxxxx`）

### 4. 配置认证

**方法 A: 使用环境变量（推荐）**

```bash
# Windows Command Prompt
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-xxxxxxxxxxxxx

# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-xxxxxxxxxxxxx"

# Linux/Mac
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-xxxxxxxxxxxxx"
```

**方法 B: 创建 .pypirc 配置文件**

创建文件 `%USERPROFILE%\.pypirc` (Windows) 或 `~/.pypirc` (Linux/Mac):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxx

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxx
```

### 5. 发布到 TestPyPI

```bash
# 进入项目目录
cd D:\work\projects\Survivalcraft\netproject\LiteNetLib-Python-0.9.5.2

# 检查包
python -m twine check dist/*

# 发布到 TestPyPI
python -m twine upload --repository testpypi dist/*
```

### 6. 从 TestPyPI 安装测试

```bash
# 方法 1: 使用 --index-url
pip install --index-url https://test.pypi.org/simple/ litenetlib-python

# 方法 2: 使用 --extra-index-url（同时从 PyPI 和 TestPyPI 搜索）
pip install --extra-index-url https://test.pypi.org/simple/ litenetlib-python

# 验证安装
python -c "from litenetlib.core.constants import NetConstants; print('PROTOCOL_ID:', NetConstants.PROTOCOL_ID)"
# 应该输出: PROTOCOL_ID: 11

# 查看已安装的包信息
pip show litenetlib-python
```

### 7. 测试完成后清理

```bash
# 卸载测试包
pip uninstall litenetlib-python -y

# 确认卸载
pip show litenetlib-python
# 应该显示: WARNING: Package(s) not found
```

## 🔍 验证 TestPyPI 发布

发布成功后，访问以下 URL 验证：

- **TestPyPI 包页面**: https://test.pypi.org/project/litenetlib-python/
- **TestPyPI 项目列表**: https://test.pypi.org/manage/projects/

## ⚠️ 常见问题

### 问题 1: 用户名或密码错误

```
HTTPError: 403 Client error: Invalid or non-existent authentication information
```

**解决**:
- 确认 token 格式正确（`pypi-` 开头）
- 确认使用 `__token__` 作为用户名
- 确认没有多余的空格

### 问题 2: 包名已存在

```
HTTPError: 400 Project already exists
```

**解决**:
- TestPyPI 允许多个用户使用相同的包名（用于测试）
- 如果要更新，请增加版本号

### 问题 3: 版本号已存在

```
HTTPError: 400 File already exists
```

**解决**:
- 增加版本号（例如改为 0.9.5.3）
- 重新构建: `python -m build`
- 重新上传

### 问题 4: 依赖包问题

```
ERROR InvalidVersion: ...
```

**解决**:
- 检查版本号格式（PEP 440）
- 当前包无依赖，应该不会出现此问题

## 📝 测试检查清单

发布前确认：

- [ ] TestPyPI 账号已注册
- [ ] API Token 已创建并复制
- [ ] 环境变量或 .pypirc 已配置
- [ ] 包已通过 `twine check` 检查
- [ ] 版本号正确（当前: 0.9.5.2）
- [ ] README.md 内容完整
- [ ] LICENSE 文件存在

## 🚀 快速命令

```bash
# 一键发布到 TestPyPI（配置好认证后）
cd D:\work\projects\Survivalcraft\netproject\LiteNetLib-Python-0.9.5.2
python -m twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ litenetlib-python

# 验证
python -c "from litenetlib.core.constants import NetConstants; print('TestPyPI install OK! PROTOCOL_ID:', NetConstants.PROTOCOL_ID)"

# 清理
pip uninstall litenetlib-python -y
```

## 📚 相关资源

- TestPyPI: https://test.pypi.org/
- TestPyPI 文档: https://packaging.python.org/guides/using-testpypi/
- Twine 文档: https://twine.readthedocs.io/
