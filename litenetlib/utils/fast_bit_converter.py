"""
Fast binary converter for exact C# compatibility / 快速二进制转换器，与 C# 完全兼容

This module provides little-endian binary encoding that exactly matches
the C# FastBitConverter implementation. All multi-byte values use
little-endian byte order for protocol compatibility.

本模块提供与 C# FastBitConverter 实现完全匹配的小端二进制编码。
所有多字节值使用小端字节序以确保协议兼容性。

Ported from: LiteNetLib/Utils/FastBitConverter.cs
"""

import struct
from typing import Union


class FastBitConverter:
    """
    Fast little-endian binary converter / 快速小端二进制转换器

    Provides methods to write primitive types to byte arrays in little-endian
    format, exactly matching the C# implementation for protocol compatibility.

    提供将基本类型以小端格式写入字节数组的方法，与 C# 实现完全匹配。

    C# Reference: FastBitConverter.GetBytes(byte[], int, T value)
    """

    __slots__ = ()

    @staticmethod
    def get_bytes(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write integer (32-bit) to buffer at offset.
        写入 32 位整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Integer value to write / 要写入的整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, int value)
        """
        struct.pack_into('<i', buffer, offset, value)

    @staticmethod
    def get_bytes_uint(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write unsigned integer (32-bit) to buffer at offset.
        写入 32 位无符号整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Unsigned integer value to write / 要写入的无符号整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, uint value)
        """
        struct.pack_into('<I', buffer, offset, value)

    @staticmethod
    def get_bytes_ushort(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write unsigned short (16-bit) to buffer at offset.
        写入 16 位无符号短整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Unsigned short value to write / 要写入的无符号短整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, ushort value)
        """
        struct.pack_into('<H', buffer, offset, value)

    @staticmethod
    def get_bytes_short(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write short (16-bit) to buffer at offset.
        写入 16 位短整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Short value to write / 要写入的短整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, short value)
        """
        struct.pack_into('<h', buffer, offset, value)

    @staticmethod
    def get_bytes_long(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write long (64-bit) to buffer at offset.
        写入 64 位长整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Long value to write / 要写入的长整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, long value)
        """
        struct.pack_into('<q', buffer, offset, value)

    @staticmethod
    def get_bytes_ulong(buffer: bytearray, offset: int, value: int) -> None:
        """
        Write unsigned long (64-bit) to buffer at offset.
        写入 64 位无符号长整数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Unsigned long value to write / 要写入的无符号长整数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, ulong value)
        """
        struct.pack_into('<Q', buffer, offset, value)

    @staticmethod
    def get_bytes_float(buffer: bytearray, offset: int, value: float) -> None:
        """
        Write float (32-bit IEEE 754) to buffer at offset.
        写入 32 位 IEEE 754 浮点数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Float value to write / 要写入的浮点数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, float value)

        Note: Uses struct.pack with '<f' for exact IEEE 754 binary representation
        matching C# float encoding.
        注意：使用 struct.pack 的 '<f' 格式以实现与 C# float 编码完全匹配的 IEEE 754 二进制表示。
        """
        struct.pack_into('<f', buffer, offset, value)

    @staticmethod
    def get_bytes_double(buffer: bytearray, offset: int, value: float) -> None:
        """
        Write double (64-bit IEEE 754) to buffer at offset.
        写入 64 位 IEEE 754 双精度浮点数到缓冲区指定位置。

        Args:
            buffer: Target byte array / 目标字节数组
            offset: Starting position in buffer / 缓冲区起始位置
            value: Double value to write / 要写入的双精度浮点数值

        C# Equivalent: GetBytes(byte[] bytes, int startIndex, double value)

        Note: Uses struct.pack with '<d' for exact IEEE 754 binary representation
        matching C# double encoding.
        注意：使用 struct.pack 的 '<d' 格式以实现与 C# double 编码完全匹配的 IEEE 754 二进制表示。
        """
        struct.pack_into('<d', buffer, offset, value)


# Convenience functions / 便捷函数
def write_int16(buffer: bytearray, offset: int, value: int) -> None:
    """Write signed 16-bit integer / 写入有符号 16 位整数"""
    FastBitConverter.get_bytes_short(buffer, offset, value)


def write_uint16(buffer: bytearray, offset: int, value: int) -> None:
    """Write unsigned 16-bit integer / 写入无符号 16 位整数"""
    FastBitConverter.get_bytes_ushort(buffer, offset, value)


def write_int32(buffer: bytearray, offset: int, value: int) -> None:
    """Write signed 32-bit integer / 写入有符号 32 位整数"""
    FastBitConverter.get_bytes(buffer, offset, value)


def write_uint32(buffer: bytearray, offset: int, value: int) -> None:
    """Write unsigned 32-bit integer / 写入无符号 32 位整数"""
    FastBitConverter.get_bytes_uint(buffer, offset, value)


def write_int64(buffer: bytearray, offset: int, value: int) -> None:
    """Write signed 64-bit integer / 写入有符号 64 位整数"""
    FastBitConverter.get_bytes_long(buffer, offset, value)


def write_uint64(buffer: bytearray, offset: int, value: int) -> None:
    """Write unsigned 64-bit integer / 写入无符号 64 位整数"""
    FastBitConverter.get_bytes_ulong(buffer, offset, value)


def write_float32(buffer: bytearray, offset: int, value: float) -> None:
    """Write 32-bit float / 写入 32 位浮点数"""
    FastBitConverter.get_bytes_float(buffer, offset, value)


def write_float64(buffer: bytearray, offset: int, value: float) -> None:
    """Write 64-bit double / 写入 64 位双精度浮点数"""
    FastBitConverter.get_bytes_double(buffer, offset, value)
