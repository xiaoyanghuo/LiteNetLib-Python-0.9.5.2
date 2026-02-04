"""
Network data writer for serializing data to binary format.

Provides methods to write various data types in a compact binary format
compatible with LiteNetLib protocol.
"""

import struct
import uuid
from typing import Union, Tuple, List, Optional


class NetDataWriter:
    """
    Binary data writer with auto-resizing buffer.

    Uses little-endian byte order for multi-byte values.
    All data is written as compactly as possible.
    """

    __slots__ = ('_data', '_position', '_auto_resize', '_initial_size')

    def __init__(self, auto_resize: bool = True, initial_size: int = 64):
        """
        Create a new NetDataWriter.

        Args:
            auto_resize: Automatically resize buffer when needed
            initial_size: Initial buffer size in bytes
        """
        self._data = bytearray(initial_size)
        self._position = 0
        self._auto_resize = auto_resize
        self._initial_size = initial_size

    @classmethod
    def from_bytes(cls, data: bytes, copy: bool = True) -> 'NetDataWriter':
        """
        Create NetDataWriter from existing bytes.

        Args:
            data: Source bytes
            copy: Whether to copy the data or reuse the buffer
        """
        writer = cls(auto_resize=True, initial_size=len(data) if copy else 0)
        if copy:
            writer._data = bytearray(data)
            writer._position = len(data)
        else:
            writer._data = bytearray(data)  # Still need to copy as bytearray
            writer._position = len(data)
        return writer

    @classmethod
    def from_bytes_with_offset(cls, data: bytes, offset: int, length: int) -> 'NetDataWriter':
        """
        Create NetDataWriter from existing bytes with offset.

        Args:
            data: Source bytes
            offset: Starting offset in data
            length: Number of bytes to copy
        """
        writer = cls(auto_resize=True, initial_size=length)
        writer._data = bytearray(data[offset:offset + length])
        writer._position = length
        return writer

    @classmethod
    def from_string(cls, value: str) -> 'NetDataWriter':
        """Create NetDataWriter from a string."""
        writer = cls()
        writer.put(value)
        return writer

    @property
    def capacity(self) -> int:
        """Get current buffer capacity."""
        return len(self._data)

    @property
    def data(self) -> bytearray:
        """Get underlying data buffer."""
        return self._data

    @property
    def length(self) -> int:
        """Get current data length (position)."""
        return self._position

    def reset(self, size: Optional[int] = None) -> None:
        """
        Reset writer position.

        Args:
            size: If provided, ensure buffer is at least this size
        """
        if size is not None:
            self._ensure_capacity(size)
        self._position = 0

    def set_position(self, position: int) -> int:
        """
        Set writer position.

        Args:
            position: New position

        Returns:
            Previous position
        """
        prev = self._position
        self._position = position
        return prev

    def copy_data(self) -> bytes:
        """Copy written data to new bytes object."""
        return bytes(self._data[:self._position])

    def to_bytes(self) -> bytes:
        """Get written data as bytes."""
        return bytes(self._data[:self._position])

    def _ensure_capacity(self, size: int) -> None:
        """Ensure buffer has enough capacity."""
        if len(self._data) < size:
            new_size = max(size, len(self._data) * 2)
            self._data.extend(b'\x00' * (new_size - len(self._data)))

    def _resize_if_needed(self, additional_size: int) -> None:
        """Resize buffer if needed for additional data."""
        if self._auto_resize:
            self._ensure_capacity(self._position + additional_size)

    def resize_if_need(self, size: int) -> None:
        """
        Resize buffer if needed.

        Args:
            size: Required minimum size
        """
        if self._auto_resize:
            self._ensure_capacity(size)

    def ensure_fit(self, additional_size: int) -> None:
        """
        Ensure buffer has capacity for additional data.

        Args:
            additional_size: Additional size needed
        """
        self._resize_if_needed(additional_size)

    # Basic types

    def put_byte(self, value: int) -> None:
        """Write a single byte."""
        self._resize_if_needed(1)
        self._data[self._position] = value & 0xFF
        self._position += 1

    def put_sbyte(self, value: int) -> None:
        """Write a signed byte."""
        self.put_byte(value & 0xFF)

    def put_bool(self, value: bool) -> None:
        """Write a boolean as a single byte (0 or 1)."""
        self.put_byte(1 if value else 0)

    def put_short(self, value: int) -> None:
        """Write a 16-bit signed integer."""
        self._resize_if_needed(2)
        struct.pack_into('<h', self._data, self._position, value)
        self._position += 2

    def put_ushort(self, value: int) -> None:
        """Write a 16-bit unsigned integer."""
        self._resize_if_needed(2)
        struct.pack_into('<H', self._data, self._position, value)
        self._position += 2

    def put_int(self, value: int) -> None:
        """Write a 32-bit signed integer."""
        self._resize_if_needed(4)
        struct.pack_into('<i', self._data, self._position, value)
        self._position += 4

    def put_uint(self, value: int) -> None:
        """Write a 32-bit unsigned integer."""
        self._resize_if_needed(4)
        struct.pack_into('<I', self._data, self._position, value)
        self._position += 4

    def put_long(self, value: int) -> None:
        """Write a 64-bit signed integer."""
        self._resize_if_needed(8)
        struct.pack_into('<q', self._data, self._position, value)
        self._position += 8

    def put_ulong(self, value: int) -> None:
        """Write a 64-bit unsigned integer."""
        self._resize_if_needed(8)
        struct.pack_into('<Q', self._data, self._position, value)
        self._position += 8

    def put_float(self, value: float) -> None:
        """Write a 32-bit float."""
        self._resize_if_needed(4)
        struct.pack_into('<f', self._data, self._position, value)
        self._position += 4

    def put_double(self, value: float) -> None:
        """Write a 64-bit double."""
        self._resize_if_needed(8)
        struct.pack_into('<d', self._data, self._position, value)
        self._position += 8

    def put_char(self, value: str) -> None:
        """Write a single character as ushort."""
        self.put_ushort(ord(value[0]) if len(value) > 0 else 0)

    # String types

    def put_string(self, value: str, max_length: int = 0) -> None:
        """
        Write a string with length prefix.

        Args:
            value: String to write
            max_length: Maximum character length (0 = no limit)
        """
        if not value:
            self.put_ushort(0)
            return

        # Truncate if max_length specified
        if max_length > 0 and len(value) > max_length:
            value = value[:max_length]

        encoded = value.encode('utf-8')
        size = len(encoded)

        if size == 0:
            self.put_ushort(0)
            return

        self.put_ushort(size + 1)  # Size + 1 for non-empty string
        self._resize_if_needed(size)
        self._data[self._position:self._position + size] = encoded
        self._position += size

    def put_large_string(self, value: str) -> None:
        """
        Write a potentially large string with int length prefix.

        Args:
            value: String to write
        """
        if not value:
            self.put_int(0)
            return

        encoded = value.encode('utf-8')
        size = len(encoded)

        if size == 0:
            self.put_int(0)
            return

        self.put_int(size)
        self._resize_if_needed(size)
        self._data[self._position:self._position + size] = encoded
        self._position += size

    # Bytes and arrays

    def put_bytes(self, data: bytes, offset: int = 0, length: Optional[int] = None) -> None:
        """
        Write raw bytes.

        Args:
            data: Bytes to write
            offset: Starting offset in data
            length: Number of bytes to write (None = all remaining)
        """
        if length is None:
            length = len(data) - offset
        self._resize_if_needed(length)
        self._data[self._position:self._position + length] = data[offset:offset + length]
        self._position += length

    def put_bytes_with_length(self, data: bytes) -> None:
        """Write bytes with ushort length prefix."""
        length = len(data)
        self.put_ushort(length)
        self.put_bytes(data)

    def put_array(self, arr: Optional[List], element_size: int = 1) -> None:
        """
        Write an array with length prefix.

        Args:
            arr: Array to write (None writes length 0)
            element_size: Size of each element in bytes
        """
        length = len(arr) if arr is not None else 0
        total_size = length * element_size
        self._resize_if_needed(2 + total_size)
        self.put_ushort(length)

        if arr and total_size > 0:
            # Handle different element types
            if element_size == 1:
                # bytes or bool or small integers
                for item in arr:
                    if isinstance(item, bool):
                        self.put_byte(1 if item else 0)
                    else:
                        # Preserve integer values (0-255)
                        self.put_byte(item & 0xFF)
            elif element_size == 2:
                # shorts or ushorts
                for item in arr:
                    self.put_short(item) if isinstance(item, int) and item < 0 else self.put_ushort(item)
            elif element_size == 4:
                # ints or floats
                for item in arr:
                    if isinstance(item, float):
                        self.put_float(item)
                    else:
                        self.put_int(item)
            elif element_size == 8:
                # longs, ulongs, or doubles
                for item in arr:
                    if isinstance(item, float):
                        self.put_double(item)
                    else:
                        self.put_long(item)

    def put_sbytes_with_length(self, data: bytes) -> None:
        """Write sbytes with length prefix."""
        self.put_bytes_with_length(data)

    # Array type-specific methods

    def put_bool_array(self, arr: Optional[List[bool]]) -> None:
        """Write an array of bools."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_bool(item)

    def put_short_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of shorts."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_short(item)

    def put_ushort_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of ushorts."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_ushort(item)

    def put_int_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of ints."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_int(item)

    def put_uint_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of uints."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_uint(item)

    def put_long_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of longs."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_long(item)

    def put_ulong_array(self, arr: Optional[List[int]]) -> None:
        """Write an array of ulongs."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_ulong(item)

    def put_float_array(self, arr: Optional[List[float]]) -> None:
        """Write an array of floats."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_float(item)

    def put_double_array(self, arr: Optional[List[float]]) -> None:
        """Write an array of doubles."""
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)
        if arr:
            for item in arr:
                self.put_double(item)

    def put_string_array(self, arr: Optional[List[str]], max_length: int = 0) -> None:
        """
        Write an array of strings.

        Args:
            arr: Array of strings (None writes length 0)
            max_length: Maximum length for each string
        """
        length = len(arr) if arr is not None else 0
        self.put_ushort(length)

        if arr:
            for s in arr:
                self.put_string(s, max_length)

    # Special types

    def put_uuid(self, value: uuid.UUID) -> None:
        """Write a UUID (16 bytes)."""
        self._resize_if_needed(16)
        self._data[self._position:self._position + 16] = value.bytes
        self._position += 16

    def put_ip_end_point(self, address: str, port: int, family: str = 'IPv4') -> None:
        """
        Write an IP endpoint.

        Args:
            address: IP address string
            port: Port number
            family: 'IPv4' or 'IPv6'
        """
        import socket

        # Normalize family string to handle both 'IPv4' and 'IPV4'
        family_upper = family.upper()
        if family_upper == 'IPV4':
            family_upper = 'IPv4'
        elif family_upper == 'IPV6':
            family_upper = 'IPv6'

        if family_upper == 'IPv4':
            self.put_byte(0)
            addr_bytes = socket.inet_pton(socket.AF_INET, address)
        elif family_upper == 'IPv6':
            self.put_byte(1)
            addr_bytes = socket.inet_pton(socket.AF_INET6, address)
        else:
            raise ValueError(f"Unsupported address family: {family}")

        self.put_bytes(addr_bytes)
        self.put_ushort(port)

    # Convenience methods

    def put(self, value) -> None:
        """
        Write a value based on its type.

        This is a convenience method that automatically selects
        the appropriate put_* method based on the value type.
        """
        if isinstance(value, bool):
            self.put_bool(value)
        elif isinstance(value, int):
            # Determine best integer size
            if -128 <= value <= 127:
                self.put_sbyte(value)
            elif -32768 <= value <= 32767:
                self.put_short(value)
            elif -2147483648 <= value <= 2147483647:
                self.put_int(value)
            else:
                self.put_long(value)
        elif isinstance(value, float):
            self.put_float(value)
        elif isinstance(value, str):
            self.put_string(value)
        elif isinstance(value, bytes):
            self.put_bytes_with_length(value)
        elif isinstance(value, (list, tuple)):
            # Try to determine element type and size
            if value and isinstance(value[0], str):
                self.put_string_array(list(value))
            else:
                # Default to int array
                self.put_array(list(value), 4)
        elif isinstance(value, uuid.UUID):
            self.put_uuid(value)
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    def __len__(self) -> int:
        return self._position

    def __repr__(self) -> str:
        return f"NetDataWriter(position={self._position}, capacity={len(self._data)})"
