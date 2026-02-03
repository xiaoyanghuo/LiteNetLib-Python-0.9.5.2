# PyPI 发布指南

## 📦 已构建的发布包

```
dist/
├── litenetlib_python-0.9.5.2-py3-none-any.whl    # Wheel 包
└── litenetlib_python-0.9.5.2.tar.gz             # 源码包
```

## 🚀 发布到 PyPI 的步骤

### 1. 注册 PyPI 账号

1. 访问 https://pypi.org/account/register/
2. 创建账号并验证邮箱
3. 启用双因素认证（2FA）

### 2. 安装发布工具

```bash
pip install twine build
```

### 3. 创建 API Token

1. 登录 PyPI: https://pypi.org/manage/account/token/
2. 创建新的 API Token
   - Token name: "LiteNetLib-Python publishing"
   - Scope: "Entire account" (或仅针对此项目)
3. **重要**: 复制生成的 token（只显示一次！）

### 4. 配置认证

**方法 A: 使用 token（推荐）**

创建 `%USERPROFILE%\.pypirc` (Windows) 或 `~/.pypirc` (Linux/Mac):

```ini
[pypi]
username = __token__
password = <your-pypi-token>
```

**方法 B: 使用环境变量（更安全）**

```bash
# Windows
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-<your-token>

# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-token>
```

### 5. 测试发布到 TestPyPI（推荐）

```bash
# 注册 TestPyPI 账号: https://test.pypi.org/account/register/

# 构建
python -m build

# 发布到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 安装测试
pip install --index-url https://test.pypi.org/simple/ litenetlib-0952
```

### 6. 发布到正式 PyPI

```bash
# 检查包内容
python -m twine check dist/*

# 发布
python -m twine upload dist/*
```

## ✅ 验证发布

发布成功后，验证安装：

```bash
# 清理旧的安装
pip uninstall litenetlib-0952 -y

# 从 PyPI 安装
pip install litenetlib-0952

# 验证
python -c "from litenetlib.core.constants import NetConstants; print(f'PROTOCOL_ID={NetConstants.PROTOCOL_ID}')"
# 应该输出: PROTOCOL_ID=11
```

## 📋 发布前检查清单

### 必需文件

- [x] `setup.py` - 安装脚本
- [x] `pyproject.toml` - 现代 Python 打包配置
- [x] `README.md` - 项目说明（会显示在 PyPI 上）
- [x] `LICENSE` - MIT License
- [x] `requirements.txt` - 依赖列表

### 版本号

- [x] 版本号: `0.9.5.2` (与 C# LiteNetLib 版本对应)

### 包名

- [x] PyPI 包名: `litenetlib-0952`
- [x] 导入名称: `litenetlib`

### 分类

- [x] Development Status: 5 - Production/Stable
- [x] License: OSI Approved :: MIT License
- [x] Python 版本: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

### 文档

- [x] README.md 包含:
  - 项目简介
  - 安装说明
  - 快速开始示例
  - 特性说明
  - 与 C# 互通说明
  - 许可证信息

## 📊 包信息

| 项目 | 值 |
|------|-----|
| **包名** | litenetlib-0952 |
| **版本** | 0.9.5.2 |
| **描述** | Lite reliable UDP networking library for Python (C# LiteNetLib v0.9.5.2 compatible) |
| **作者** | xiaoyanghuo |
| **许可证** | MIT |
| **Python 要求** | >= 3.7 |
| **依赖** | 无（纯 Python 实现）|
| **关键字** | networking, udp, reliable, protocol, litenetlib, game, networking |

## 🔗 相关链接

- **GitHub**: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2
- **PyPI**: https://pypi.org/project/litenetlib-0952/
- **问题追踪**: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues

## 📝 版本发布说明

### v0.9.5.2 (当前版本)

**特性**:
- 与 C# LiteNetLib v0.9.5.2 100% 二进制兼容
- 所有 5 种传输方法（Unreliable, ReliableOrdered 等）
- 完整的协议实现（ACK、分片、MERGED 包等）
- UTF-8 编码支持（包括中文）
- asyncio 支持

**测试**:
- 365 个单元测试（100% 通过率）
- 互操作性测试（与 C# 互通验证）
- 二进制兼容性验证（38/38 测试通过）

**质量**:
- 生产就绪（Development Status: 5 - Production/Stable）
- 完整文档
- 示例代码
- MIT 许可证

## 🛠️ 后续版本发布

### 更新版本号

1. 更新 `setup.py` 中的 `version`
2. 更新 `pyproject.toml` 中的 `version`
3. 更新 `README.md` 中的版本说明
4. 提交到 Git

### 构建和发布

```bash
# 清理旧的构建
rm -rf dist/ build/ *.egg-info

# 构建
python -m build

# 检查
python -m twine check dist/*

# 发布
python -m twine upload dist/*
```

## 📞 支持

如有问题，请:
- 提交 Issue: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues
- 查看文档: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/blob/main/README.md
