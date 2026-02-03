"""
Network utility functions for LiteNetLib v0.9.5.2 / LiteNetLib 网络工具函数

Ported from: LiteNetLib/Utils/NetUtils.cs
"""

import time
import random
from litenetlib.core.constants import NetConstants


class NetUtils:
    """
    Utility functions for network operations / 网络操作工具函数

    Ported from C# NetUtils class.
    """

    @staticmethod
    def relative_sequence_number(number: int, expected: int) -> int:
        """
        Calculate relative sequence number considering wrap-around.
        计算相对序列号，考虑循环回绕。

        Ported from C# implementation:
        RelativeSequenceNumber(int number, int expected)

        Args:
            number: The sequence number to evaluate / 要评估的序列号
            expected: The reference/expected sequence number / 参考/期望的序列号

        Returns:
            Relative distance (can be negative for wrap-around)
            相对距离（循环回绕时可以为负）

        C# Formula:
        (number - expected + MaxSequence + HalfMaxSequence) % MaxSequence - HalfMaxSequence
        """
        # C#: (number - expected + MaxSequence + HalfMaxSequence) % MaxSequence - HalfMaxSequence
        return (number - expected + NetConstants.MAX_SEQUENCE + NetConstants.HALF_MAX_SEQUENCE) % NetConstants.MAX_SEQUENCE - NetConstants.HALF_MAX_SEQUENCE

    @staticmethod
    def is_sequence_less_than(s1: int, s2: int) -> bool:
        """
        Check if s1 < s2 considering sequence wrap-around.
        检查 s1 是否小于 s2（考虑序列号循环）。

        Args:
            s1: First sequence number / 第一个序列号
            s2: Second sequence number / 第二个序列号

        Returns:
            True if s1 < s2 in circular sense / 在循环意义上 s1 < s2 时返回 True
        """
        return NetUtils.relative_sequence_number(s1, s2) < 0

    @staticmethod
    def is_sequence_greater_than(s1: int, s2: int) -> bool:
        """
        Check if s1 > s2 considering sequence wrap-around.
        检查 s1 是否大于 s2（考虑序列号循环）。

        Args:
            s1: First sequence number / 第一个序列号
            s2: Second sequence number / 第二个序列号

        Returns:
            True if s1 > s2 in circular sense / 在循环意义上 s1 > s2 时返回 True
        """
        return NetUtils.relative_sequence_number(s1, s2) > 0

    @staticmethod
    def get_time_millis() -> int:
        """
        Get current time in milliseconds.
        获取当前时间（毫秒）。

        Returns:
            Current time in milliseconds / 当前毫秒时间戳
        """
        return int(time.time() * 1000)

    @staticmethod
    def get_time_ticks() -> int:
        """
        Get current time in ticks (100ns units).
        获取当前时间（刻度，100ns 单位）。

        Returns:
            Current time in ticks / 当前刻度时间戳
        """
        return int(time.time() * 10000000)

    @staticmethod
    def random_bytes(length: int) -> bytes:
        """
        Generate random bytes.
        生成随机字节。

        Args:
            length: Number of bytes to generate / 要生成的字节数

        Returns:
            Random bytes / 随机字节
        """
        return bytes(random.getrandbits(8) for _ in range(length))

    @staticmethod
    def generate_connect_id() -> int:
        """
        Generate a random connection ID.
        生成随机连接 ID。

        Returns:
            Random connection ID / 随机连接 ID
        """
        return random.randint(0, 0xFFFFFFFF)

    @staticmethod
    def parse_address(address: str) -> tuple:
        """
        Parse address string into host and port.
        将地址字符串解析为主机和端口。

        Args:
            address: Address string (e.g., "127.0.0.1:7777" or "[::1]:7777")
            地址字符串（例如 "127.0.0.1:7777" 或 "[::1]:7777"）

        Returns:
            Tuple of (host, port) / (主机, 端口) 元组
        """
        if address.startswith('['):
            # IPv6
            if ']:' in address:
                # Split on the last ']:' to separate host from port
                parts = address.rsplit(']:', 1)
                host = parts[0][1:]  # Remove opening bracket
                port = int(parts[1]) if len(parts) > 1 else None
                return host, port
            # No port, just remove brackets
            return address[1:-1], None
        else:
            # IPv4
            parts = address.rsplit(':', 1)
            if len(parts) == 2:
                return parts[0], int(parts[1])
            return parts[0], None

    @staticmethod
    def format_address(host: str, port: int) -> str:
        """
        Format host and port into address string.
        将主机和端口格式化为地址字符串。

        Args:
            host: Host address / 主机地址
            port: Port number / 端口号

        Returns:
            Formatted address string / 格式化的地址字符串
        """
        if ':' in host:
            # IPv6
            return f"[{host}]:{port}"
        return f"{host}:{port}"
