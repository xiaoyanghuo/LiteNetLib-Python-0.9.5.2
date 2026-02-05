"""
Crc32cLayer.cs translation

CRC32C packet processing layer
"""

from .packet_layer_base import PacketLayerBase
from ..utils.crc32c import CRC32C


class Crc32cLayer(PacketLayerBase):
    """
    CRC32C checksum layer for packet integrity

    C# class: public class Crc32cLayer : PacketLayerBase
    """

    def __init__(self):
        """Initialize CRC32C layer"""
        pass

    def process_out_bound_packet(self, data: bytearray, offset: int, length: int) -> None:
        """
        Add CRC32C checksum to outgoing packet

        C# method: public override void ProcessOutBoundPacket(byte[] data, int offset, int length)
        """
        checksum = CRC32C.compute(data, offset, length)
        # Write checksum at end of packet (after the data)
        # Ensure data has space for checksum
        if offset + length + 4 > len(data):
            raise ValueError(f"Not enough space in data buffer for checksum. Need {offset + length + 4}, have {len(data)}")
        import struct
        struct.pack_into("<I", data, offset + length, checksum)

    def process_in_bound_packet(self, data: bytes, offset: int, length: int) -> bool:
        """
        Verify CRC32C checksum on incoming packet

        C# method: public override bool ProcessInBoundPacket(byte[] data, int offset, int length)
        """
        if length < CRC32C.CHECKSUM_SIZE:
            return False

        received_checksum = int.from_bytes(
            data[offset + length - 4 : offset + length], "little"
        )
        computed_checksum = CRC32C.compute(data, offset, length - 4)

        return received_checksum == computed_checksum


__all__ = ["Crc32cLayer"]
