# LiteNetLib-Python-0.9.5.2 项目上下文

> **用于 AI 助手快速恢复项目上下文**

## 项目概览

### 核心信息

```
项目名称: litenetlib-0952
当前版本: 1.0.0
PyPI: https://pypi.org/project/litenetlib-0952/
GitHub: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2
原版 (C#): https://github.com/RevenantX/LiteNetLib (v0.9.5.2)
作者: xiaoyanghuo
许可: MIT
```

### 项目定位

- **非官方 Python 移植版本**，从 C# LiteNetLib v0.9.5.2 移植
- 100% 二进制兼容，可与 C# 版本互通
- 纯 Python 实现，无外部依赖
- 生产就绪，365 个单元测试全部通过

## 技术架构

### 目录结构

```
litenetlib/
├── __init__.py                 # 包入口
├── core/                       # 核心实现
│   ├── constants.py           # 协议常量 (PacketProperty, DeliveryMethod 等)
│   ├── packet.py              # 数据包实现 (NetPacket, NetPacketPool)
│   ├── manager.py             # 网络管理器 (LiteNetManager)
│   ├── peer.py                # 对等端实现 (NetPeer)
│   ├── events.py              # 事件系统 (EventBasedNetListener)
│   ├── connection_request.py  # 连接请求处理
│   └── internal_packets.py    # 内部数据包
├── channels/                   # 传输通道
│   ├── base_channel.py        # 基础通道
│   ├── reliable_channel.py    # 可靠通道
│   └── sequenced_channel.py    # 顺序通道
└── utils/                      # 工具函数
    ├── data_writer.py         # 数据序列化
    ├── data_reader.py         # 数据反序列化
    ├── fast_bit_converter.py  # 快速字节转换
    └── net_utils.py           # 网络工具函数
```

### 核心协议常量 (v0.9.5.2)

```python
PROTOCOL_ID = 11
ACK = 2
EMPTY = 17
MERGED = 12
CHANNELED = 1
DEFAULT_WINDOW_SIZE = 64
MAX_SEQUENCE = 32768
```

### 5 种传输方法

- `UNRELIABLE` - 不可靠传输
- `RELIABLE_UNORDERED` - 可靠无序
- `SEQUENCED` - 有序传递
- `RELIABLE_ORDERED` - 可靠有序
- `RELIABLE_SEQUENCED` - 可靠有序

## 版本号体系

### 当前方案

```
包名: litenetlib-0952
  └─ 标识与 C# LiteNetLib v0.9.5.2 兼容

版本: 1.0.0
  └─ Python 包的独立版本号
      1.0.0 = 首个稳定发布
      1.0.1 = bug 修复
      1.1.0 = 新功能
      2.0.0 = 重大变更
```

**重要**: 包名标识 C# 兼容性，版本号标识 Python 包迭代

## 开发历程

### 已完成的关键工作

1. **核心实现** (2026-02-03)
   - 完整的协议实现（18 种数据包类型）
   - 365 个单元测试（100% 通过率）
   - C# 互操作性验证（38/38 测试通过）

2. **Bug 修复**
   - NetPacket.py 的 IntEnum 判断问题
     ```python
     # 修复前
     if isinstance(size_or_property, PacketProperty):  # ❌
     # 修复后
     try:
         prop = PacketProperty(size_or_property)  # ✅
     ```

3. **PyPI 发布准备**
   - 包重命名: `litenetlib-python` → `litenetlib-0952`
   - 版本号: `0.9.5.2` → `1.0.0` (独立版本体系)
   - README 合规化：移除开发上下文，专注 v0.9.5.2
   - 添加原作者致谢和许可证说明

4. **发布流程**
   - TestPyPI: https://test.pypi.org/project/litenetlib-0952/1.0.0/
   - PyPI: https://pypi.org/project/litenetlib-0952/1.0.0/
   - 所有测试通过 (7/7 组，100%)

## 测试验证

### 测试套件

```
tests/
├── test_constants.py           # 协议常量测试
├── test_packet.py              # 数据包测试
├── test_serialization.py       # 序列化测试
├── test_channels.py            # 通道测试
├── test_integration.py         # 集成测试
├── test_protocol_compatibility.py  # 协议兼容性测试
└── test_events.py              # 事件系统测试
```

### 关键测试结果

- 单元测试: 365/365 通过 (100%)
- 二进制兼容性: 38/38 通过 (100%)
- TestPyPI 验证: 7/7 测试组通过

### 运行测试

```bash
# 全部测试
python -m pytest tests/ -v

# 跳过集成测试
python -m pytest tests/ -m "not integration"

# TestPyPI 安装测试
python test_testpypi_install.py
```

## 发布流程

### 更新发布

```bash
# 1. 更新版本号
# - setup.py
# - pyproject.toml
# - README.md

# 2. 构建包
rm -rf dist build *.egg-info
python -m build

# 3. 检查包
python -m twine check dist/*

# 4. 先发布到 TestPyPI 测试
python -m twine upload --repository testpypi --disable-progress-bar dist/litenetlib_0952-*

# 5. 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ litenetlib-0952

# 6. 发布到正式 PyPI
python -m twine upload --disable-progress-bar dist/litenetlib_0952-*
```

### 发布工具

- `upload_testpypi.bat` - 上传到 TestPyPI
- `upload_pypi.bat` - 上传到 PyPI
- `test_testpypi_install.py` - TestPyPI 安装验证测试

## 已知问题和注意事项

### 关键修复记录

1. **NetPacket IntEnum 判断**
   - 问题: `isinstance(size_or_property, PacketProperty)` 对 IntEnum 不工作
   - 解决: 使用 `try: PacketProperty(value)` 检测

2. **Windows 控制台 UTF-8 编码**
   - 问题: 中文和 Unicode 符号显示乱码
   - 解决: 测试脚本开头添加
     ```python
     if sys.platform == 'win32':
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
     ```

3. **Twine 进度条编码问题**
   - 问题: Windows 下 Unicode 字符导致崩溃
   - 解决: 添加 `--disable-progress-bar` 标志

## 合规性

### 原作者致谢

```
C# 原版 LiteNetLib
- 原作者: RevenantX (Hubert "LHub" Tonneau)
- 原版仓库: https://github.com/RevenantX/LiteNetLib
- 版本: v0.9.5.2
- 许可: MIT
```

本项目是**非官方 Python 移植版本**，保持与原版相同的 MIT 许可证。

## 使用示例

### 基本用法

```python
from litenetlib import LiteNetManager, EventBasedNetListener
from litenetlib.core.constants import DeliveryMethod

# 创建监听器
listener = EventBasedNetListener()

@listener.on_peer_connected
def on_connected(peer):
    print(f"Connected: {peer.address}")

@listener.on_network_receive
def on_receive(peer, reader, channel_id, delivery_method):
    msg = reader.get_string()
    print(f"Received: {msg}")

# 创建管理器
manager = LiteNetManager(listener)

# 作为服务器
manager.start(9050)

# 作为客户端
peer = manager.connect("127.0.0.1", 9050)

# 发送数据
peer.send(data, DeliveryMethod.RELIABLE_ORDERED)
```

## 维护要点

### 添加新功能时

1. 保持与 C# v0.9.5.2 的二进制兼容性
2. 添加对应的单元测试
3. 更新版本号（遵循语义化版本）
4. 更新 README.md

### Bug 修复时

1. 创建重现问题的测试用例
2. 修复 bug
3. 确保所有测试通过
4. 发布 patch 版本（如 1.0.1）

### 兼容性原则

**不破坏兼容性**: 任何更改都必须保持与已发布版本的 API 兼容性

## 相关链接

- GitHub: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2
- PyPI: https://pypi.org/project/litenetlib-0952/
- TestPyPI: https://test.pypi.org/project/litenetlib-0952/
- C# 原版: https://github.com/RevenantX/LiteNetLib
- Issue 追踪: https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues

## 最后更新

- 日期: 2026-02-03
- 版本: 1.0.0
- 状态: 生产就绪，已发布到 PyPI
