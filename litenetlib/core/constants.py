"""
LiteNetLib 网络常量和枚举 / Network constants and enumerations for LiteNetLib v0.9.5.2

本模块定义了所有网络通信中使用的常量和枚举类型。
This module defines all constants and enumeration types used in network communication.

与 C# LiteNetLib v0.9.5.2 完全兼容 / Fully compatible with C# LiteNetLib v0.9.5.2.
"""

from enum import IntEnum
from typing import List


class PacketProperty(IntEnum):
    """
    数据包属性类型 / Packet property types stored in the first byte of packet header

    v0.9.5.2 版本枚举值（无 ReliableMerged）
    v0.9.5.2 enum values (no ReliableMerged)
    """
    UNRELIABLE = 0
    CHANNELED = 1
    ACK = 2
    PING = 3
    PONG = 4
    CONNECT_REQUEST = 5
    CONNECT_ACCEPT = 6
    DISCONNECT = 7
    UNCONNECTED_MESSAGE = 8
    MTU_CHECK = 9
    MTU_OK = 10
    BROADCAST = 11
    MERGED = 12
    SHUTDOWN_OK = 13
    PEER_NOT_FOUND = 14
    INVALID_PROTOCOL = 15
    NAT_MESSAGE = 16
    EMPTY = 17
    # Total is implicit (18)


class DeliveryMethod(IntEnum):
    """
    数据传输方法 / Sending method type

    定义数据包如何被传输到对等端。
    Defines how packets are delivered to the peer.

    传输方法说明 / Delivery method details:
    - UNRELIABLE (不可靠): 可丢包、可重复、无序 / Can be dropped, duplicated, arrive out of order
    - RELIABLE_UNORDERED (可靠无序): 不丢包、不重复、无序 / Won't be dropped/duplicated, can arrive out of order
    - SEQUENCED (有序): 可丢包、不重复、有序 / Can be dropped, won't be duplicated, arrives in order
    - RELIABLE_ORDERED (可靠有序): 不丢包、不重复、有序 / Won't be dropped/duplicated, arrives in order
    - RELIABLE_SEQUENCED (可靠序列): 仅最后一个包可靠 / Only last packet reliable, cannot be fragmented

    ⚠️ 重要 / IMPORTANT:
    枚举值必须与 C# LiteNetLib v0.9.5.2 的 DeliveryMethod 枚举完全匹配以实现互操作性。
    Values MUST match C# LiteNetLib v0.9.5.2 DeliveryMethod enum for interoperability.

    C# 参考代码 / C# Reference (NetConstants.cs):
        Unreliable = 4
        ReliableUnordered = 0
        Sequenced = 1
        ReliableOrdered = 2
        ReliableSequenced = 3
    """
    UNRELIABLE = 4
    RELIABLE_UNORDERED = 0
    SEQUENCED = 1
    RELIABLE_ORDERED = 2
    RELIABLE_SEQUENCED = 3


class DisconnectReason(IntEnum):
    """
    断开连接的原因 / Reason for peer disconnection

    定义对等端断开连接时的原因代码。
    Defines the reason code when a peer disconnects.
    """
    CONNECTION_FAILED = 0
    TIMEOUT = 1
    HOST_UNREACHABLE = 2
    NETWORK_UNREACHABLE = 3
    REMOTE_CONNECTION_CLOSE = 4
    DISCONNECT_PEER_CALLED = 5
    CONNECTION_REJECTED = 6
    INVALID_PROTOCOL = 7
    UNKNOWN_HOST = 8
    RECONNECT = 9
    PEER_TO_PEER_CONNECTION = 10
    PEER_NOT_FOUND = 11


class UnconnectedMessageType(IntEnum):
    """
    无连接消息类型 / Type of unconnected message

    定义未连接状态下发送的消息类型。
    Defines the type of message sent in unconnected state.
    """
    BASIC_MESSAGE = 0
    BROADCAST = 1


class NetConstants:
    """
    网络常量和配置值 / Network constants and configuration values

    包含所有网络通信中使用的常量配置。
    Contains all constant configurations used in network communication.

    v0.9.5.2 特定值 / v0.9.5.2 specific values:
    - ProtocolId = 11
    - PossibleMtu has 7 options
    """

    # 可调优参数 / Can be tuned
    DEFAULT_WINDOW_SIZE: int = 64
    SOCKET_BUFFER_SIZE: int = 1024 * 1024  # 1 MB
    SOCKET_TTL: int = 255

    # Packet headers
    HEADER_SIZE: int = 1
    CHANNELED_HEADER_SIZE: int = 4
    FRAGMENT_HEADER_SIZE: int = 6
    FRAGMENTED_HEADER_TOTAL_SIZE: int = CHANNELED_HEADER_SIZE + FRAGMENT_HEADER_SIZE

    # Sequence numbers
    MAX_SEQUENCE: int = 32768
    HALF_MAX_SEQUENCE: int = MAX_SEQUENCE // 2

    # Protocol
    PROTOCOL_ID: int = 11  # v0.9.5.2 uses ProtocolId = 11
    MAX_UDP_HEADER_SIZE: int = 68

    # Possible MTU values (v0.9.5.2 has 7 options)
    POSSIBLE_MTU: List[int] = [
        576 - MAX_UDP_HEADER_SIZE,   # Minimal (RFC 1191)
        1024,                        # Most games standard
        1232 - MAX_UDP_HEADER_SIZE,  #
        1460 - MAX_UDP_HEADER_SIZE,  # Google Cloud
        1472 - MAX_UDP_HEADER_SIZE,  # VPN
        1492 - MAX_UDP_HEADER_SIZE,  # Ethernet with LLC and SNAP, PPPoE (RFC 1042)
        1500 - MAX_UDP_HEADER_SIZE,  # Ethernet II (RFC 1191)
    ]

    # Max possible single packet size
    INITIAL_MTU: int = POSSIBLE_MTU[0]
    MAX_PACKET_SIZE: int = POSSIBLE_MTU[-1]
    MAX_UNRELIABLE_DATA_SIZE: int = MAX_PACKET_SIZE - HEADER_SIZE

    # Peer specific
    MAX_CONNECTION_NUMBER: int = 4

    # Packet pool
    PACKET_POOL_SIZE: int = 1000


# Header sizes for each packet property
# Must match C# NetPacket.cs HeaderSizes exactly for v0.9.5.2
_HEADER_SIZES = {
    PacketProperty.UNRELIABLE: NetConstants.HEADER_SIZE,
    PacketProperty.CHANNELED: NetConstants.CHANNELED_HEADER_SIZE,
    PacketProperty.ACK: NetConstants.CHANNELED_HEADER_SIZE,
    PacketProperty.PING: NetConstants.HEADER_SIZE + 2,
    PacketProperty.PONG: NetConstants.HEADER_SIZE + 10,
    PacketProperty.CONNECT_REQUEST: 18,  # NetConnectRequestPacket.HeaderSize
    PacketProperty.CONNECT_ACCEPT: 15,   # NetConnectAcceptPacket.Size
    PacketProperty.DISCONNECT: NetConstants.HEADER_SIZE + 8,
    PacketProperty.UNCONNECTED_MESSAGE: NetConstants.HEADER_SIZE,
    PacketProperty.MTU_CHECK: NetConstants.HEADER_SIZE + 2,
    PacketProperty.MTU_OK: NetConstants.HEADER_SIZE,
    PacketProperty.BROADCAST: NetConstants.HEADER_SIZE,
    PacketProperty.MERGED: NetConstants.HEADER_SIZE,
    PacketProperty.SHUTDOWN_OK: NetConstants.HEADER_SIZE,
    PacketProperty.PEER_NOT_FOUND: NetConstants.HEADER_SIZE,
    PacketProperty.INVALID_PROTOCOL: NetConstants.HEADER_SIZE,
    PacketProperty.NAT_MESSAGE: NetConstants.HEADER_SIZE,
    PacketProperty.EMPTY: NetConstants.HEADER_SIZE,
}


def get_header_size(prop: PacketProperty) -> int:
    """Get header size for a specific packet property."""
    return _HEADER_SIZES.get(prop, NetConstants.HEADER_SIZE)
