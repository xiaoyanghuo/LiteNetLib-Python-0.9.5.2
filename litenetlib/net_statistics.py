"""
NetStatistics.cs translation

Network statistics tracking
"""

import threading
from typing import Optional


class NetStatistics:
    """
    Network statistics for a peer

    C# class: public class NetStatistics
    """

    def __init__(self):
        """Initialize statistics"""
        self._packets_sent: int = 0
        self._packets_received: int = 0
        self._bytes_sent: int = 0
        self._bytes_received: int = 0
        self._packet_loss: int = 0
        self._duplicate_packets: int = 0
        self._rtt: int = 0
        self._rtt_min: int = 0
        self._rtt_max: int = 0
        _lock = threading.Lock()

    @property
    def packets_sent(self) -> int:
        """Get packets sent count"""
        return self._packets_sent

    @property
    def packets_received(self) -> int:
        """Get packets received count"""
        return self._packets_received

    @property
    def bytes_sent(self) -> int:
        """Get bytes sent"""
        return self._bytes_sent

    @property
    def bytes_received(self) -> int:
        """Get bytes received"""
        return self._bytes_received

    @property
    def packet_loss(self) -> int:
        """Get packet loss count"""
        return self._packet_loss

    @property
    def duplicate_packets(self) -> int:
        """Get duplicate packets count"""
        return self._duplicate_packets

    @property
    def rtt(self) -> int:
        """Get current round trip time"""
        return self._rtt

    @property
    def ping(self) -> int:
        """
        Get ping (half of RTT)

        C# property: public int Ping
        """
        return self._rtt // 2 if self._rtt > 0 else 0

    @property
    def rtt_min(self) -> int:
        """Get minimum RTT"""
        return self._rtt_min

    @property
    def rtt_max(self) -> int:
        """Get maximum RTT"""
        return self._rtt_max

    def increment_packets_sent(self) -> None:
        """Increment packets sent counter"""
        self._packets_sent += 1

    def increment_packets_received(self) -> None:
        """Increment packets received counter"""
        self._packets_received += 1

    def add_bytes_sent(self, count: int) -> None:
        """Add bytes sent"""
        self._bytes_sent += count

    def add_bytes_received(self, count: int) -> None:
        """Add bytes received"""
        self._bytes_received += count

    def increment_packet_loss(self) -> None:
        """Increment packet loss counter"""
        self._packet_loss += 1

    def increment_duplicate_packets(self) -> None:
        """Increment duplicate packets counter"""
        self._duplicate_packets += 1

    def update_rtt(self, rtt: int) -> None:
        """
        Update RTT

        C# method: internal void UpdateRoundTripTime(int rtt)
        """
        self._rtt = rtt
        if self._rtt_min == 0 or rtt < self._rtt_min:
            self._rtt_min = rtt
        if rtt > self._rtt_max:
            self._rtt_max = rtt

    def reset(self) -> None:
        """Reset all statistics"""
        self._packets_sent = 0
        self._packets_received = 0
        self._bytes_sent = 0
        self._bytes_received = 0
        self._packet_loss = 0
        self._duplicate_packets = 0
        self._rtt = 0
        self._rtt_min = 0
        self._rtt_max = 0


__all__ = ["NetStatistics"]
