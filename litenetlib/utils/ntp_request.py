"""
NtpRequest.cs 翻译

NTP请求状态管理，处理重发和超时

C#源文件: Utils/NtpRequest.cs
C#行数: ~42行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括基于定时器的重发逻辑和自动请求过期。
"""

import socket
from typing import Tuple
from .ntp_packet import NtpPacket


class NtpRequest:
    """
    NTP请求

    C#定义: internal sealed class NtpRequest
    C#源位置: NtpRequest.cs:6-41

    属性:
        endpoint: Tuple[str, int] - NTP服务器端点
        need_to_kill: bool - 是否需要终止请求

    常量:
        RESEND_TIMER: int - 重发定时器（毫秒）
        KILL_TIMER: int - 终止定时器（毫秒）
        DEFAULT_PORT: int - 默认NTP端口

    方法:
        send() - 发送NTP包
    """

    # C#常量: private const int ResendTimer = 1000
    RESEND_TIMER = 1000  # C#值: 1000 - 重发定时器（1秒）

    # C#常量: private const int KillTimer = 10000
    KILL_TIMER = 10000  # C#值: 10000 - 终止定时器（10秒）

    # C#常量: public const int DefaultPort = 123
    DEFAULT_PORT = 123  # C#值: 123 - 默认NTP端口

    def __init__(self, endpoint: Tuple[str, int]):
        """
        创建NTP请求

        C#构造函数: public NtpRequest(IPEndPoint endPoint)
        C#源位置: NtpRequest.cs:15-18

        参数:
            endpoint: Tuple[str, int] - NTP服务器端点（主机名/IP, 端口）
                C#对应: IPEndPoint endPoint

        说明:
            初始化重发和终止计时器
        """
        self._endpoint = endpoint
        self._resend_time = float(self.RESEND_TIMER)
        self._kill_time = 0.0

    @property
    def endpoint(self) -> Tuple[str, int]:
        """
        获取NTP服务器端点

        C#对应: _ntpEndPoint (private field)

        返回:
            Tuple[str, int]: NTP服务器端点
        """
        return self._endpoint

    @property
    def need_to_kill(self) -> bool:
        """
        检查是否需要终止请求

        C#属性: public bool NeedToKill
        C#源位置: NtpRequest.cs:20

        返回:
            bool: 如果kill时间超过KILL_TIMER返回true，否则返回false
                C#对应: bool

        说明:
            当请求超时（10秒）时，应终止请求
        """
        return self._kill_time >= self.KILL_TIMER

    def send(self, sock: socket.socket, time_delta: float) -> bool:
        """
        发送NTP包

        C#方法: public bool Send(Socket socket, float time)
        C#源位置: NtpRequest.cs:22-40

        参数:
            sock: socket.socket - UDP socket
                C#对应: Socket socket
            time_delta: float - 自上次调用以来经过的时间（秒）
                C#对应: float time

        返回:
            bool: 如果成功发送包返回true，否则返回false
                C#对应: bool

        说明:
            此方法管理重发逻辑：
            - 累加时间到重发和终止计时器
            - 只有当重发计时器超过RESEND_TIMER（1秒）时才发送
            - 发送成功后重置重发计时器
            - 如果发送失败返回false
        """
        self._resend_time += time_delta * 1000  # 转换为毫秒
        self._kill_time += time_delta * 1000  # 转换为毫秒

        if self._resend_time < self.RESEND_TIMER:
            return False

        # 创建NTP请求包
        packet = NtpPacket()

        try:
            # 发送NTP包
            send_count = sock.sendto(packet.bytes, 0, len(packet.bytes), self._endpoint)
            success = send_count == len(packet.bytes)

            if success:
                # 重置重发计时器
                self._resend_time = 0.0

            return success
        except Exception:
            # 发送失败
            return False


__all__ = [
    "NtpRequest",
]
