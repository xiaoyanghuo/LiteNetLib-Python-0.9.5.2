"""
MTU discovery for LiteNetLib.

Implements dynamic Path MTU Discovery to optimize packet size.
探测网络路径的最大传输单元，优化数据包大小。

Ported from: LiteNetLib/NetPeer.cs (MTU Discovery相关部分)
"""

import time
from typing import Optional
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, NetConstants


class MtuDiscovery:
    """
    MTU discovery manager / MTU 发现管理器

    Implements binary search style MTU discovery using predefined MTU values.
    实现二分查找式的 MTU 发现，使用预定义的 MTU 值。
    """

    def __init__(self):
        """Initialize MTU discovery / 初始化 MTU 发现"""
        self._mtu_index = len(NetConstants.POSSIBLE_MTU) - 1  # Start from largest
        self._last_check_time = -1  # Use -1 to indicate no checks yet
        self._check_attempts = 0
        self._max_attempts = 5
        self._check_delay = 1000  # ms between checks
        self._current_mtu = NetConstants.INITIAL_MTU
        self._discovery_complete = False

    @property
    def current_mtu(self) -> int:
        """Get current MTU value / 获取当前 MTU 值"""
        return self._current_mtu

    @property
    def is_discovery_complete(self) -> bool:
        """Check if MTU discovery is complete / 检查 MTU 发现是否完成"""
        return self._discovery_complete

    def reset(self) -> None:
        """Reset MTU discovery / 重置 MTU 发现"""
        self._mtu_index = len(NetConstants.POSSIBLE_MTU) - 1
        self._last_check_time = 0
        self._check_attempts = 0
        self._current_mtu = NetConstants.INITIAL_MTU
        self._discovery_complete = False

    def get_next_mtu(self) -> Optional[int]:
        """
        Get next MTU value to try / 获取下一个要尝试的 MTU 值

        Returns:
            Next MTU value or None if no more to try / 下一个 MTU 值或 None

        C# Reference: NetPeer.SendMtuPacket
        """
        if self._mtu_index < 0:
            return None

        mtu = NetConstants.POSSIBLE_MTU[self._mtu_index]
        return mtu

    def start_check(self, current_time: int) -> bool:
        """
        Check if it's time to send MTU probe / 检查是否应该发送 MTU 探测包

        Args:
            current_time: Current time in milliseconds / 当前时间（毫秒）

        Returns:
            True if should send probe / 是否应该发送探测包

        C# Reference: NetPeer.Update (MTU check logic)
        """
        if self._discovery_complete:
            return False

        if self._mtu_index < 0:
            # Tried all MTU values
            self._discovery_complete = True
            return False

        # Allow first check immediately, or check if enough time has passed
        # C#: if (currentTime - _mtuCheckTime > _mtuCheckDelay)
        if self._last_check_time == -1 or current_time - self._last_check_time >= self._check_delay:
            return True

        return False

    def send_probe(self, current_time: int) -> Optional[NetPacket]:
        """
        Create MTU probe packet / 创建 MTU 探测数据包

        Args:
            current_time: Current time in milliseconds / 当前时间（毫秒）

        Returns:
            MTU check packet or None / MTU 检查数据包或 None

        C# Reference: NetPeer.SendMtuPacket
        """
        mtu = self.get_next_mtu()
        if mtu is None:
            self._discovery_complete = True
            return None

        # Create MTU check packet with size equal to MTU
        # C#: var packet = new NetPacket(PacketProperty.MtuCheck, mtu);
        packet = NetPacket(PacketProperty.MTU_CHECK, mtu)

        # Record check time
        # C#: _mtuCheckTime = currentTime;
        self._last_check_time = current_time

        return packet

    def handle_success(self, mtu: int) -> None:
        """
        Handle successful MTU probe / 处理 MTU 探测成功

        Args:
            mtu: Successful MTU value / 成功的 MTU 值

        C# Reference: NetPeer.OnMtuOk
        """
        self._current_mtu = mtu
        self._check_attempts = 0

        # Try larger MTU
        # C#: if (_mtuIdx + 1 < PossibleMtu.Count)
        if self._mtu_index + 1 < len(NetConstants.POSSIBLE_MTU):
            self._mtu_index += 1
        else:
            # Found maximum MTU
            # C#: _mtuSuccess = true;
            self._discovery_complete = True

    def handle_failure(self) -> None:
        """
        Handle MTU probe failure / 处理 MTU 探测失败

        C# Reference: NetPeer.Update (MTU timeout logic)
        """
        self._check_attempts += 1

        # C#: if (_checkAttempts >= _maxAttempts || _mtuIdx == 0)
        if self._check_attempts >= self._max_attempts or self._mtu_index == 0:
            # Current MTU too large, try smaller
            # C#: _mtuIdx--;
            self._mtu_index -= 1
            self._check_attempts = 0

            if self._mtu_index < 0:
                # Smallest MTU also failed
                self._discovery_complete = True
                self._current_mtu = NetConstants.INITIAL_MTU

    def should_try_next(self, current_time: int) -> bool:
        """
        Check if should try next MTU value (timeout on current) / 检查是否应该尝试下一个 MTU 值

        Args:
            current_time: Current time in milliseconds / 当前时间（毫秒）

        Returns:
            True if should try smaller MTU / 是否应该尝试更小的 MTU

        C# Reference: NetPeer.Update (MTU timeout)
        """
        if self._discovery_complete:
            return False

        # Check for timeout
        # C#: int timeout = _mtuCheckAttempts * 1000 + 1000;
        timeout = self._check_attempts * 1000 + 1000

        if current_time - self._last_check_time > timeout:
            # Current MTU failed
            self.handle_failure()
            return True

        return False

    def get_max_safe_mtu(self) -> int:
        """
        Get maximum safe MTU that has been successfully tested / 获取已成功测试的最大安全 MTU

        Returns:
            Maximum safe MTU value / 最大安全 MTU 值
        """
        return self._current_mtu

    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        return (f"MtuDiscovery(current={self._current_mtu}, "
                f"index={self._mtu_index}, "
                f"complete={self._discovery_complete})")
