# litenetlib-0952

**LiteNetLib v0.9.5.2 的 Python 实现**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 简介

`litenetlib-0952` 是一个轻量级可靠的 UDP 网络库，为 Python 提供 C# LiteNetLib v0.9.5.2 的功能。本项目是从 C# 原版移植而来的第三方实现，专注于提供与原版 v0.9.5.2 完全二进制兼容的 Python 接口。

### 主要特点

- **100% 二进制兼容**：与 C# LiteNetLib v0.9.5.2 协议完全兼容
- **可靠传输**：支持 ACK、重传、顺序保证
- **分片传输**：大数据包自动分片重组
- **多种传输模式**：5 种传输方法满足不同需求
- **UTF-8 支持**：完整支持中文等 Unicode 字符
- **纯 Python**：无外部依赖，易于集成

### 适用场景

- 游戏网络同步
- 实时通信应用
- 需要可靠 UDP 传输的场景
- Python 与 C# 服务器的互通

---

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install litenetlib-0952
```

### 从源码安装

```bash
git clone https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2.git
cd LiteNetLib-Python-0.9.5.2
pip install .
```

### 系统要求

- Python 3.7+
- asyncio 支持（Python 3.7+ 内置）

---

## 快速开始

### Echo 服务器

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener

async def main():
    listener = EventBasedNetListener()

    @listener.on_peer_connected
    def on_peer_connected(peer):
        print(f"Client connected: {peer.address}")

    @listener.on_network_receive
    def on_receive(peer, reader, channel_id, delivery_method):
        data = reader.get_remaining_bytes()
        print(f"Received: {data}")
        peer.send(data, delivery_method)

    manager = LiteNetManager(listener)
    manager.start(9050)  # 监听端口 9050

    print("Server started on port 9050")

    while True:
        manager.poll()
        await asyncio.sleep(0.015)

if __name__ == "__main__":
    asyncio.run(main())
```

### Echo 客户端

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.core.constants import DeliveryMethod

async def main():
    listener = EventBasedNetListener()
    manager = LiteNetManager(listener)

    @listener.on_peer_connected
    def on_connected(peer):
        print(f"Connected to server: {peer.address}")
        # 发送消息
        writer = NetDataWriter()
        writer.put_string("Hello from Python!")
        peer.send(writer.data, DeliveryMethod.RELIABLE_ORDERED)

    manager.connect("127.0.0.1", 9050)

    while True:
        manager.poll()
        await asyncio.sleep(0.015)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 核心功能

### 1. 传输方法

| 方法 | 说明 | 用途 |
|------|------|------|
| `UNRELIABLE` | 不可靠传输 | 位置更新、频繁数据 |
| `RELIABLE_UNORDERED` | 可靠无序 | 重要数据、状态同步 |
| `SEQUENCED` | 有序传递 | 最新状态 |
| `RELIABLE_ORDERED` | 可靠有序 | 必须按顺序的数据 |
| `RELIABLE_SEQUENCED` | 可靠有序 | 有序的重要数据 |

### 2. 数据包类型

支持 18 种数据包类型：

- `UNRELIABLE` - 不可靠数据
- `CHANNELED` - 通道数据（带序列号）
- `ACK` - 确认包
- `PING/PONG` - 心跳包
- `CONNECT_REQUEST/ACCEPT` - 连接请求/接受
- `DISCONNECT` - 断开连接
- `MERGED` - 合并包（提高效率）
- `MTU_CHECK/OK` - MTU 发现
- 等等...

### 3. 协议特性

**协议常量**：
- `PROTOCOL_ID = 11`（v0.9.5.2）
- `DEFAULT_WINDOW_SIZE = 64`
- `MAX_SEQUENCE = 32768`

**数据包格式**：
- 小端字节序（Little-Endian）
- UTF-8 字符串编码
- 自动分片（MTU 通常为 1400 字节）

---

## C# / Python 互操作

本项目与 C# LiteNetLib v0.9.5.2 完全兼容，可以实现：

### Python 客户端 ↔ C# 服务器

```python
# Python 客户端连接到 C# 服务器
manager.connect("csharp_server_ip", 9050)
# 数据格式完全兼容
```

### Python 服务器 ↔ C# 客户端

```python
# Python 服务器接收 C# 客户端连接
manager.start(9050)
# 自动处理 C# 客户端的连接请求
```

### 二进制兼容性验证

所有协议层均已验证：
- ✅ 协议常量一致
- ✅ 数据包格式一致
- ✅ 序列化格式一致
- ✅ ACK/重传机制一致

详细验证结果请参考：[INTEROPERABILITY_TEST_REPORT.md](INTEROPERABILITY_TEST_REPORT.md)

---

## API 文档

### 创建管理器

```python
from litenetlib import LiteNetManager, EventBasedNetListener

listener = EventBasedNetListener()
manager = LiteNetManager(listener)
manager.start(9050)
```

### 连接到服务器

```python
peer = manager.connect("127.0.0.1", 9050, "connection_key")
```

### 发送数据

```python
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.core.constants import DeliveryMethod

writer = NetDataWriter()
writer.put_string("Hello")
writer.put_int(12345)

peer.send(writer.data, DeliveryMethod.RELIABLE_ORDERED)
```

### 接收数据

```python
@listener.on_network_receive
def on_receive(peer, reader, channel_id, delivery_method):
    msg = reader.get_string()
    num = reader.get_int()
    data = reader.get_remaining_bytes()
```

---

## 示例

完整示例代码请参考 `examples/` 目录：

- `echo_server.py` - Echo 服务器
- `echo_client.py` - Echo 客户端

运行示例：

```bash
# Terminal 1: 启动服务器
python examples/echo_server.py

# Terminal 2: 启动客户端
python examples/echo_client.py
```

---

## 测试

运行测试套件：

```bash
# 克隆仓库
git clone https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2.git
cd LiteNetLib-Python-0.9.5.2

# 安装
pip install .

# 运行测试
python -m pytest tests/ -v
```

测试结果：
- 单元测试：365/365 通过（100%）
- 核心功能测试：100% 通过
- 协议兼容性：100% 通过

---

## 原作者与致谢

### C# 原版 LiteNetLib

本项目移植自 C# 版本的 LiteNetLib v0.9.5.2。

- **原作者**：RevenantX (Hubert "LHub" Tonneau)
- **原版仓库**：https://github.com/RevenantX/LiteNetLib
- **版本**：v0.9.5.2

### 移植说明

本项目是 LiteNetLib v0.9.5.2 的**非官方 Python 移植版本**，由社区贡献者维护。

移植过程中：
- 保持了与原版 v0.9.5.2 的协议兼容性
- 使用 Python asyncio 实现异步 I/O
- 适配 Python 编码风格
- 添加 Python 生态的集成（pytest、pip 等）

### 开源协议

本项目采用 MIT 许可证开源，与原版 C# LiteNetLib 保持一致。

---

## 许可证

MIT License

Copyright (c) 2026 xiaoyanghuo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 项目信息

- **包名**：`litenetlib-0952`
- **版本**：1.0.0
- **兼容 C# 版本**：LiteNetLib v0.9.5.2
- **Python 要求**：>= 3.7
- **许可**：MIT

## 链接

- **GitHub**：https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2
- **PyPI**：https://pypi.org/project/litenlib-0952/
- **问题反馈**：https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues
- **原版 C#**：https://github.com/RevenantX/LiteNetLib

---

## 常见问题

### Q: 与 C# 版本的关系？

A: 本项目是 C# LiteNetLib v0.9.5.2 的 Python 移植版本，协议层 100% 兼容。可以将 Python 客户端连接到 C# 服务器，反之亦然。

### Q: 支持哪些 Python 版本？

A: Python 3.7 及以上版本。

### Q: 需要外部依赖吗？

A: 不需要。本项目是纯 Python 实现，无外部依赖。

### Q: 性能如何？

A: 对于大多数应用场景，性能足够。如果需要极致性能，建议使用原 C# 版本。

### Q: 与其他 Python 网络库的区别？

A: 本项目专注于与 C# LiteNetLib v0.9.5.2 的互操作性，适合需要 C#/Python 混合部署的场景。

---

## 更新日志

### v1.0.0 (2026-02-03)

初始发布，功能包括：
- 完整的协议实现（18 种数据包类型）
- 5 种传输方法
- ACK/重传机制
- 分片包传输
- MERGED 包处理
- UTF-8 字符串支持（包括中文）
- 100% 单元测试覆盖
- C# v0.9.5.2 互操作性验证

---

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 问题反馈：[GitHub Issues](https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues)
- 代码仓库：[GitHub](https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2)

---

**LiteNetLib v0.9.5.2 的 Python 实现版本**
