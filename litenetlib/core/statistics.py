"""
Network statistics for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 网络统计

Tracks network traffic and packet statistics.
追踪网络流量和数据包统计。

Ported from: LiteNetLib/NetStatistics.cs (v0.9.5.2)
"""


class NetStatistics:
    """
    Network statistics class / 网络统计类

    Tracks packets sent/received, bytes transferred, and packet loss.
    追踪发送/接收的数据包、传输字节数和丢包情况。

    C# Reference: NetStatistics
    """

    def __init__(self):
        """Create statistics object / 创建统计对象"""
        self._packets_sent: int = 0
        self._packets_received: int = 0
        self._bytes_sent: int = 0
        self._bytes_received: int = 0
        self._packet_loss: int = 0

    @property
    def packets_sent(self) -> int:
        """Get number of packets sent / 获取已发送数据包数"""
        return self._packets_sent

    @property
    def packets_received(self) -> int:
        """Get number of packets received / 获取已接收数据包数"""
        return self._packets_received

    @property
    def bytes_sent(self) -> int:
        """Get number of bytes sent / 获取已发送字节数"""
        return self._bytes_sent

    @property
    def bytes_received(self) -> int:
        """Get number of bytes received / 获取已接收字节数"""
        return self._bytes_received

    @property
    def packet_loss(self) -> int:
        """Get number of lost packets / 获取丢包数"""
        return self._packet_loss

    @property
    def packet_loss_percent(self) -> float:
        """Get packet loss percentage / 获取丢包百分比"""
        total = self._packets_sent + self._packet_loss
        if total == 0:
            return 0.0
        return (self._packet_loss / total) * 100.0

    def reset(self) -> None:
        """Reset all statistics / 重置所有统计"""
        self._packets_sent = 0
        self._packets_received = 0
        self._bytes_sent = 0
        self._bytes_received = 0
        self._packet_loss = 0

    def increment_packets_sent(self) -> None:
        """Increment packets sent counter / 递增发送计数"""
        self._packets_sent += 1

    def increment_packets_received(self) -> None:
        """Increment packets received counter / 递增接收计数"""
        self._packets_received += 1

    def add_bytes_sent(self, count: int) -> None:
        """
        Add bytes sent / 添加发送字节数

        Args:
            count: Number of bytes to add
        """
        self._bytes_sent += count

    def add_bytes_received(self, count: int) -> None:
        """
        Add bytes received / 添加接收字节数

        Args:
            count: Number of bytes to add
        """
        self._bytes_received += count

    def increment_packet_loss(self) -> None:
        """Increment packet loss counter / 递增丢包计数"""
        self._packet_loss += 1

    def add_packet_loss(self, count: int) -> None:
        """
        Add packet loss / 添加丢包数

        Args:
            count: Number of lost packets
        """
        self._packet_loss += count

    def __str__(self) -> str:
        """Format statistics as string / 格式化统计为字符串"""
        return (
            f"NetStatistics("
            f"sent={self._packets_sent}, "
            f"received={self._packets_received}, "
            f"bytes_sent={self._bytes_sent}, "
            f"bytes_received={self._bytes_received}, "
            f"loss={self._packet_loss} ({self.packet_loss_percent:.2f}%)"
            f")"
        )

    def __repr__(self) -> str:
        return self.__str__()
