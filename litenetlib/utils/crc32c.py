"""
CRC32C.cs translation

CRC32C (Castagnoli) checksum implementation
Implementation from Crc32.NET
"""

from typing import List


class CRC32C:
    """
    CRC32C (Castagnoli) checksum calculation

    C# class: public static class CRC32C

    Implementation from Crc32.NET
    Uses polynomial 0x82F63B78 (CRC32C standard)
    """

    CHECKSUM_SIZE = 4
    _POLY = 0x82F63B78

    _TABLE: List[int] = None

    @classmethod
    def _initialize_table(cls) -> None:
        """
        Initialize CRC32C lookup table

        C# method: static CRC32C()
        """
        if cls._TABLE is not None:
            return

        cls._TABLE = [0] * 256
        for i in range(256):
            res = i
            for _ in range(8):
                if (res & 1) == 1:
                    res = cls._POLY ^ (res >> 1)
                else:
                    res = res >> 1
            cls._TABLE[i] = res & 0xFFFFFFFF

    @classmethod
    def compute(cls, data, offset: int = 0, length: int = None) -> int:
        """
        Compute CRC32C checksum for data

        C# method: public static uint Compute(byte[] input, int offset, int length)

        Args:
            data: Input data as bytes or bytearray
            offset: Starting offset in data
            length: Length of data to process (None for remaining data)

        Returns:
            CRC32C checksum as uint32
        """
        # Initialize table if needed
        cls._initialize_table()

        # Convert bytearray to bytes if needed
        if isinstance(data, bytearray):
            data = bytes(data)

        if length is None:
            length = len(data) - offset

        if length == 0:
            return 0

        crc_local = 0xFFFFFFFF

        # Process all bytes
        for i in range(length):
            crc_local = cls._TABLE[((crc_local ^ data[offset + i]) & 0xFF)] ^ (crc_local >> 8)

        return (crc_local ^ 0xFFFFFFFF) & 0xFFFFFFFF


__all__ = ["CRC32C"]
