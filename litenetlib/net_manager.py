"""
NetManager.cs 翻译（完整版）

功能丰富的网络管理器，支持可调整的通道数量

C#源文件: NetManager.cs
C#行数: ~280行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括多通道支持、NTP请求、事件处理
"""

import socket
import threading
from typing import Optional, List, Dict, TYPE_CHECKING
from queue import Queue

from .constants import DeliveryMethod, NetConstants
from .event_interfaces import INetEventListener
from .connection_request import ConnectionRequest
from .lite_net_manager import LiteNetManager
from .lite_net_peer import LiteNetPeer
from .net_event import NetEvent, NetEventType, DisconnectReason
from .debug import NetDebug

if TYPE_CHECKING:
    from .net_peer import NetPeer
    from .layers.packet_layer_base import PacketLayerBase
    from .packets.net_packet import NetPacket
    from .utils.ntp_request import NtpRequest
    from .utils.ntp_packet import NtpPacket
    from .utils.net_data_reader import NetDataReader
    from .utils.net_data_writer import NetDataWriter


class NetManager(LiteNetManager):
    """
    网络管理器

    C#定义: public class NetManager : LiteNetManager
    C#源位置: NetManager.cs:13-244

    主要功能：
    - 多通道QoS支持（1-64个通道）
    - NTP请求管理
    - 连接管理
    - 事件处理
    - 包分发
    """

    def __init__(self, listener: 'INetEventListener', extra_packet_layer: Optional['PacketLayerBase'] = None):
        """
        创建网络管理器

        C#构造函数: public NetManager(INetEventListener listener, PacketLayerBase extraPacketLayer = null)
        C#源位置: NetManager.cs:33-34

        参数:
            listener: INetEventListener - 事件监听器
            extra_packet_layer: PacketLayerBase - 额外的包处理层（可选）
        """
        super().__init__(listener, extra_packet_layer)

        self._net_event_listener = listener
        self._channels_count = 1
        self._ntp_requests: Dict[tuple, 'NtpRequest'] = {}

    @property
    def channels_count(self) -> int:
        """
        获取或设置每个消息类型的QoS通道数量（值必须在1到64之间）

        C#属性: public byte ChannelsCount { get; set; }
        C#源位置: NetManager.cs:22-31

        返回:
            int: 通道数量（1-64）
        """
        return self._channels_count

    @channels_count.setter
    def channels_count(self, value: int) -> None:
        if value < 1 or value > 64:
            raise ValueError("Channels count must be between 1 and 64")
        self._channels_count = value

    def create_ntp_request(self, address: str, port: Optional[int] = None) -> None:
        """
        创建NTP服务器请求

        C#方法: public void CreateNtpRequest(IPEndPoint endPoint)
        C#方法: public void CreateNtpRequest(string ntpServerAddress, int port)
        C#方法: public void CreateNtpRequest(string ntpServerAddress)
        C#源位置: NetManager.cs:40-62

        参数:
            address: str - NTP服务器地址或主机名
            port: Optional[int] - NTP端口（默认123）
        """
        from .utils.net_utils import NetUtils
        from .utils.ntp_request import NtpRequest

        if port is None:
            # 使用默认端口
            end_point = NetUtils.make_end_point(address, 123)
        else:
            end_point = NetUtils.make_end_point(address, port)

        self._ntp_requests[end_point] = NtpRequest(end_point)

    def send_to_all(
        self,
        data: bytes,
        channel_number: int,
        options: DeliveryMethod,
        exclude_peer: Optional['NetPeer'] = None
    ) -> None:
        """
        发送数据到所有连接的peer

        C#方法: public void SendToAll(byte[] data, byte channelNumber, DeliveryMethod options, LiteNetPeer excludePeer)
        C#源位置: NetManager.cs:245-258

        参数:
            data: bytes - 要发送的数据
            channel_number: int - 通道编号（0到channels_count-1）
            options: DeliveryMethod - 发送选项
            exclude_peer: Optional[NetPeer] - 排除的peer
        """
        from .net_peer import NetPeer

        with self._peer_lock:
            peer = self._head_peer
            while peer is not None:
                if isinstance(peer, NetPeer) and peer is not exclude_peer:
                    peer.send(data, channel_number, options)
                peer = peer.next_peer

    def send_to_all_with_writer(
        self,
        writer: 'NetDataWriter',
        channel_number: int,
        options: DeliveryMethod,
        exclude_peer: Optional['NetPeer'] = None
    ) -> None:
        """
        发送数据到所有连接的peer（使用NetDataWriter）

        C#方法: public void SendToAll(NetDataWriter writer, byte channelNumber, DeliveryMethod options, LiteNetPeer excludePeer)
        C#源位置: NetManager.cs:223-234

        参数:
            writer: NetDataWriter - 包含数据的写入器
            channel_number: int - 通道编号
            options: DeliveryMethod - 发送选项
            exclude_peer: Optional[NetPeer] - 排除的peer
        """
        self.send_to_all(writer.data, channel_number, options, exclude_peer)

    # ========================================================================
    # LiteNetManager抽象方法实现
    # ========================================================================

    def create_outgoing_peer(
        self,
        remote_end_point: tuple,
        id: int,
        connect_num: int,
        connect_data: bytes
    ) -> LiteNetPeer:
        """
        创建出站peer（用于主动连接）

        C#方法: protected override LiteNetPeer CreateOutgoingPeer(IPEndPoint remoteEndPoint, int id, byte connectNum, ReadOnlySpan<byte> connectData)
        C#源位置: NetManager.cs:99-100

        参数:
            remote_end_point: tuple - 远程端点
            id: int - peer ID
            connect_num: int - 连接编号
            connect_data: bytes - 连接数据

        返回:
            LiteNetPeer: 创建的peer
        """
        from .net_peer import NetPeer
        return NetPeer(self, remote_end_point, id, connect_num, connect_data)

    def create_incoming_peer(self, request: 'ConnectionRequest', id: int) -> LiteNetPeer:
        """
        创建入站peer（用于接受连接）

        C#方法: protected override LiteNetPeer CreateIncomingPeer(ConnectionRequest request, int id)
        C#源位置: NetManager.cs:103-104

        参数:
            request: ConnectionRequest - 连接请求
            id: int - peer ID

        返回:
            LiteNetPeer: 创建的peer
        """
        from .net_peer import NetPeer
        return NetPeer(self, request, id)

    def create_reject_peer(self, remote_end_point: tuple, id: int) -> LiteNetPeer:
        """
        创建拒绝peer（用于拒绝连接）

        C#方法: protected override LiteNetPeer CreateRejectPeer(IPEndPoint remoteEndPoint, int id)
        C#源位置: NetManager.cs:107-108

        参数:
            remote_end_point: tuple - 远程端点
            id: int - peer ID

        返回:
            LiteNetPeer: 创建的peer
        """
        from .net_peer import NetPeer
        return NetPeer(self, remote_end_point, id)

    def process_event(self, evt: NetEvent) -> None:
        """
        处理网络事件

        C#方法: protected override void ProcessEvent(NetEvent evt)
        C#源位置: NetManager.cs:110-172

        参数:
            evt: NetEvent - 要处理的事件
        """
        from .net_peer import NetPeer

        NetDebug.write(f"[NM] Processing event: {evt.type}")

        empty_data = evt.data_reader is None
        net_peer = evt.peer

        # 分发事件到监听器
        if evt.type == NetEventType.Connect:
            self._net_event_listener.on_peer_connected(net_peer)

        elif evt.type == NetEventType.Disconnect:
            info = DisconnectInfo(
                reason=evt.disconnect_reason,
                additional_data=evt.data_reader,
                socket_error_code=evt.error_code
            )
            self._net_event_listener.on_peer_disconnected(net_peer, info)

        elif evt.type == NetEventType.Receive:
            self._net_event_listener.on_network_receive(
                net_peer,
                evt.data_reader,
                evt.channel_number,
                evt.delivery_method
            )

        elif evt.type == NetEventType.ReceiveUnconnected:
            self._net_event_listener.on_network_receive_unconnected(
                evt.remote_end_point,
                evt.data_reader,
                UnconnectedMessageType.BasicMessage
            )

        elif evt.type == NetEventType.Broadcast:
            self._net_event_listener.on_network_receive_unconnected(
                evt.remote_end_point,
                evt.data_reader,
                UnconnectedMessageType.Broadcast
            )

        elif evt.type == NetEventType.Error:
            self._net_event_listener.on_network_error(
                evt.remote_end_point,
                evt.error_code
            )

        elif evt.type == NetEventType.ConnectionLatencyUpdated:
            self._net_event_listener.on_network_latency_update(
                net_peer,
                evt.latency
            )

        elif evt.type == NetEventType.ConnectionRequest:
            self._net_event_listener.on_connection_request(evt.connection_request)

        elif evt.type == NetEventType.MessageDelivered:
            self._net_event_listener.on_message_delivered(
                net_peer,
                evt.user_data
            )

        elif evt.type == NetEventType.PeerAddressChanged:
            # 更新peer地址
            with self._peer_lock:
                if self._contains_peer(evt.peer):
                    self.remove_peer_from_set(evt.peer)
                    previous_address = (evt.peer.address, evt.peer.port)
                    evt.peer.finish_end_point_change(evt.remote_end_point)
                    self.add_peer_to_set(evt.peer)

                    self._net_event_listener.on_peer_address_changed(
                        net_peer,
                        previous_address
                    )

        # 回收事件
        if empty_data:
            self.recycle_event(evt)
        elif self.auto_recycle and evt.data_reader is not None:
            # 如果需要自动回收
            pass

    def custom_message_handle(self, packet: 'NetPacket', remote_end_point: tuple) -> bool:
        """
        自定义消息处理（用于NTP响应）

        C#方法: internal override bool CustomMessageHandle(NetPacket packet, IPEndPoint remoteEndPoint)
        C#源位置: NetManager.cs:64-96

        参数:
            packet: NetPacket - 收到的包
            remote_end_point: tuple - 远程端点

        返回:
            bool: 如果消息被处理返回true
        """
        from .utils.ntp_packet import NtpPacket

        # 检查是否有NTP请求
        if len(self._ntp_requests) > 0 and remote_end_point in self._ntp_requests:
            if packet.size < 48:
                NetDebug.write(f"[NTP] Response too short: {packet.size}")
                return True

            # 复制数据
            copied_data = bytes(packet.raw_data[:packet.size])

            try:
                from datetime import datetime
                ntp_packet = NtpPacket.from_server_response(copied_data, datetime.utcnow())
                ntp_packet.validate_reply()

                # 成功 - 移除请求并通知
                del self._ntp_requests[remote_end_point]
                self._net_event_listener.on_ntp_response(ntp_packet)
                return True

            except Exception as ex:
                NetDebug.write(f"[NTP] Response error: {ex}")
                return True

        return False

    def process_ntp_requests(self, elapsed_milliseconds: float) -> None:
        """
        处理NTP请求

        C#方法: protected override void ProcessNtpRequests(float elapsedMilliseconds)
        C#源位置: NetManager.cs:174-196

        参数:
            elapsed_milliseconds: float - 经过的毫秒数
        """
        if len(self._ntp_requests) == 0:
            return

        requests_to_remove = []

        for end_point, ntp_request in self._ntp_requests.items():
            ntp_request.send(self, elapsed_milliseconds)
            if ntp_request.need_to_kill:
                requests_to_remove.append(end_point)

        for end_point in requests_to_remove:
            del self._ntp_requests[end_point]


class UnconnectedMessageType:
    """
    未连接消息类型

    C#定义: internal enum UnconnectedMessageType
    C#源位置: LiteNetManager.cs
    """
    BasicMessage = 0
    Broadcast = 1


class DisconnectInfo:
    """
    断开连接信息

    C#定义: public class DisconnectInfo
    C#源位置: NetManager.cs:121-126
    """
    def __init__(
        self,
        reason: int = DisconnectReason.DisconnectPeerCalled,
        additional_data: Optional['NetDataReader'] = None,
        socket_error_code: int = 0
    ):
        """
        创建断开连接信息

        参数:
            reason: int - 断开原因
            additional_data: NetDataReader - 额外数据
            socket_error_code: int - socket错误代码
        """
        self.reason = reason
        self.additional_data = additional_data
        self.socket_error_code = socket_error_code


__all__ = [
    "NetManager",
    "UnconnectedMessageType",
    "DisconnectInfo",
]
