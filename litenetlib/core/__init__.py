"""
Core modules for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 核心模块
"""

from .constants import (
    PacketProperty,
    DeliveryMethod,
    DisconnectReason,
    NetConstants,
    get_header_size
)
from .manager import LiteNetManager
from .peer import NetPeer, ConnectionState
from .events import EventBasedNetListener, INetEventListener
from .packet import NetPacket, NetPacketPool
from .connection_request import ConnectionRequest
from .internal_packets import (
    NetConnectRequestPacket,
    NetConnectAcceptPacket,
    serialize_address,
    deserialize_address
)

__all__ = [
    # Constants / 常量
    "PacketProperty",
    "DeliveryMethod",
    "DisconnectReason",
    "NetConstants",
    "get_header_size",

    # Manager / 管理器
    "LiteNetManager",

    # Peer / 对等端
    "NetPeer",
    "ConnectionState",

    # Events / 事件
    "EventBasedNetListener",
    "INetEventListener",

    # Packets / 数据包
    "NetPacket",
    "NetPacketPool",
    "ConnectionRequest",

    # Internal packets / 内部数据包
    "NetConnectRequestPacket",
    "NetConnectAcceptPacket",
    "serialize_address",
    "deserialize_address",
]
