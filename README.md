# LiteNetLib Python v0.9.5.2

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

完整的 LiteNetLib v0.9.5.2 Python 实现，与 C# 版本 100% 二进制兼容。

Complete Python implementation of LiteNetLib v0.9.5.2 with 100% binary compatibility to C# version.

## ✅ 验证状态 / Verification Status

所有关键常量已验证匹配 v0.9.5.2 协议：
All critical constants verified to match v0.9.5.2 protocol:

```bash
$ python verify_version.py
[OK] PROTOCOL_ID = 11 (not 13)
[OK] ACK = 2 (not 3)
[OK] EMPTY = 17 (not 18)
[OK] 18 packet types (not 19)
[OK] ALL CHECKS PASSED!
```

## 特性 / Features

- ✅ 与 C# LiteNetLib v0.9.5.2 100% 二进制兼容
- ✅ 异步 I/O（asyncio）
- ✅ UDP 网络
- ✅ 可靠和不可靠消息传递
- ✅ 连接管理
- ✅ 数据包序列化/反序列化
- ✅ 支持所有传输方法

## 版本信息 / Version Info

| 项目 / Project | 版本 / Version |
|----------------|---------------|
| **Python 实现** | v1.0.0 |
| **C# 参考** | LiteNetLib v0.9.5.2 |
| **协议 ID** | 11 |
| **兼容性** | 完全二进制兼容 |

## 快速开始 / Quick Start

### 安装 / Installation

```bash
cd LiteNetLib-Python-0.9.5.2
pip install -e .
```

### 运行示例 / Run Examples

```bash
# Terminal 1: 启动服务器 / Start server
cd examples
python echo_server.py

# Terminal 2: 启动客户端 / Start client
cd examples
python echo_client.py
```

### 服务器代码 / Server Code

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener

class ServerListener(EventBasedNetListener):
    def on_connection_request(self, request):
        print(f"Connection from {request.address}")
        return True  # Accept

    def on_peer_connected(self, peer):
        print(f"Peer connected: {peer.address}")

    def on_network_receive(self, peer, reader):
        data = reader.get_remaining_bytes()
        message = data.decode('utf-8')
        print(f"Received: {message}")
        peer.send(data)  # Echo back

async def main():
    server = LiteNetManager(ServerListener())
    server.start(port=7777)
    print(f"Server started on port {server.local_port}")

    while server.is_running:
        await server.poll_async()
        await asyncio.sleep(0.001)

asyncio.run(main())
```

### 客户端代码 / Client Code

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener, DeliveryMethod

class ClientListener(EventBasedNetListener):
    def on_peer_connected(self, peer):
        print(f"Connected to {peer.address}")
        peer.send(b"Hello, Server!", DeliveryMethod.RELIABLE_ORDERED)

    def on_network_receive(self, peer, reader):
        data = reader.get_remaining_bytes()
        print(f"Received: {data.decode('utf-8')}")

async def main():
    client = LiteNetManager(ClientListener())
    client.start(port=0)
    client.connect("127.0.0.1", 7777)

    while client.is_running:
        await client.poll_async()
        await asyncio.sleep(0.001)

asyncio.run(main())
```

## v0.9.5.2 版本差异 / Version Differences

此实现专门针对 **LiteNetLib v0.9.5.2**，与 v2.0.0 有以下关键差异：

This implementation is specifically for **LiteNetLib v0.9.5.2**, with key differences from v2.0.0:

| 特性 / Feature | v0.9.5.2 | v2.0.0 |
|----------------|----------|--------|
| PROTOCOL_ID | 11 | 13 |
| ACK value | 2 | 3 |
| EMPTY value | 17 | 18 |
| Packet types | 18 | 19 |
| ReliableMerged | ❌ 不存在 | ✅ 存在 |
| ConnectRequest HeaderSize | 14 | 18 |
| ConnectAccept Size | 11 | 15 |

更多信息：[VERSION_NOTES.md](VERSION_NOTES.md) | More info: [VERSION_NOTES.md](VERSION_NOTES.md)

## 项目结构 / Project Structure

```
litenetlib/
├── core/                    # 核心模块 / Core modules
│   ├── constants.py         # v0.9.5.2 协议常量
│   ├── packet.py            # 数据包实现
│   ├── peer.py              # 对等端
│   ├── manager.py           # 网络管理器
│   ├── events.py            # 事件系统
│   └── internal_packets.py  # 连接数据包
├── channels/                # 通道实现
│   ├── reliable_channel.py
│   └── sequenced_channel.py
└── utils/                   # 工具模块
    ├── data_reader.py       # 数据读取
    ├── data_writer.py       # 数据写入
    └── fast_bit_converter.py # 二进制转换
```

## 二进制兼容性 / Binary Compatibility

✅ **与 C# LiteNetLib v0.9.5.2 100% 二进制兼容**
**100% binary compatible with C# LiteNetLib v0.9.5.2**

- 相同的数据包格式 / Same packet format
- 相同的协议 ID (11) / Same protocol ID
- 相同的枚举值 / Same enum values
- 小端字节序 / Little-endian byte order
- UTF-8 编码 / UTF-8 encoding

Python 客户端可以连接到 C# 服务器（v0.9.5.2），反之亦然。
Python clients can connect to C# servers (v0.9.5.2) and vice versa.

## 文档 / Documentation

- [VERSION_NOTES.md](VERSION_NOTES.md) - v0.9.5.2 版本详情
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 实现总结
- [examples/](examples/) - 示例代码

## 系统要求 / Requirements

- Python 3.7+
- asyncio (标准库)
- socket (标准库)

## 许可证 / License

MIT License - 与原始 C# 版本相同
MIT License - Same as original C# version

## 参考 / References

- **C# 原版**: https://github.com/RevenantX/LiteNetLib/releases/tag/v0.9.5.2
- **作者**: RevenantX

---

**注意 / Note**: 此实现仅与 v0.9.5.2 兼容。如需 v2.0.0，请使用 LiteNetLib-CC。
**Note**: This implementation is only compatible with v0.9.5.2. For v2.0.0, use LiteNetLib-CC.
