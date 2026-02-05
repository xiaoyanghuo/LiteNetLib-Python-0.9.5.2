"""
NatPunchModule.cs 翻译（完整版）

NAT穿透模块 - UDP NAT打孔操作模块

C#源文件: NatPunchModule.cs
C#行数: ~265行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括NAT穿透请求/响应处理
"""

import threading
from typing import Optional, Callable, TYPE_CHECKING
from queue import Queue
from enum import IntEnum

from .utils.net_data_reader import NetDataReader
from .utils.net_data_writer import NetDataWriter
from .utils.net_packet_processor import NetPacketProcessor
from .net_utils import NetUtils
from .constants import NetConstants
from .debug import NetDebug

if TYPE_CHECKING:
    from .lite_net_manager import LiteNetManager
    from .packets.net_packet import NetPacket


class NatAddressType(IntEnum):
    """
    NAT地址类型

    C#定义: public enum NatAddressType
    C#源位置: NatPunchModule.cs:9-13
    """
    Internal = 0  # 内部地址
    External = 1  # 外部地址


class INatPunchListener:
    """
    NAT穿透监听器接口

    C#定义: public interface INatPunchListener
    C#源位置: NatPunchModule.cs:15-19
    """

    def on_nat_introduction_request(
        self,
        local_end_point: tuple,
        remote_end_point: tuple,
        token: str
    ) -> None:
        """
        收到NAT引入请求

        C#方法: void OnNatIntroductionRequest(IPEndPoint localEndPoint, IPEndPoint remoteEndPoint, string token)
        C#源位置: NatPunchModule.cs:17

        参数:
            local_end_point: tuple - 本地端点
            remote_end_point: tuple - 远程端点
            token: str - 令牌
        """
        pass

    def on_nat_introduction_success(
        self,
        target_end_point: tuple,
        type: NatAddressType,
        token: str
    ) -> None:
        """
        NAT引入成功

        C#方法: void OnNatIntroductionSuccess(IPEndPoint targetEndPoint, NatAddressType type, string token)
        C#源位置: NatPunchModule.cs:18

        参数:
            target_end_point: tuple - 目标端点
            type: NatAddressType - 地址类型
            token: str - 令牌
        """
        pass


class EventBasedNatPunchListener(INatPunchListener):
    """
    基于事件的NAT穿透监听器

    C#定义: public class EventBasedNatPunchListener : INatPunchListener
    C#源位置: NatPunchModule.cs:21-40

    使用委托模式实现事件通知
    """

    def __init__(self):
        """
        创建事件监听器

        C#构造函数: public EventBasedNatPunchListener()
        """
        self._nat_introduction_request_callback: Optional[Callable] = None
        self._nat_introduction_success_callback: Optional[Callable] = None

    def on_nat_introduction_request(
        self,
        local_end_point: tuple,
        remote_end_point: tuple,
        token: str
    ) -> None:
        """
        收到NAT引入请求（触发事件）

        C#方法: void INatPunchListener.OnNatIntroductionRequest(...)
        C#源位置: NatPunchModule.cs:29-33
        """
        if self._nat_introduction_request_callback is not None:
            self._nat_introduction_request_callback(local_end_point, remote_end_point, token)

    def on_nat_introduction_success(
        self,
        target_end_point: tuple,
        type: NatAddressType,
        token: str
    ) -> None:
        """
        NAT引入成功（触发事件）

        C#方法: void INatPunchListener.OnNatIntroductionSuccess(...)
        C#源位置: NatPunchModule.cs:35-39
        """
        if self._nat_introduction_success_callback is not None:
            self._nat_introduction_success_callback(target_end_point, type, token)


class NatIntroduceRequestPacket:
    """
    NAT引入请求包

    C#定义: internal class NatIntroduceRequestPacket
    C#源位置: NatPunchModule.cs:61-65
    """

    def __init__(self):
        self.internal: Optional[tuple] = None
        self.token: str = ""


class NatIntroduceResponsePacket:
    """
    NAT引入响应包

    C#定义: internal class NatIntroduceResponsePacket
    C#源位置: NatPunchModule.cs:67-72
    """

    def __init__(self):
        self.internal: Optional[tuple] = None
        self.external: Optional[tuple] = None
        self.token: str = ""


class NatPunchPacket:
    """
    NAT打孔包

    C#定义: internal class NatPunchPacket
    C#源位置: NatPunchModule.cs:74-78
    """

    def __init__(self):
        self.token: str = ""
        self.is_external: bool = False


class NatPunchModule:
    """
    NAT穿透模块

    C#定义: public sealed class NatPunchModule
    C#源位置: NatPunchModule.cs:45-263

    UDP NAT打孔操作的模块，可从NetManager访问
    """

    MAX_TOKEN_LENGTH = 256

    def __init__(self, socket: 'LiteNetManager'):
        """
        创建NAT穿透模块

        C#构造函数: internal NatPunchModule(LiteNetManager socket)
        C#源位置: NatPunchModule.cs:94-100

        参数:
            socket: LiteNetManager - 网络管理器
        """
        self._socket = socket
        self._request_events: Queue = Queue()
        self._success_events: Queue = Queue()
        self._cache_reader = NetDataReader()
        self._cache_writer = NetDataWriter()
        self._net_packet_processor = NetPacketProcessor(self.MAX_TOKEN_LENGTH)
        self._nat_punch_listener: Optional[INatPunchListener] = None
        self._unsynced_events = False
        self._lock = threading.Lock()

        # 订阅包处理器
        self._net_packet_processor.subscribe_reusable(
            NatIntroduceResponsePacket,
            self._on_nat_introduction_response
        )
        self._net_packet_processor.subscribe_reusable_with_point(
            NatIntroduceRequestPacket,
            self._on_nat_introduction_request
        )
        self._net_packet_processor.subscribe_reusable_with_point(
            NatPunchPacket,
            self._on_nat_punch
        )

    @property
    def unsynced_events(self) -> bool:
        """
        获取或设置是否自动调用事件（不使用PollEvents）

        C#属性: public bool UnsyncedEvents { get; set; }
        C#源位置: NatPunchModule.cs:92

        返回:
            bool: True表示从另一个线程自动调用事件
        """
        return self._unsynced_events

    @unsynced_events.setter
    def unsynced_events(self, value: bool) -> None:
        self._unsynced_events = value

    def init(self, listener: INatPunchListener) -> None:
        """
        初始化NAT穿透模块

        C#方法: public void Init(INatPunchListener listener)
        C#源位置: NatPunchModule.cs:111-114

        参数:
            listener: INatPunchListener - NAT穿透监听器
        """
        self._nat_punch_listener = listener

    def process_message(self, sender_end_point: tuple, packet: 'NetPacket') -> None:
        """
        处理收到的消息

        C#方法: internal void ProcessMessage(IPEndPoint senderEndPoint, NetPacket packet)
        C#源位置: NatPunchModule.cs:102-109

        参数:
            sender_end_point: tuple - 发送者端点
            packet: NetPacket - 收到的包
        """
        with self._lock:
            self._cache_reader.set_source(
                packet.raw_data,
                NetConstants.header_size,
                packet.size
            )
            self._net_packet_processor.read_all_packets(self._cache_reader, sender_end_point)

    def poll_events(self) -> None:
        """
        轮询事件（从事件队列中获取并触发）

        C#方法: public void PollEvents()
        C#源位置: NatPunchModule.cs:151-171
        """
        if self._unsynced_events:
            return

        if self._nat_punch_listener is None or (self._success_events.empty() and self._request_events.empty()):
            return

        # 处理成功事件
        while not self._success_events.empty():
            evt = self._success_events.get()
            self._nat_punch_listener.on_nat_introduction_success(
                evt['target_end_point'],
                evt['type'],
                evt['token']
            )

        # 处理请求事件
        while not self._request_events.empty():
            evt = self._request_events.get()
            self._nat_punch_listener.on_nat_introduction_request(
                evt['local_end_point'],
                evt['remote_end_point'],
                evt['token']
            )

    def send_nat_introduce_request(self, host: str, port: int, additional_info: str) -> None:
        """
        发送NAT引入请求

        C#方法: public void SendNatIntroduceRequest(string host, int port, string additionalInfo)
        C#源位置: NatPunchModule.cs:173-176

        参数:
            host: str - 主机服务器地址
            port: int - 主机服务器端口
            additional_info: str - 额外信息
        """
        master_server_end_point = NetUtils.make_end_point(host, port)
        self._send_nat_introduce_request_internal(master_server_end_point, additional_info)

    def nat_introduce(
        self,
        host_internal: tuple,
        host_external: tuple,
        client_internal: tuple,
        client_external: tuple,
        additional_info: str
    ) -> None:
        """
        NAT引入（服务器端调用，向双方发送对方的地址信息）

        C#方法: public void NatIntroduce(...)
        C#源位置: NatPunchModule.cs:128-149

        参数:
            host_internal: tuple - 主机内部地址
            host_external: tuple - 主机外部地址
            client_internal: tuple - 客户端内部地址
            client_external: tuple - 客户端外部地址
            additional_info: str - 额外信息
        """
        req = NatIntroduceResponsePacket()
        req.token = additional_info

        # 第一个包（服务器）发送给客户端
        req.internal = host_internal
        req.external = host_external
        self._send(req, client_external)

        # 第二个包（客户端）发送给服务器
        req.internal = client_internal
        req.external = client_external
        self._send(req, host_external)

    # ========================================================================
    # 私有方法
    # ========================================================================

    def _send_nat_introduce_request_internal(
        self,
        master_server_end_point: tuple,
        additional_info: str
    ) -> None:
        """
        发送NAT引入请求（内部方法）

        C#方法: public void SendNatIntroduceRequest(IPEndPoint masterServerEndPoint, string additionalInfo)
        C#源位置: NatPunchModule.cs:178-194

        参数:
            master_server_end_point: tuple - 主服务器端点
            additional_info: str - 额外信息
        """
        # 准备外出数据
        network_ip = NetUtils.get_local_ip(NetUtils.LocalAddrType.IPv4)
        if network_ip is None or network_ip == "":
            network_ip = NetUtils.get_local_ip(NetUtils.LocalAddrType.IPv6)

        req = NatIntroduceRequestPacket()
        req.internal = NetUtils.make_end_point(network_ip, self._socket.local_port)
        req.token = additional_info

        self._send(req, master_server_end_point)

    def _send(self, packet, target: tuple) -> None:
        """
        发送包

        C#方法: private void Send<T>(T packet, IPEndPoint target)
        C#源位置: NatPunchModule.cs:116-126

        参数:
            packet: 要发送的包对象
            target: tuple - 目标端点
        """
        from .packets.net_packet import PacketProperty

        self._cache_writer.reset()
        self._cache_writer.put_byte(PacketProperty.NatMessage)
        self._net_packet_processor.write(self._cache_writer, packet)
        self._socket.send_raw(
            self._cache_writer.data,
            0,
            self._cache_writer.length,
            target
        )

    def _on_nat_introduction_request(
        self,
        req: NatIntroduceRequestPacket,
        sender_end_point: tuple
    ) -> None:
        """
        收到NAT引入请求

        C#方法: private void OnNatIntroductionRequest(NatIntroduceRequestPacket req, IPEndPoint senderEndPoint)
        C#源位置: NatPunchModule.cs:197-215

        参数:
            req: NatIntroduceRequestPacket - 请求包
            sender_end_point: tuple - 发送者端点
        """
        if self._unsynced_events:
            self._nat_punch_listener.on_nat_introduction_request(
                req.internal,
                sender_end_point,
                req.token
            )
        else:
            self._request_events.put({
                'local_end_point': req.internal,
                'remote_end_point': sender_end_point,
                'token': req.token
            })

    def _on_nat_introduction_response(self, req: NatIntroduceResponsePacket) -> None:
        """
        收到NAT引入响应

        C#方法: private void OnNatIntroductionResponse(NatIntroduceResponsePacket req)
        C#源位置: NatPunchModule.cs:218-236

        参数:
            req: NatIntroduceResponsePacket - 响应包
        """
        NetDebug.write("[NAT] introduction received")

        # 发送内部打孔
        punch_packet = NatPunchPacket()
        punch_packet.token = req.token
        self._send(punch_packet, req.internal)
        NetDebug.write(f"[NAT] internal punch sent to {req.internal}")

        # 某些路由器的hack
        self._socket.ttl = 2
        from .packets.net_packet import PacketProperty
        self._socket.send_raw(
            bytes([PacketProperty.Empty]),
            0,
            1,
            req.external
        )

        # 发送外部打孔
        self._socket.ttl = NetConstants.socket_ttl
        punch_packet.is_external = True
        self._send(punch_packet, req.external)
        NetDebug.write(f"[NAT] external punch sent to {req.external}")

    def _on_nat_punch(self, req: NatPunchPacket, sender_end_point: tuple) -> None:
        """
        收到NAT打孔

        C#方法: private void OnNatPunch(NatPunchPacket req, IPEndPoint senderEndPoint)
        C#源位置: NatPunchModule.cs:239-262

        参数:
            req: NatPunchPacket - 打孔包
            sender_end_point: tuple - 发送者端点
        """
        NetDebug.write(f"[NAT] punch received from {sender_end_point} - additional info: {req.token}")

        # 释放打孔成功到客户端；如果令牌正确，允许他连接到发送者
        if self._unsynced_events:
            self._nat_punch_listener.on_nat_introduction_success(
                sender_end_point,
                NatAddressType.External if req.is_external else NatAddressType.Internal,
                req.token
            )
        else:
            self._success_events.put({
                'target_end_point': sender_end_point,
                'type': NatAddressType.External if req.is_external else NatAddressType.Internal,
                'token': req.token
            })


__all__ = [
    "NatAddressType",
    "INatPunchListener",
    "EventBasedNatPunchListener",
    "NatPunchModule",
]
