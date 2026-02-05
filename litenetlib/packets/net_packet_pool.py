"""
NetPacketPool.cs translation

Object pool for network packets to reduce GC pressure
"""

import threading
from typing import Optional
from .net_packet import NetPacket
from ..constants import NetConstants


class NetPacketPool:
    """
    Packet object pool

    C# class: (embedded in NetPacketPool.cs, implemented as static class with pool management)
    """

    def __init__(self):
        """Initialize packet pool"""
        self._head: Optional[NetPacket] = None
        self._count: int = 0
        self._lock = threading.Lock()

    def get_packet(self, size: int, property_value: int = None) -> NetPacket:
        """
        Get packet from pool or create new one

        C# method: public static NetPacket GetPacket(int size)
        """
        # Don't pool oversized packets
        if size > NetConstants.MaxPacketSize:
            return NetPacket(size, property_value)

        packet = None

        with self._lock:
            packet = self._head
            if packet is not None:
                self._head = packet.next
                self._count -= 1

        if packet is None:
            return NetPacket(size, property_value)

        # Reset packet
        packet.size = size
        packet.next = None
        packet.user_data = None

        # If property was specified, set it (this also sets header size)
        if property_value is not None:
            # Need to resize and set property for recycled packet
            from .net_packet import PacketProperty
            size += PacketProperty.get_header_size(property_value)
            if len(packet._raw_data) < size:
                packet._raw_data = bytearray(size)
            packet.packet_property = property_value
            packet.size = size

        return packet

    def recycle(self, packet: NetPacket) -> None:
        """
        Return packet to pool

        C# method: public static void Recycle(NetPacket packet)
        """
        # Don't pool oversized packets
        if packet.size > NetConstants.MaxPacketSize:
            return

        # Don't exceed pool size
        if self._count >= NetConstants.PacketPoolSize:
            return

        self._count += 1

        with self._lock:
            packet.next = self._head
            self._head = packet


__all__ = ["NetPacketPool"]
