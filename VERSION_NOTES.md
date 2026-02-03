# LiteNetLib Python v0.9.5.2

## 概述 / Overview

完整的 LiteNetLib v0.9.5.2 Python 实现，与 C# 版本 100% 二进制兼容。

Complete Python implementation of LiteNetLib v0.9.5.2 with 100% binary compatibility to C# version.

## v0.9.5.2 版本差异 / Version Differences

此实现专门针对 LiteNetLib v0.9.5.2 协议，与 v2.0.0 有以下关键差异：

This implementation is specifically for LiteNetLib v0.9.5.2 protocol, with key differences from v2.0.0:

### 1. 协议 ID / Protocol ID
- **v0.9.5.2**: `PROTOCOL_ID = 11`
- **v2.0.0**: `PROTOCOL_ID = 13`

### 2. PacketProperty 枚举值 / PacketProperty Enum Values

| 属性 / Property | v0.9.5.2 | v2.0.0 |
|----------------|----------|--------|
| ACK | 2 | 3 |
| EMPTY | 17 | 18 |
| MERGED | 12 | 13 |
| 总数 / Total | 18 | 19 |

### 3. 数据包类型 / Packet Types
- **v0.9.5.2**: 无 `ReliableMerged` 包类型 / No `ReliableMerged` packet type
- **v2.0.0**: 包含 `ReliableMerged` / Includes `ReliableMerged`

### 4. 连接数据包结构 / Connection Packet Structure

#### ConnectRequestPacket
- **v0.9.5.2**: `HeaderSize = 14` (无 peerId 字段 / no peerId field)
- **v2.0.0**: `HeaderSize = 18` (包含 peerId / includes peerId)

#### ConnectAcceptPacket
- **v0.9.5.2**: `Size = 11` (无 peerId 字段 / no peerId field)
- **v2.0.0**: `Size = 15` (包含 peerId / includes peerId)

## 项目结构 / Project Structure

```
litenetlib/
├── __init__.py              # 主模块 / Main module
├── core/                    # 核心模块 / Core modules
│   ├── constants.py         # 协议常量 / Protocol constants (v0.9.5.2)
│   ├── packet.py            # NetPacket 实现 / NetPacket implementation
│   ├── peer.py              # NetPeer 实现 / NetPeer implementation
│   ├── manager.py           # LiteNetManager 实现 / Manager implementation
│   ├── events.py            # 事件系统 / Event system
│   ├── connection_request.py # 连接请求 / Connection request
│   └── internal_packets.py  # 内部数据包 / Internal packets
├── channels/                # 通道实现 / Channel implementations
│   ├── base_channel.py      # 基础通道 / Base channel
│   ├── reliable_channel.py  # 可靠通道 / Reliable channel
│   └── sequenced_channel.py # 有序通道 / Sequenced channel
└── utils/                   # 工具模块 / Utility modules
    ├── data_reader.py       # 数据读取器 / Data reader
    ├── data_writer.py       # 数据写入器 / Data writer
    ├── fast_bit_converter.py # 快速二进制转换 / Fast binary converter
    └── net_utils.py         # 网络工具 / Network utilities

examples/
├── echo_server.py           # Echo 服务器 / Echo server
└── echo_client.py           # Echo 客户端 / Echo client
```

## 安装 / Installation

```bash
cd LiteNetLib-Python-0.9.5.2
pip install -e .
```

## 使用示例 / Usage Examples

### 服务器 / Server

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener

class MyListener(EventBasedNetListener):
    def on_connection_request(self, request):
        print(f"Connection request from {request.address}")
        return True  # 接受连接 / Accept

    def on_peer_connected(self, peer):
        print(f"Peer connected: {peer.address}")

    def on_network_receive(self, peer, reader):
        data = reader.get_remaining_bytes()
        print(f"Received: {data}")

async def main():
    listener = MyListener()
    server = LiteNetManager(listener)
    server.start(port=7777)

    while server.is_running:
        await server.poll_async()
        await asyncio.sleep(0.001)

asyncio.run(main())
```

### 客户端 / Client

```python
import asyncio
from litenetlib import LiteNetManager, EventBasedNetListener

class MyListener(EventBasedNetListener):
    def on_peer_connected(self, peer):
        print(f"Connected to {peer.address}")
        # 发送消息 / Send message
        peer.send(b"Hello, Server!")

    def on_network_receive(self, peer, reader):
        data = reader.get_remaining_bytes()
        print(f"Received: {data}")

async def main():
    listener = MyListener()
    client = LiteNetManager(listener)
    client.start(port=0)

    # 连接到服务器 / Connect to server
    client.connect("127.0.0.1", 7777)

    while client.is_running:
        await client.poll_async()
        await asyncio.sleep(0.001)

asyncio.run(main())
```

## 运行示例 / Running Examples

### 启动服务器 / Start Server

```bash
cd examples
python echo_server.py
```

### 启动客户端 / Start Client

```bash
cd examples
python echo_client.py
```

## 与 C# 互操作 / Interoperability with C#

此实现与 C# LiteNetLib v0.9.5.2 完全兼容：

This implementation is fully compatible with C# LiteNetLib v0.9.5.2:

- ✅ 相同的数据包格式 / Same packet format
- ✅ 相同的协议 ID / Same protocol ID
- ✅ 相同的枚举值 / Same enum values
- ✅ 相同的字节序（小端）/ Same byte order (little-endian)
- ✅ 相同的字符串编码（UTF-8）/ Same string encoding (UTF-8)

## 注意事项 / Notes

1. **协议版本**：此实现仅与 v0.9.5.2 兼容，不能与 v2.0.0 互通
   **Protocol Version**: This implementation is only compatible with v0.9.5.2, cannot interoperate with v2.0.0

2. **异步 I/O**：使用 asyncio，需要 Python 3.7+
   **Async I/O**: Uses asyncio, requires Python 3.7+

3. **简化实现**：某些高级功能（如 NAT 穿透）尚未实现
   **Simplified Implementation**: Some advanced features (like NAT punchthrough) are not yet implemented

## 许可证 / License

本项目遵循与 LiteNetLib 相同的许可证。

This project follows the same license as LiteNetLib.

## 参考实现 / Reference Implementation

- C# LiteNetLib v0.9.5.2: https://github.com/RevenantX/LiteNetLib
- 基于 / Based on: LiteNetLib-CC Python 实现
