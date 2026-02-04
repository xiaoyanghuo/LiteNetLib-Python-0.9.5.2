"""
LiteNetLib Python - v0.9.5.2 Implementation
LiteNetLib Python v0.9.5.2 实现

Complete Python implementation of LiteNetLib v0.9.5.2 with 100% binary compatibility.
完整的 LiteNetLib v0.9.5.2 Python 实现，100% 二进制兼容。

Key features / 主要功能:
- Compatible with C# LiteNetLib v0.9.5.2 / 与 C# LiteNetLib v0.9.5.2 兼容
- Async I/O with asyncio / 使用 asyncio 的异步 I/O
- UDP networking / UDP 网络
- Reliable and unreliable messaging / 可靠和不可靠消息传递
- Connection management / 连接管理

Version differences / 版本差异:
- PROTOCOL_ID = 11 (not 13) / 协议 ID = 11（不是 13）
- ACK = 2 (not 3) / ACK = 2（不是 3）
- EMPTY = 17 (not 18) / EMPTY = 17（不是 18）
- No ReliableMerged packet type / 无 ReliableMerged 数据包类型
"""

from .core.manager import LiteNetManager
from .core.peer import NetPeer, ConnectionState
from .core.events import EventBasedNetListener, INetEventListener
from .core.statistics import NetStatistics
from .core.constants import (
    PacketProperty,
    DeliveryMethod,
    DisconnectReason,
    NetConstants
)
from .core.packet import NetPacket, NetPacketPool
from .core.connection_request import ConnectionRequest

from .utils.data_reader import NetDataReader
from .utils.data_writer import NetDataWriter
from .utils.fast_bit_converter import FastBitConverter
from .utils.net_utils import NetUtils

__version__ = "1.0.1"
__protocol_version__ = "0.9.5.2"

__all__ = [
    # Core / 核心
    "LiteNetManager",
    "NetPeer",
    "ConnectionState",
    "EventBasedNetListener",
    "INetEventListener",
    "NetStatistics",

    # Constants / 常量
    "PacketProperty",
    "DeliveryMethod",
    "DisconnectReason",
    "NetConstants",

    # Packets / 数据包
    "NetPacket",
    "NetPacketPool",
    "ConnectionRequest",

    # Utils / 工具
    "NetDataReader",
    "NetDataWriter",
    "FastBitConverter",
    "NetUtils",
]
