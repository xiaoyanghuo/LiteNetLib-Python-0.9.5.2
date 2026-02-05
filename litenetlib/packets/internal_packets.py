"""
InternalPackets.cs 翻译（完整版）

内部包结构 - 连接请求和连接接受的包协议

C#源文件: InternalPackets.cs
C#行数: ~132行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括连接请求和连接接受包
"""

import struct
from typing import Optional, TYPE_CHECKING

from ..utils.net_data_reader import NetDataReader
from ..utils.fast_bit_converter import FastBitConverter
from ..constants import NetConstants

if TYPE_CHECKING:
    from .net_packet import NetPacket
    from ..lite_net_peer import LiteNetPeer


class NetConnectRequestPacket:
    """
    连接请求包

    C#定义: internal sealed class NetConnectRequestPacket
    C#源位置: NetPacket.cs:169-227

    用于客户端发起连接请求

    CRITICAL: HEADER_SIZE必须与C#完全一致 = 14
    C#代码: public const int HeaderSize = 14;
    """

    HEADER_SIZE = 14  # C# line 171: public const int HeaderSize = 14;

    def __init__(
        self,
        connection_time: int,
        connection_number: int,
        target_address: bytes,
        data: 'NetDataReader'
    ):
        """
        创建连接请求包

        C#构造函数: private NetConnectRequestPacket(long connectionTime, byte connectionNumber, byte[] targetAddress, NetDataReader data)
        C#源位置: NetPacket.cs:177-182

        参数:
            connection_time: int - 连接时间戳
            connection_number: int - 连接编号
            target_address: bytes - 目标地址
            data: NetDataReader - 连接数据
        """
        self.connection_time = connection_time
        self.connection_number = connection_number
        self.target_address = target_address
        self.data = data

    @staticmethod
    def get_protocol_id(packet: 'NetPacket') -> int:
        """
        获取协议ID

        C#方法: public static int GetProtocolId(NetPacket packet)
        C#源位置: InternalPackets.cs:25-26

        参数:
            packet: NetPacket - 数据包

        返回:
            int: 协议ID
        """
        return struct.unpack_from('<i', packet.raw_data, 1)[0]

    @staticmethod
    def from_data(packet: 'NetPacket') -> Optional['NetConnectRequestPacket']:
        """
        从数据包解析连接请求

        C#方法: public static NetConnectRequestPacket FromData(NetPacket packet)
        C#源位置: NetPacket.cs:190-211

        字节布局:
        - [0]: Property + ConnectionNumber
        - [1-4]: ProtocolId (int, 4 bytes)
        - [5-12]: ConnectionTime (long, 8 bytes)
        - [13]: AddressSize (1 byte)
        - [14-]: AddressBytes

        参数:
            packet: NetPacket - 收到的数据包

        返回:
            Optional[NetConnectRequestPacket]: 解析出的连接请求包，失败返回None
        """
        if packet.connection_number >= NetConstants.max_connection_number:
            return None

        # 获取连接时间 - C# line 196: BitConverter.ToInt64(packet.RawData, 5)
        connection_time = struct.unpack_from('<q', packet.raw_data, 5)[0]

        # 获取地址大小 - C# line 199: int addrSize = packet.RawData[13]
        addr_size = packet.raw_data[13]
        if addr_size != 16 and addr_size != 28:
            return None

        # 获取地址字节 - C# line 202-203: Buffer.BlockCopy(packet.RawData, 14, addressBytes, 0, addrSize)
        address_bytes = packet.raw_data[14:14 + addr_size]

        # 读取数据并创建请求 - C# line 206-208
        reader = NetDataReader()
        if packet.size > NetConnectRequestPacket.HEADER_SIZE + addr_size:
            reader.set_source(
                packet.raw_data,
                NetConnectRequestPacket.HEADER_SIZE + addr_size,
                packet.size
            )

        return NetConnectRequestPacket(
            connection_time,
            packet.connection_number,
            address_bytes,
            reader
        )

    @staticmethod
    def make(connect_data: bytes, address_bytes: bytes, connect_time: int) -> 'NetPacket':
        """
        创建连接请求数据包

        C#方法: public static NetPacket Make(NetDataWriter connectData, SocketAddress addressBytes, long connectId)
        C#源位置: NetPacket.cs:213-226

        参数:
            connect_data: bytes - 连接数据
            address_bytes: bytes - 地址字节
            connect_time: int - 连接时间

        返回:
            NetPacket: 创建的数据包
        """
        from .net_packet import NetPacket, PacketProperty

        # 创建初始包 - C# line 216: new NetPacket(PacketProperty.ConnectRequest, connectData.Length+addressBytes.Size)
        # 注意：size参数不包含包头，NetPacket会自动加上包头大小
        packet = NetPacket(PacketProperty.ConnectRequest, len(connect_data) + len(address_bytes))

        # 确保包足够大以容纳包头+数据
        required_size = NetConnectRequestPacket.HEADER_SIZE + len(connect_data) + len(address_bytes)
        if len(packet.raw_data) < required_size:
            # 扩展buffer
            packet.raw_data.extend(b'\x00' * (required_size - len(packet.raw_data)))

        # 添加数据 - C# lines 219-223
        FastBitConverter.set_bytes(packet.raw_data, 1, NetConstants.get_protocol_id())  # line 219
        FastBitConverter.set_bytes(packet.raw_data, 5, connect_time)  # line 220
        packet.raw_data[13] = len(address_bytes)  # line 221

        # 复制地址字节 - C# line 222-223
        offset = NetConnectRequestPacket.HEADER_SIZE  # 14
        for i, b in enumerate(address_bytes):
            packet.raw_data[offset + i] = b

        # 复制连接数据 - C# line 224
        data_offset = NetConnectRequestPacket.HEADER_SIZE + len(address_bytes)
        packet.raw_data[data_offset:data_offset + len(connect_data)] = connect_data

        return packet


class NetConnectAcceptPacket:
    """
    连接接受包

    C#定义: internal sealed class NetConnectAcceptPacket
    C#源位置: NetPacket.cs:229-269

    用于服务器接受连接请求

    CRITICAL: SIZE必须与C#完全一致 = 11
    C#代码: public const int Size = 11;

    字节布局:
    - [0]: Property + ConnectionNumber
    - [1-8]: ConnectionId (long, 8 bytes)
    - [9]: ConnectionNumber (byte)
    - [10]: IsReused (byte)
    """

    SIZE = 11  # C# line 231: public const int Size = 11;

    def __init__(
        self,
        connection_id: int,
        connection_number: int,
        is_reused: bool
    ):
        """
        创建连接接受包

        C#构造函数: private NetConnectAcceptPacket(long connectionId, byte connectionNumber, bool isReusedPeer)
        C#源位置: NetPacket.cs:236-241

        参数:
            connection_id: int - 连接ID
            connection_number: int - 连接编号
            is_reused: bool - 是否重用peer
        """
        self.connection_id = connection_id
        self.connection_number = connection_number
        self.is_reused = is_reused

    @staticmethod
    def from_data(packet: 'NetPacket') -> Optional['NetConnectAcceptPacket']:
        """
        从数据包解析连接接受

        C#方法: public static NetConnectAcceptPacket FromData(NetPacket packet)
        C#源位置: NetPacket.cs:243-259

        参数:
            packet: NetPacket - 收到的数据包

        返回:
            Optional[NetConnectAcceptPacket]: 解析出的连接接受包，失败返回None
        """
        if packet.size > NetConnectAcceptPacket.SIZE:
            return None

        # 获取连接ID - C# line 248: BitConverter.ToInt64(packet.RawData, 1)
        connection_id = struct.unpack_from('<q', packet.raw_data, 1)[0]

        # 检查连接编号 - C# line 250-252
        connection_number = packet.raw_data[9]
        if connection_number >= NetConstants.max_connection_number:
            return None

        # 检查重用标志 - C# line 254-256
        is_reused = packet.raw_data[10]
        if is_reused > 1:
            return None

        return NetConnectAcceptPacket(connection_id, connection_number, is_reused == 1)

    @staticmethod
    def make(connect_id: int, connect_num: int, reused_peer: bool) -> 'NetPacket':
        """
        创建连接接受数据包

        C#方法: public static NetPacket Make(long connectId, byte connectNum, bool reusedPeer)
        C#源位置: NetPacket.cs:261-268

        参数:
            connect_id: int - 连接ID
            connect_num: int - 连接编号
            reused_peer: bool - 是否重用peer

        返回:
            NetPacket: 创建的数据包
        """
        from .net_packet import NetPacket, PacketProperty

        # 创建ConnectAccept包 - 至少需要11字节
        packet = NetPacket(PacketProperty.ConnectAccept, 0)

        # 确保包足够大以容纳所有数据（至少11字节）
        required_size = NetConnectAcceptPacket.SIZE
        if len(packet.raw_data) < required_size:
            packet.raw_data.extend(b'\x00' * (required_size - len(packet.raw_data)))

        FastBitConverter.set_bytes(packet.raw_data, 1, connect_id)  # C# line 264
        packet.raw_data[9] = connect_num  # C# line 265
        packet.raw_data[10] = 1 if reused_peer else 0  # C# line 266
        return packet


__all__ = [
    "NetConnectRequestPacket",
    "NetConnectAcceptPacket",
]
