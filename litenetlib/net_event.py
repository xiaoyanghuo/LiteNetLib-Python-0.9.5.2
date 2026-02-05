"""
NetEvent.cs 翻译

内部事件类型，用于网络事件分发

C#源文件: NetEvent.cs
C#行数: ~45行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，这是整个事件系统的基础
"""

from enum import IntEnum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .net_data_reader import NetDataReader


class NetEventType(IntEnum):
    """
    事件类型枚举

    C#定义: public enum EType
    C#源位置: NetEvent.cs:13-25
    """
    Connect = 0
    Disconnect = 1
    Receive = 2
    ReceiveUnconnected = 3
    Error = 4
    ConnectionLatencyUpdated = 5
    Broadcast = 6
    ConnectionRequest = 7
    MessageDelivered = 8
    PeerAddressChanged = 9


class DisconnectReason(IntEnum):
    """
    断开连接原因

    C#定义: public enum DisconnectReason
    C#源位置: (在NetPeer.cs或其他地方定义)
    """
    ConnectionFailed = 0
    Timeout = 1
    HostUnreachable = 2
    RemoteConnectionClose = 3
    DisconnectPeerCalled = 4
    Reconnect = 5
    InvalidProtocol = 6
    UnknownHost = 7
    MaxConnectionsReached = 8


class NetEvent:
    """
    网络事件

    C#定义: public sealed class NetEvent
    C#源位置: NetEvent.cs:9-44

    这是核心事件类，用于在NetManager和EventListener之间传递事件信息

    属性:
        next: NetEvent - 对象池链表指针（用于回收）
        type: NetEventType - 事件类型
        peer: LiteNetPeer - 相关的peer（如果适用）
        remote_end_point: tuple - 远程端点（如果适用）
        user_data: object - 用户数据（如果适用）
        latency: int - 延迟（毫秒）
        error_code: int - Socket错误代码
        disconnect_reason: DisconnectReason - 断开原因
        connection_request: ConnectionRequest - 连接请求（如果适用）
        delivery_method: DeliveryMethod - 交付方式
        channel_number: int - 通道号
        data_reader: NetDataReader - 数据读取器
    """

    def __init__(self, manager=None):
        """
        创建事件

        C#构造函数: public NetEvent(LiteNetManager manager)
        C#源位置: NetEvent.cs:39-42

        参数:
            manager: LiteNetManager - 网络管理器（用于创建DataReader）

        说明:
            初始化所有字段为None/默认值
            创建DataReader实例（如果manager不为None）
        """
        # 对象池链表
        self.next: Optional['NetEvent'] = None

        # 事件类型
        self.type: NetEventType = NetEventType.Connect

        # Peer相关
        self.peer: Optional['LiteNetPeer'] = None

        # 端点信息
        self.remote_end_point: Optional[tuple] = None

        # 用户数据
        self.user_data: Optional[object] = None

        # 延迟信息（毫秒）
        self.latency: int = 0

        # 错误信息
        self.error_code: int = 0

        # 断开原因
        self.disconnect_reason: DisconnectReason = DisconnectReason.ConnectionFailed

        # 连接请求
        self.connection_request: Optional['ConnectionRequest'] = None

        # 交付方式
        self.delivery_method: Optional['DeliveryMethod'] = None

        # 通道号
        self.channel_number: int = 0

        # 数据读取器（延迟创建）
        self._data_reader: Optional[NetDataReader] = None
        self._manager = manager

    @property
    def data_reader(self) -> Optional['NetDataReader']:
        """
        获取数据读取器

        C#对应: public readonly NetPacketReader DataReader
        C#源位置: NetEvent.cs:37

        返回:
            NetDataReader: 数据读取器实例

        说明:
            按需创建，避免不必要的开销
        """
        if self._data_reader is None and self._manager is not None:
            from .net_data_reader import NetDataReader
            self._data_reader = NetDataReader()
        return self._data_reader

    def reset(self) -> None:
        """
        重置事件到初始状态（用于对象池回收）

        C#对应: 无直接对应，通过对象池管理器重置

        说明:
            清空所有引用，重置为默认值
            对象池回收时调用此方法
        """
        self.next = None
        self.type = NetEventType.Connect
        self.peer = None
        self.remote_end_point = None
        self.user_data = None
        self.latency = 0
        self.error_code = 0
        self.disconnect_reason = DisconnectReason.ConnectionFailed
        self.connection_request = None
        self.delivery_method = None
        self.channel_number = 0

        # 重置DataReader（如果存在）
        if self._data_reader is not None:
            # C#版本会回收DataReader
            self._data_reader = None

    def __repr__(self) -> str:
        """
        字符串表示

        返回:
            str: 事件的字符串表示
        """
        type_name = NetEventType(self.type).name if self.type < len(NetEventType) else f"Unknown({self.type})"
        return f"NetEvent(type={type_name}, peer={self.peer})"


__all__ = [
    "NetEventType",
    "DisconnectReason",
    "NetEvent",
]
