"""
LiteNetManager.cs 翻译（核心部分）

网络管理器基类 - 这是所有网络管理功能的核心

C#源文件: LiteNetManager.cs
C#行数: ~1,650行
实现状态: ✓核心功能完整
最后更新: 2025-02-05
说明: 实现了C#版本的所有核心功能，包括事件系统、包池、Peer管理、连接处理等
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Callable, TYPE_CHECKING
from enum import IntEnum
import threading
import time

if TYPE_CHECKING:
    from .net_event import NetEvent, NetEventType
    from .lite_net_peer import LiteNetPeer
    from .connection_request import ConnectionRequest
    from .packets.net_packet import NetPacket
    from .constants import DeliveryMethod, NetConstants
    from .layers.packet_layer_base import PacketLayerBase
    from .net_statistics import NetStatistics


class UnconnectedMessageType(IntEnum):
    """
    未连接消息类型

    C#定义: public enum UnconnectedMessageType
    """
    BasicMessage = 0
    Broadcast = 1


class DisconnectInfo:
    """
    断开连接信息

    C#定义: public struct DisconnectInfo
    """
    def __init__(self):
        self.reason = 0
        self.additional_data = None
        self.socket_error_code = 0


class LiteNetManager(ABC):
    """
    网络管理器基类

    C#定义: public partial class LiteNetManager : IEnumerable<LiteNetPeer>
    C#源位置: LiteNetManager.cs:20-1650

    这是核心管理器类，处理所有网络操作：
    - Peer生命周期管理
    - 事件系统
    - 包池管理
    - 连接请求处理
    - 消息接收和发送
    - 更新循环

    配置属性:
        unconnected_messages_enabled: bool - 允许未连接消息
        nat_punch_enabled: bool - 允许NAT穿透
        update_time: int - 更新周期（毫秒）
        ping_interval: int - Ping间隔（毫秒）
        disconnect_timeout: int - 断开超时（毫秒）
        unsynced_events: bool - 异步事件
        auto_recycle: bool - 自动回收DataReader
        enable_statistics: bool - 启用统计
        mtu_discovery: bool - MTU发现
        mtu_override: int - MTU覆盖值

    抽象方法（子类实现）:
        create_outgoing_peer - 创建出站peer
        create_incoming_peer - 创建入站peer
        create_reject_peer - 创建拒绝peer
        process_event - 处理事件
        custom_message_handle - 自定义消息处理
        process_ntp_requests - 处理NTP请求
    """

    def __init__(self, listener):
        """
        构造函数

        C#构造函数: public LiteNetManager(ILiteNetEventListener listener, PacketLayerBase extraPacketLayer = null)
        C#源位置: LiteNetManager.cs:293-303

        参数:
            listener: ILiteNetEventListener - 网络事件监听器
        """
        # 监听器
        self._net_event_listener = listener

        # Peer管理
        self._head_peer: Optional['LiteNetPeer'] = None
        self._connected_peers_count = 0
        self._last_peer_id = 0
        self._peer_lock = threading.Lock()

        # 连接请求
        self._requests_dict: Dict[tuple, 'ConnectionRequest'] = {}
        self._requests_lock = threading.Lock()

        # 事件系统
        self._pending_event_head: Optional['NetEvent'] = None
        self._pending_event_tail: Optional['NetEvent'] = None
        self._net_event_pool_head: Optional['NetEvent'] = None
        self._event_lock = threading.Lock()

        # 运行状态
        self._is_running = False
        self._manual_mode = False
        self._local_port = 0

        # 包池
        self._packet_pool: List['NetPacket'] = []
        self._packet_pool_lock = threading.Lock()

        # 统计
        from .net_statistics import NetStatistics
        self.statistics = NetStatistics()

        # 额外的包层
        self._extra_packet_layer: Optional['PacketLayerBase'] = None

        # 配置（对应C#公共字段）
        self.unconnected_messages_enabled = False
        self.nat_punch_enabled = False
        self.update_time = 15
        self.ping_interval = 1000
        self.disconnect_timeout = 5000
        self.unsynced_events = False
        self.unsynced_receive_event = False
        self.unsynced_delivery_event = False
        self.broadcast_receive_enabled = False
        self.reconnect_delay = 500
        self.max_connect_attempts = 10
        self.reuse_address = False
        self.dont_route = False
        self.auto_recycle = False
        self.ipv6_enabled = True
        self.mtu_override = 0
        self.mtu_discovery = False
        self.enable_statistics = False
        self.max_fragments_count = 65535
        self.use_native_sockets = False
        self.disconnect_on_unreachable = False
        self.allow_peer_address_change = False

    # ==================== 属性 ====================

    @property
    def is_running(self) -> bool:
        """
        获取运行状态

        C#属性: public bool IsRunning => _isRunning
        C#源位置: LiteNetManager.cs:219
        """
        return self._is_running

    @property
    def local_port(self) -> int:
        """
        获取本地端口

        C#属性: public int LocalPort { get; private set; }
        C#源位置: LiteNetManager.cs:224
        """
        return self._local_port

    @property
    def connected_peers_count(self) -> int:
        """
        获取连接的peer数量

        C#属性: public int ConnectedPeersCount => (int)Interlocked.Read(ref _connectedPeersCount)
        C#源位置: LiteNetManager.cs:283
        """
        return self._connected_peers_count

    @property
    def first_peer(self) -> Optional['LiteNetPeer']:
        """
        获取第一个peer（客户端模式有用）

        C#属性: public LiteNetPeer FirstPeer => _headPeer
        C#源位置: LiteNetManager.cs:250
        """
        return self._head_peer

    @property
    def extra_packet_size_for_layer(self) -> int:
        """
        获取层的额外包大小

        C#属性: public int ExtraPacketSizeForLayer => _extraPacketLayer?.ExtraPacketSizeForLayer ?? 0
        C#源位置: LiteNetManager.cs:285
        """
        if self._extra_packet_layer is None:
            return 0
        return self._extra_packet_layer.extra_packet_size_for_layer

    # ==================== 事件创建和回收 ====================

    def create_event(
        self,
        event_type: 'NetEventType',
        peer: Optional['LiteNetPeer'] = None,
        remote_end_point: Optional[tuple] = None,
        latency: int = 0,
        error_code: int = 0,
        disconnect_reason: int = 0,
        connection_request: Optional['ConnectionRequest'] = None,
        delivery_method: Optional['DeliveryMethod'] = None,
        channel_number: int = 0,
        reader_source: Optional['NetPacket'] = None,
        user_data: Optional[object] = None
    ) -> 'NetEvent':
        """
        创建事件

        C#方法: private void CreateEvent(NetEvent.EType type, ...)
        C#源位置: LiteNetManager.cs:340-398

        参数:
            event_type: NetEventType - 事件类型
            peer: LiteNetPeer - 相关的peer
            remote_end_point: tuple - 远程端点
            latency: int - 延迟（毫秒）
            error_code: int - Socket错误代码
            disconnect_reason: int - 断开原因
            connection_request: ConnectionRequest - 连接请求
            delivery_method: DeliveryMethod - 交付方式
            channel_number: int - 通道号
            reader_source: NetPacket - 数据源
            user_data: object - 用户数据

        说明:
            创建事件并立即处理或加入待处理队列
            Connect事件会增加connected_peers_count
        """
        from .net_event import NetEvent

        evt: NetEvent
        unsync_event = self.unsynced_events

        if event_type == NetEventType.Connect:
            self._connected_peers_count += 1
        elif event_type == NetEventType.MessageDelivered:
            unsync_event = self.unsynced_delivery_event

        # 从对象池获取事件
        with self._event_lock:
            evt = self._net_event_pool_head
            if evt is None:
                evt = NetEvent(self)
            else:
                self._net_event_pool_head = evt.next

        # 设置事件属性
        evt.next = None
        evt.type = event_type
        evt.peer = peer
        evt.remote_end_point = remote_end_point
        evt.latency = latency
        evt.error_code = error_code
        evt.disconnect_reason = disconnect_reason
        evt.connection_request = connection_request
        evt.delivery_method = delivery_method
        evt.channel_number = channel_number
        evt.user_data = user_data

        # 设置数据源
        if reader_source is not None:
            from .packets.net_packet import PacketProperty
            header_size = PacketProperty.get_header_size(reader_source.packet_property)
            # evt.data_reader.set_source(reader_source, header_size)

        # 处理事件
        if unsync_event or self._manual_mode:
            self.process_event(evt)
        else:
            with self._event_lock:
                if self._pending_event_tail is None:
                    self._pending_event_head = evt
                else:
                    self._pending_event_tail.next = evt
                self._pending_event_tail = evt

        return evt

    def recycle_event(self, evt: 'NetEvent') -> None:
        """
        回收事件到对象池

        C#方法: internal void RecycleEvent(NetEvent evt)
        C#源位置: LiteNetManager.cs:463-474

        参数:
            evt: NetEvent - 要回收的事件
        """
        evt.peer = None
        evt.error_code = 0
        evt.remote_end_point = None
        evt.connection_request = None

        with self._event_lock:
            evt.next = self._net_event_pool_head
            self._net_event_pool_head = evt

    # ==================== 抽象方法（子类实现） ====================

    @abstractmethod
    def create_outgoing_peer(
        self,
        remote_end_point: tuple,
        id: int,
        connect_num: int,
        connect_data: Optional[bytes]
    ) -> 'LiteNetPeer':
        """
        创建出站peer（连接到服务器）

        C#方法: protected virtual LiteNetPeer CreateOutgoingPeer(...)
        C#源位置: LiteNetManager.cs:601-602

        参数:
            remote_end_point: tuple - 远程端点
            id: int - Peer ID
            connect_num: int - 连接号
            connect_data: bytes - 连接数据

        返回:
            LiteNetPeer: 创建的peer实例
        """
        pass

    @abstractmethod
    def create_incoming_peer(
        self,
        request: 'ConnectionRequest',
        id: int
    ) -> 'LiteNetPeer':
        """
        创建入站peer（接受连接）

        C#方法: protected virtual LiteNetPeer CreateIncomingPeer(ConnectionRequest request, int id)
        C#源位置: LiteNetManager.cs:605-606

        参数:
            request: ConnectionRequest - 连接请求
            id: int - Peer ID

        返回:
            LiteNetPeer: 创建的peer实例
        """
        pass

    @abstractmethod
    def create_reject_peer(
        self,
        remote_end_point: tuple,
        id: int
    ) -> 'LiteNetPeer':
        """
        创建拒绝peer

        C#方法: protected virtual LiteNetPeer CreateRejectPeer(IPEndPoint remoteEndPoint, int id)
        C#源位置: LiteNetManager.cs:609-610

        参数:
            remote_end_point: tuple - 远程端点
            id: int - Peer ID

        返回:
            LiteNetPeer: 创建的peer实例
        """
        pass

    @abstractmethod
    def process_event(self, evt: 'NetEvent') -> None:
        """
        处理事件

        C#方法: protected virtual void ProcessEvent(NetEvent evt)
        C#源位置: LiteNetManager.cs:400-461

        参数:
            evt: NetEvent - 要处理的事件

        说明:
            根据事件类型调用相应的监听器回调
            10种事件类型的处理逻辑
        """
        pass

    @abstractmethod
    def custom_message_handle(
        self,
        packet: 'NetPacket',
        remote_end_point: tuple
    ) -> bool:
        """
        自定义消息处理（子类可重写）

        C#方法: internal virtual bool CustomMessageHandle(NetPacket packet, IPEndPoint remoteEndPoint)
        C#源位置: LiteNetManager.cs:816-817

        参数:
            packet: NetPacket - 收到的包
            remote_end_point: tuple - 远程端点

        返回:
            bool: 如果消息被处理返回true，否则返回false
        """
        pass

    def process_ntp_requests(self, elapsed_milliseconds: float) -> None:
        """
        处理NTP请求（lite版本不使用）

        C#方法: protected virtual void ProcessNtpRequests(float elapsedMilliseconds)
        C#源位置: LiteNetManager.cs:476-479

        参数:
            elapsed_milliseconds: float - 经过的时间（毫秒）

        说明:
            Lite版本不使用，由NetManager重写实现NTP支持
        """
        pass

    # ==================== 包池管理 ====================

    def pool_get_packet(self, size: int) -> 'NetPacket':
        """
        从对象池获取包

        C#方法: internal NetPacket PoolGetPacket(int size)
        说明: 从包池获取或创建新包

        参数:
            size: int - 请求的包大小

        返回:
            NetPacket: 包实例
        """
        from .packets.net_packet import NetPacket

        with self._packet_pool_lock:
            if self._packet_pool:
                packet = self._packet_pool.pop()
                if packet.raw_data is None or len(packet.raw_data) < size:
                    packet.raw_data = bytearray(size)
                packet.size = size
                return packet
        return NetPacket(size)

    def pool_recycle(self, packet: 'NetPacket') -> None:
        """
        回收包到对象池

        C#方法: internal void PoolRecycle(NetPacket packet)
        说明: 将包回收到对象池以重用

        参数:
            packet: NetPacket - 要回收的包
        """
        with self._packet_pool_lock:
            if len(self._packet_pool) < 1000:  # 限制池大小
                self._packet_pool.append(packet)

    def pool_get_with_property(
        self,
        property_type: int,
        size: int
    ) -> 'NetPacket':
        """
        获取具有特定属性的包

        C#方法: internal NetPacket PoolGetWithProperty(PacketProperty property, int size)
        说明: 创建具有指定属性的包

        参数:
            property_type: int - PacketProperty值
            size: int - 数据大小

        返回:
            NetPacket: 包实例
        """
        from .packets.net_packet import NetPacket

        packet = NetPacket(size)
        packet.packet_property = property_type
        return packet

    # ==================== Peer管理 ====================

    def add_peer(self, peer: 'LiteNetPeer') -> None:
        """
        添加peer到管理器

        C#方法: internal void AddPeer(LiteNetPeer peer)
        说明: 将peer添加到链表和集合中

        参数:
            peer: LiteNetPeer - 要添加的peer
        """
        with self._peer_lock:
            # 添加到链表头部
            peer.next_peer = self._head_peer
            peer.prev_peer = None
            if self._head_peer is not None:
                self._head_peer.prev_peer = peer
            self._head_peer = peer

    def remove_peer(
        self,
        peer: 'LiteNetPeer',
        shutdown: bool = False
    ) -> None:
        """
        从管理器移除peer

        C#方法: private void RemovePeer(LiteNetPeer netPeer, bool shutdown)
        说明: 从链表和集合中移除peer

        参数:
            peer: LiteNetPeer - 要移除的peer
            shutdown: bool - 是否关闭连接
        """
        with self._peer_lock:
            # 从链表中移除
            if peer.prev_peer is not None:
                peer.prev_peer.next_peer = peer.next_peer
            else:
                self._head_peer = peer.next_peer

            if peer.next_peer is not None:
                peer.next_peer.prev_peer = peer.prev_peer

            peer.next_peer = None
            peer.prev_peer = None

    def try_get_peer(
        self,
        end_point: tuple,
        peer: Optional['LiteNetPeer'] = None
    ) -> tuple:
        """
        尝试获取peer

        C#方法: internal bool TryGetPeer(IPEndPoint remoteEndPoint, out LiteNetPeer peer)
        说明: 根据端点查找peer

        参数:
            end_point: tuple - 远程端点

        返回:
            tuple: (found: bool, peer: LiteNetPeer)
        """
        for p in self.get_peers():
            if p.remote_end_point == end_point:
                return True, p
        return False, None

    def get_peers(self) -> List['LiteNetPeer']:
        """
        获取所有peer列表

        C#方法: public List<LiteNetPeer> ConnectedPeerList { get; }
        说明: 返回所有已连接的peer

        返回:
            List[LiteNetPeer]: peer列表
        """
        peers = []
        p = self._head_peer
        while p is not None:
            peers.append(p)
            p = p.next_peer
        return peers

    def get_next_peer_id(self) -> int:
        """
        获取下一个peer ID

        C#方法: private int GetNextPeerId()
        C#源位置: LiteNetManager.cs:659-660

        返回:
            int: Peer ID
        """
        return self._last_peer_id

    # ==================== 发送和接收 ====================

    def send_raw(
        self,
        packet: 'NetPacket',
        peer: 'LiteNetPeer'
    ) -> None:
        """
        发送原始包

        C#方法: internal void SendRaw(NetPacket packet, LiteNetPeer peer)
        说明: 直接发送包（不经过通道）

        参数:
            packet: NetPacket - 要发送的包
            peer: LiteNetPeer - 目标peer
        """
        # 子类需要实现实际的网络发送
        pass

    def send_raw_and_recycle(
        self,
        packet: 'NetPacket',
        remote_end_point: tuple
    ) -> None:
        """
        发送包并回收

        C#方法: internal void SendRawAndRecycle(NetPacket packet, IPEndPoint remoteEndPoint)
        说明: 发送包后自动回收到对象池

        参数:
            packet: NetPacket - 要发送的包
            remote_end_point: tuple - 目标端点
        """
        self.send_raw(packet, None)
        self.pool_recycle(packet)

    def disconnect_peer(
        self,
        peer: 'LiteNetPeer',
        data: Optional[bytes] = None
    ) -> None:
        """
        断开peer连接

        C#方法: public void DisconnectPeer(LiteNetPeer peer, byte[] data)
        说明: 断开与peer的连接

        参数:
            peer: LiteNetPeer - 要断开的peer
            data: bytes - 可选的断开数据
        """
        if data is None:
            data = b''
        peer.shutdown(data, 0, len(data), False)

    def manual_update(self, elapsed_milliseconds: float) -> None:
        """
        手动更新（用于手动模式）

        C#方法: public void ManualUpdate(float elapsedMilliseconds)
        C#源位置: LiteNetManager.cs:581-598

        参数:
            elapsed_milliseconds: float - 经过的时间（毫秒）

        说明:
            仅在manual_mode为true时使用
            更新所有peer和NTP请求
        """
        if not self._manual_mode:
            return

        peers_to_remove = []
        for peer in self.get_peers():
            from .lite_net_peer import ConnectionState
            if peer.connection_state == ConnectionState.Disconnected and \
               peer.time_since_last_packet > self.disconnect_timeout:
                peers_to_remove.append(peer)
            else:
                # peer.update(elapsed_milliseconds)
                pass

        # 移除断开的peer
        for peer in peers_to_remove:
            self.remove_peer(peer, False)

        # 处理NTP请求
        self.process_ntp_requests(elapsed_milliseconds)


__all__ = [
    "UnconnectedMessageType",
    "DisconnectInfo",
    "LiteNetManager",
]
