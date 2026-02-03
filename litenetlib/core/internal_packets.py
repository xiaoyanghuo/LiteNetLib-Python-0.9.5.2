"""
Internal connection packets for LiteNetLib v0.9.5.2 protocol.
LiteNetLib v0.9.5.2 内部连接数据包

This module contains the internal packet structures used for connection
establishment and management. These packets are part of the core protocol
and must match the C# implementation byte-for-byte.

本模块包含用于连接建立和管理的内部数据包结构。
这些数据包是核心协议的一部分，必须与 C# 实现逐字节匹配。

Ported from: LiteNetLib/NetPacket.cs (v0.9.5.2)
"""

import struct
import socket
from typing import Optional, Tuple
from litenetlib.core.constants import NetConstants, PacketProperty
from litenetlib.core.packet import NetPacket
from litenetlib.utils.fast_bit_converter import FastBitConverter


class NetConnectRequestPacket:
    """
    Connection request packet / 连接请求数据包

    Sent by client to server when initiating a connection.
    客户端向服务器发起连接时发送。

    C# Reference: NetConnectRequestPacket (v0.9.5.2)
    Structure (HeaderSize = 14) / 结构:
    - Byte 0: Property (ConnectRequest) + connNum / 属性 + 连接号
    - Bytes 1-4: ProtocolId (int, little-endian) = 11 / 协议 ID
    - Bytes 5-12: ConnectionTime (long, little-endian) / 连接时间
    - Byte 13: Address size (16 for IPv4, 28 for IPv6) / 地址大小
    - Bytes 14+: Target address bytes / 目标地址字节
    - Bytes 14+addrSize+: Additional connection data / 额外连接数据
    """

    HEADER_SIZE = 14

    __slots__ = ('connection_time', 'connection_number', 'target_address', 'data')

    def __init__(
        self,
        connection_time: int,
        connection_number: int,
        target_address: bytes,
        data: Optional[bytes] = None
    ):
        """
        Create connection request packet / 创建连接请求数据包。

        Args:
            connection_time: Connection timestamp (long, ticks) / 连接时间戳
            connection_number: Connection number (0-3) / 连接编号
            target_address: Serialized target address bytes / 序列化的目标地址字节
            data: Additional connection data / 额外连接数据
        """
        self.connection_time = connection_time
        self.connection_number = connection_number
        self.target_address = target_address
        self.data = data or b''

    @staticmethod
    def get_protocol_id(packet: NetPacket) -> int:
        """
        Extract protocol ID from connection request packet.
        从连接请求数据包中提取协议 ID。

        Args:
            packet: Connection request packet / 连接请求数据包

        Returns:
            Protocol ID (should be 11 for v0.9.5.2) / 协议 ID（v0.9.5.2 应为 11）

        C# Equivalent: GetProtocolId(NetPacket packet)
        """
        # C#: BitConverter.ToInt32(packet.RawData, 1)
        return struct.unpack_from('<I', packet._data, 1)[0]

    @staticmethod
    def from_data(packet: NetPacket) -> Optional['NetConnectRequestPacket']:
        """
        Parse connection request from packet / 从数据包解析连接请求。

        Args:
            packet: Received packet / 接收到的数据包

        Returns:
            Parsed connection request, or None if invalid / 解析的连接请求，无效则返回 None

        C# Equivalent: FromData(NetPacket packet)
        """
        conn_num = packet.connection_number
        if conn_num >= NetConstants.MAX_CONNECTION_NUMBER:
            return None

        # Get connection time (long at offset 5)
        # C#: BitConverter.ToInt64(packet.RawData, 5)
        connection_time = struct.unpack_from('<q', packet._data, 5)[0]

        # Get target address size (byte at offset 13)
        # C#: int addrSize = packet.RawData[13]
        addr_size = packet._data[13]
        if addr_size != 16 and addr_size != 28:
            return None

        # Extract target address bytes
        # C#: Buffer.BlockCopy(packet.RawData, 14, addressBytes, 0, addrSize)
        if packet.size < NetConnectRequestPacket.HEADER_SIZE + addr_size:
            return None

        address_bytes = bytes(packet._data[
            NetConnectRequestPacket.HEADER_SIZE:
            NetConnectRequestPacket.HEADER_SIZE + addr_size
        ])

        # Extract additional data if present
        # C#: reader.SetSource(packet.RawData, HeaderSize + addrSize, packet.Size)
        data = b''
        if packet.size > NetConnectRequestPacket.HEADER_SIZE + addr_size:
            data = bytes(packet._data[
                NetConnectRequestPacket.HEADER_SIZE + addr_size:
                packet.size
            ])

        return NetConnectRequestPacket(
            connection_time=connection_time,
            connection_number=conn_num,
            target_address=address_bytes,
            data=data
        )

    @staticmethod
    def make(
        connect_data: bytes,
        address_bytes: bytes,
        connect_id: int
    ) -> NetPacket:
        """
        Create connection request packet / 创建连接请求数据包。

        Args:
            connect_data: Additional connection data to send / 要发送的额外连接数据
            address_bytes: Serialized target address (SocketAddress) / 序列化的目标地址
            connect_id: Connection ID / 连接 ID

        Returns:
            Constructed packet ready to send / 构造好的可发送数据包

        C# Equivalent: Make(NetDataWriter, SocketAddress, long)
        """
        # Create initial packet with space for data
        # C#: var packet = new NetPacket(PacketProperty.ConnectRequest, connectData.Length+addressBytes.Size)
        packet = NetPacket(PacketProperty.CONNECT_REQUEST, len(connect_data) + len(address_bytes))

        # Write protocol ID (offset 1)
        # C#: FastBitConverter.GetBytes(packet.RawData, 1, NetConstants.ProtocolId)
        FastBitConverter.get_bytes_uint(packet._data, 1, NetConstants.PROTOCOL_ID)

        # Write connection ID (offset 5)
        # C#: FastBitConverter.GetBytes(packet.RawData, 5, connectId)
        FastBitConverter.get_bytes_long(packet._data, 5, connect_id)

        # Write address size (offset 13)
        # C#: packet.RawData[13] = (byte)addressBytes.Size
        packet._data[13] = len(address_bytes) & 0xFF

        # Write address bytes
        # C#: for (int i = 0; i < addressBytes.Size; i++) packet.RawData[14+i] = addressBytes[i]
        addr_start = NetConnectRequestPacket.HEADER_SIZE
        packet._data[addr_start:addr_start + len(address_bytes)] = address_bytes

        # Write connection data
        # C#: Buffer.BlockCopy(connectData.Data, 0, packet.RawData, 14+addressBytes.Size, connectData.Length)
        if connect_data:
            data_start = addr_start + len(address_bytes)
            packet._data[data_start:data_start + len(connect_data)] = connect_data

        return packet


class NetConnectAcceptPacket:
    """
    Connection accept packet / 连接接受数据包

    Sent by server to client to accept a connection.
    服务器向客户端发送以接受连接。

    C# Reference: NetConnectAcceptPacket (v0.9.5.2)
    Structure (Size = 11) / 结构:
    - Byte 0: Property (ConnectAccept) / 属性
    - Bytes 1-8: ConnectionId (long, little-endian) / 连接 ID
    - Byte 9: ConnectionNumber (0-3) / 连接编号
    - Byte 10: IsReused (0 or 1) / 是否重用
    """

    SIZE = 11

    __slots__ = ('connection_id', 'connection_number', 'is_reused')

    def __init__(
        self,
        connection_id: int,
        connection_number: int,
        is_reused: bool = False
    ):
        """
        Create connection accept packet / 创建连接接受数据包。

        Args:
            connection_id: Connection ID (long) / 连接 ID
            connection_number: Connection number (0-3) / 连接编号
            is_reused: Whether peer ID was reused / 是否重用了对等端 ID
        """
        self.connection_id = connection_id
        self.connection_number = connection_number
        self.is_reused = is_reused

    @staticmethod
    def from_data(packet: NetPacket) -> Optional['NetConnectAcceptPacket']:
        """
        Parse connection accept from packet / 从数据包解析连接接受。

        Args:
            packet: Received packet / 接收到的数据包

        Returns:
            Parsed connection accept, or None if invalid / 解析的连接接受，无效则返回 None

        C# Equivalent: FromData(NetPacket packet)
        """
        if packet.size > NetConnectAcceptPacket.SIZE:
            return None

        # Get connection ID (long at offset 1)
        # C#: long connectionId = BitConverter.ToInt64(packet.RawData, 1)
        connection_id = struct.unpack_from('<q', packet._data, 1)[0]

        # Get connection number (byte at offset 9)
        # C#: byte connectionNumber = packet.RawData[9]
        connection_number = packet._data[9]
        if connection_number >= NetConstants.MAX_CONNECTION_NUMBER:
            return None

        # Get reuse flag (byte at offset 10)
        # C#: byte isReused = packet.RawData[10]
        is_reused = packet._data[10]
        if is_reused > 1:
            return None

        return NetConnectAcceptPacket(
            connection_id=connection_id,
            connection_number=connection_number,
            is_reused=(is_reused == 1)
        )

    @staticmethod
    def make(
        connect_id: int,
        connect_num: int,
        reused_peer: bool = False
    ) -> NetPacket:
        """
        Create connection accept packet / 创建连接接受数据包。

        Args:
            connect_id: Connection ID (long) / 连接 ID
            connect_num: Connection number (0-3) / 连接编号
            reused_peer: Whether this is a reused peer / 是否为重用的对等端

        Returns:
            Constructed packet ready to send / 构造好的可发送数据包

        C# Equivalent: Make(long, byte, bool)
        """
        # Create packet (no additional data needed)
        # C#: var packet = new NetPacket(PacketProperty.ConnectAccept, 0)
        packet = NetPacket(PacketProperty.CONNECT_ACCEPT, 0)

        # Write connection ID (offset 1)
        # C#: FastBitConverter.GetBytes(packet.RawData, 1, connectId)
        FastBitConverter.get_bytes_long(packet._data, 1, connect_id)

        # Write connection number (offset 9)
        # C#: packet.RawData[9] = connectNum
        packet._data[9] = connect_num & 0xFF

        # Write reuse flag (offset 10)
        # C#: packet.RawData[10] = (byte)(reusedPeer ? 1 : 0)
        packet._data[10] = 1 if reused_peer else 0

        return packet


# Helper functions for address serialization / 地址序列化辅助函数

def serialize_address(host: str, port: int) -> bytes:
    """
    Serialize an IP address and port to bytes.
    将 IP 地址和端口序列化为字节。

    Args:
        host: IP address string / IP 地址字符串
        port: Port number / 端口号

    Returns:
        Serialized address bytes (SocketAddress format) / 序列化的地址字节

    C# Equivalent: SocketAddress serialization
    """
    try:
        # Try IPv4 first / 先尝试 IPv4
        addr_bytes = socket.inet_pton(socket.AF_INET, host)
        # Format for IPv4: [4 bytes address][2 bytes port]
        # IPv4 格式：[4 字节地址][2 字节端口]
        return addr_bytes + struct.pack('<H', port)
    except socket.error:
        try:
            # Try IPv6 / 尝试 IPv6
            addr_bytes = socket.inet_pton(socket.AF_INET6, host)
            # Format for IPv6: [16 bytes address][2 bytes port]
            # IPv6 格式：[16 字节地址][2 字节端口]
            return addr_bytes + struct.pack('<H', port)
        except socket.error:
            raise ValueError(f"Invalid address: {host}")


def deserialize_address(data: bytes, offset: int = 0) -> Tuple[str, int, str]:
    """
    Deserialize an IP address and port from bytes.
    从字节反序列化 IP 地址和端口。

    Args:
        data: Serialized address bytes / 序列化的地址字节
        offset: Starting offset in data / 数据中的起始偏移

    Returns:
        Tuple of (host, port, family) where family is 'IPv4' or 'IPv6'
        (主机, 端口, 协议族) 元组，协议族为 'IPv4' 或 'IPv6'

    C# Equivalent: SocketAddress deserialization
    """
    # Determine format from size / 根据大小确定格式
    size = len(data) - offset
    if size == 6:
        # IPv4: 4 bytes + 2 bytes port / IPv4：4 字节 + 2 字节端口
        host = socket.inet_ntop(socket.AF_INET, data[offset:offset+4])
        port = struct.unpack_from('<H', data, offset + 4)[0]
        return host, port, 'IPv4'
    elif size == 18:
        # IPv6: 16 bytes + 2 bytes port / IPv6：16 字节 + 2 字节端口
        host = socket.inet_ntop(socket.AF_INET6, data[offset:offset+16])
        port = struct.unpack_from('<H', data, offset + 16)[0]
        return host, port, 'IPv6'
    else:
        raise ValueError(f"Invalid serialized address size: {size}")
