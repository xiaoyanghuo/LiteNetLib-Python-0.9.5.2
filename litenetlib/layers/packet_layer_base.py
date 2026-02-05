"""
PacketLayerBase.cs translation

Base class for packet processing layers
"""

from abc import ABC, abstractmethod


class PacketLayerBase(ABC):
    """
    Base class for packet processing layers

    C# class: public abstract class PacketLayerBase
    """

    @abstractmethod
    def process_out_bound_packet(self, data: bytes, offset: int, length: int) -> bytes:
        """
        Process outgoing packet

        C# method: public abstract void ProcessOutBoundPacket(byte[] data, int offset, int length)
        """
        pass

    @abstractmethod
    def process_in_bound_packet(self, data: bytes, offset: int, length: int) -> bool:
        """
        Process incoming packet

        C# method: public abstract bool ProcessInBoundPacket(byte[] data, int offset, int length)
        """
        pass


__all__ = ["PacketLayerBase"]
