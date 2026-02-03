# AI 助手项目恢复指南

## 快速恢复 litenetlib-0952 项目上下文

当重新接手此项目时，按以下顺序阅读：

### 第一步：阅读 CONTEXT.md（最全面）

```bash
cd D:\work\projects\Survivalcraft\netproject\LiteNetLib-Python-0.9.5.2
```

阅读 `CONTEXT.md` - 这包含了项目的完整上下文：
- 项目概览和定位
- 技术架构和目录结构
- 核心协议常量
- 开发历程和 bug 修复记录
- 测试验证结果
- 发布流程
- 已知问题和注意事项
- 合规性信息

### 第二步：检查当前状态

```bash
# 查看最新代码
git log --oneline -5

# 检查版本
cat setup.py | grep version
cat pyproject.toml | grep version

# 查看未提交的更改
git status
```

### 第三步：运行测试验证

```bash
# 运行完整测试套件
python -m pytest tests/ -v

# 测试 PyPI 安装
python test_testpypi_install.py
```

### 第四步：检查 PyPI 发布状态

```bash
# 检查包是否可用
pip search litenetlib-0952  # 如果可用
# 或访问
# https://pypi.org/project/litenetlib-0952/
```

## 关键信息速查

### 项目基本信息

```
包名: litenetlib-0952
当前版本: 1.0.0
兼容: C# LiteNetLib v0.9.5.2
PyPI: https://pypi.org/project/litenetlib-0952/
GitHub: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2
```

### 版本号体系

- **包名** `litenetlib-0952`: 标识与 C# v0.9.5.2 的兼容性
- **版本号** `1.0.0`: Python 包的独立版本号
  - `1.0.1` = bug 修复
  - `1.1.0` = 新功能
  - `2.0.0` = 重大变更

### 核心文件

| 文件 | 用途 |
|------|------|
| `CONTEXT.md` | 完整项目上下文（AI助手专用）|
| `README.md` | 用户文档 |
| `setup.py` | 包配置 |
| `pyproject.toml` | 现代Python打包配置 |
| `litenetlib/core/packet.py` | 数据包实现 |
| `litenetlib/core/constants.py` | 协议常量 |

### 常用命令

```bash
# 测试
python -m pytest tests/ -v
python test_testpypi_install.py

# 构建
rm -rf dist build *.egg-info
python -m build

# 检查包
python -m twine check dist/*

# 发布（需要配置 token）
python -m twine upload --repository testpypi dist/litenetlib_0952-*
python -m twine upload dist/litenetlib_0952-*
```

### 已知的重要修复

1. **NetPacket IntEnum 判断** (packet.py)
   - 使用 `try: PacketProperty(value)` 而不是 `isinstance()`

2. **Windows UTF-8 编码** (测试脚本)
   - 添加 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`

3. **Twine 进度条**
   - 使用 `--disable-progress-bar` 标志

## 遇到问题时的诊断流程

### 问题：测试失败

1. 检查是否是 IntEnum 问题（packet.py）
2. 检查 UTF-8 编码（测试脚本）
3. 检查测试期望值是否正确

### 问题：发布失败

1. 检查版本号是否已更新
2. 检查 token 是否正确配置
3. 先在 TestPyPI 测试

### 问题：C# 互操作性

1. 验证 PROTOCOL_ID = 11
2. 验证字节序（little-endian）
3. 验证 PacketProperty 枚举值

## 项目维护者

- **原作者 (C#)**: RevenantX (Hubert "LHub" Tonneau)
- **Python 移植**: xiaoyanghuo
- **AI 助手**: Claude Sonnet 4.5

## 最后更新

- 日期: 2026-02-03
- 版本: 1.0.0
- 状态: 生产就绪，已发布到 PyPI
