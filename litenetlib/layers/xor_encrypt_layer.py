"""
XorEncryptLayer.cs translation

XOR encryption layer
"""

from .packet_layer_base import PacketLayerBase


class XorEncryptLayer(PacketLayerBase):
    """
    XOR encryption layer

    C# class: public class XorEncryptLayer : PacketLayerBase
    """

    def __init__(self, key: bytes):
        """
        Initialize XOR encryption layer

        C# constructor: public XorEncryptLayer(byte[] key)
        """
        self._key = key
        self._key_length = len(key)

    def process_out_bound_packet(self, data: bytearray, offset: int, length: int) -> None:
        """
        Encrypt outgoing packet with XOR

        C# method: public override void ProcessOutBoundPacket(byte[] data, int offset, int length)
        """
        for i in range(length):
            data[offset + i] ^= self._key[i % self._key_length]

    def process_in_bound_packet(self, data: bytearray, offset: int, length: int) -> bool:
        """
        Decrypt incoming packet with XOR

        C# method: public override bool ProcessInBoundPacket(byte[] data, int offset, int length)
        """
        for i in range(length):
            data[offset + i] ^= self._key[i % self._key_length]
        return True


__all__ = ["XorEncryptLayer"]
