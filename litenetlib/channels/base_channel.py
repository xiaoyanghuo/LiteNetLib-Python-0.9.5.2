"""
BaseChannel.cs 翻译（完整版）

通道基类 - 所有发送通道的抽象基类

C#源文件: BaseChannel.cs
C#行数: ~46行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from queue import Queue

if TYPE_CHECKING:
    from ..packets.net_packet import NetPacket
    from ..lite_net_peer import LiteNetPeer


class BaseChannel(ABC):
    """
    通道基类

    C#定义: internal abstract class BaseChannel
    C#源位置: BaseChannel.cs

    所有发送通道的抽象基类，提供通用功能：
    - 出队队列管理
    - 包发送接口
    - 包处理接口
    """

    def __init__(self, peer: 'LiteNetPeer'):
        """
        创建通道

        C#构造函数: internal BaseChannel(LiteNetPeer peer)
        C#源位置: BaseChannel.cs 构造函数

        参数:
            peer: LiteNetPeer - 所属的peer
        """
        self._peer = peer
        self.outgoing_queue: List['NetPacket'] = []

    @property
    def peer(self) -> 'LiteNetPeer':
        """获取所属peer"""
        return self._peer

    @abstractmethod
    def send_next_packets(self) -> bool:
        """
        发送下一个包

        C#方法: public abstract bool SendNextPackets()
        C#源位置: BaseChannel.cs

        返回:
            bool: 如果有待处理的包返回true
        """
        pass

    @abstractmethod
    def process_packet(self, packet: 'NetPacket') -> bool:
        """
        处理收到的包

        C#方法: public abstract bool ProcessPacket(NetPacket packet)
        C#源位置: BaseChannel.cs

        参数:
            packet: NetPacket - 收到的包

        返回:
            bool: 如果包被处理返回true
        """
        pass

    def add_to_queue(self, packet: 'NetPacket') -> None:
        """
        添加包到队列

        C#方法: internal void AddToQueue(NetPacket packet)
        说明: 将包添加到出队队列

        参数:
            packet: NetPacket - 要添加的包
        """
        self.outgoing_queue.append(packet)

    def add_to_peer_channel_send_queue(self) -> None:
        """
        添加到peer的通道发送队列

        C#方法: internal void AddToPeerChannelSendQueue()
        说明: 将此通道添加到peer的待发送队列

        实现:
            告诉peer这个通道有数据需要发送
        """
        if hasattr(self._peer, 'add_to_reliable_channel_send_queue'):
            self._peer.add_to_reliable_channel_send_queue(self)


__all__ = ["BaseChannel"]
