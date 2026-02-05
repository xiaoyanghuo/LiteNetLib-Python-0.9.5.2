"""
FastBitConverter.cs translation

Fast binary conversion utilities for little-endian byte order
"""

import struct
from typing import Union


class FastBitConverter:
    """
    Fast bit converter for little-endian byte order

    C# class: public static class FastBitConverter

    Note: Python's struct module is used instead of explicit layout structs
    All operations use little-endian byte order ('<' prefix) to match C# behavior
    """

    @staticmethod
    def _write_little_endian_int64(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write 64-bit integer in little-endian format

        C# method: private static void WriteLittleEndian(byte[] buffer, int offset, ulong data)
        """
        struct.pack_into("<Q", buffer, offset, value & 0xFFFFFFFFFFFFFFFF)

    @staticmethod
    def _write_little_endian_int32(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write 32-bit integer in little-endian format

        C# method: private static void WriteLittleEndian(byte[] buffer, int offset, int data)
        """
        struct.pack_into("<I", buffer, offset, value & 0xFFFFFFFF)

    @staticmethod
    def _write_little_endian_int16(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write 16-bit integer in little-endian format

        C# method: public static void WriteLittleEndian(byte[] buffer, int offset, short data)
        """
        struct.pack_into("<H", buffer, offset, value & 0xFFFF)

    @staticmethod
    def get_bytes_double(buffer: bytearray, offset: int, value: float) -> None:
        """
        Convert double to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, double value)
        """
        struct.pack_into("<d", buffer, offset, value)

    @staticmethod
    def get_bytes_float(buffer: bytearray, offset: int, value: float) -> None:
        """
        Convert float to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, float value)
        """
        struct.pack_into("<f", buffer, offset, value)

    @staticmethod
    def get_bytes_int16(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert int16 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, short value)
        """
        FastBitConverter._write_little_endian_int16(buffer, offset, value)

    @staticmethod
    def get_bytes_uint16(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert uint16 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, ushort value)
        """
        FastBitConverter._write_little_endian_int16(buffer, offset, value)

    @staticmethod
    def get_bytes_int32(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert int32 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, int value)
        """
        FastBitConverter._write_little_endian_int32(buffer, offset, value)

    @staticmethod
    def get_bytes_uint32(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert uint32 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, uint value)
        """
        FastBitConverter._write_little_endian_int32(buffer, offset, value)

    @staticmethod
    def get_bytes_int64(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert int64 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, long value)
        """
        FastBitConverter._write_little_endian_int64(buffer, offset, value)

    @staticmethod
    def get_bytes_uint64(buffer: bytearray, offset: int, value: int) -> None:
        """
        Convert uint64 to bytes and write to buffer

        C# method: public static void GetBytes(byte[] bytes, int startIndex, ulong value)
        """
        FastBitConverter._write_little_endian_int64(buffer, offset, value)

    @staticmethod
    def set_bytes(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write integer as bytes to buffer at offset

        C# method: public static void SetBytes(byte[] buffer, int offset, int value)
        C#源位置: Utils/FastBitConverter.cs

        This is a convenience method that writes an integer in little-endian format.
        The size depends on the value range (auto-detected).

        Args:
            buffer: Target buffer
            offset: Starting position in buffer
            value: Integer value to write
        """
        # Auto-detect size needed (like C# version)
        if value < 0:
            # Signed negative - use int64
            struct.pack_into("<q", buffer, offset, value)
        elif value <= 0xFF:
            # Fits in 1 byte
            buffer[offset] = value & 0xFF
        elif value <= 0xFFFF:
            # Fits in 2 bytes (ushort)
            struct.pack_into("<H", buffer, offset, value)
        elif value <= 0xFFFFFFFF:
            # Fits in 4 bytes (uint)
            struct.pack_into("<I", buffer, offset, value)
        else:
            # Needs 8 bytes (ulong)
            struct.pack_into("<Q", buffer, offset, value)


__all__ = ["FastBitConverter"]
