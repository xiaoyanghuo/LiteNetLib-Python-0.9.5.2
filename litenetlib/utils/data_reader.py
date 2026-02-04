"""
Network data reader for deserializing binary data.

Provides methods to read various data types from a binary buffer
that was written with NetDataWriter.
"""

import struct
import uuid
import socket
from typing import Optional, List, Tuple, Union


class NetDataReader:
    """
    Binary data reader with position tracking.

    Uses little-endian byte order for multi-byte values.
    All data reads must be within the buffer bounds.
    """

    __slots__ = ('_data', '_position', '_data_size', '_offset')

    def __init__(self, source: Optional[bytes] = None, offset: int = 0, max_size: Optional[int] = None):
        """
        Create a new NetDataReader.

        Args:
            source: Source bytes to read from
            offset: Starting offset in source
            max_size: Maximum size to read (None = to end of source)
        """
        if source is not None:
            self._data = memoryview(source)
            self._data_size = len(source) if max_size is None else min(max_size, len(source))
            self._offset = offset
            self._position = offset
        else:
            self._data = memoryview(b'')
            self._data_size = 0
            self._offset = 0
            self._position = 0

    @classmethod
    def from_writer(cls, writer: 'NetDataWriter') -> 'NetDataReader':
        """Create reader from a NetDataWriter."""
        # Import here to avoid circular dependency
        from litenetlib.utils.data_writer import NetDataWriter
        return cls(writer.to_bytes())

    def set_source(self, source: bytes, offset: int = 0, max_size: Optional[int] = None) -> None:
        """
        Set new data source.

        Args:
            source: New source bytes
            offset: Starting offset
            max_size: Maximum size to read
        """
        self._data = memoryview(source)
        self._data_size = len(source) if max_size is None else min(max_size, len(source))
        self._offset = offset
        self._position = offset

    @property
    def position(self) -> int:
        """Get current read position."""
        return self._position

    @property
    def available_bytes(self) -> int:
        """Get remaining bytes available to read."""
        return self._data_size - self._position

    @property
    def end_of_data(self) -> bool:
        """Check if at end of data."""
        return self._position >= self._data_size

    @property
    def is_null(self) -> bool:
        """Check if has no data."""
        return self._data_size == 0

    @property
    def user_data_offset(self) -> int:
        """Get user data offset (if applicable)."""
        return self._offset

    @property
    def user_data_size(self) -> int:
        """Get user data size."""
        return self._data_size - self._offset

    def skip_bytes(self, count: int) -> None:
        """Skip ahead by specified number of bytes."""
        self._position = min(self._position + count, self._data_size)

    def set_position(self, position: int) -> None:
        """Set read position."""
        self._position = max(0, min(position, self._data_size))

    def clear(self) -> None:
        """Clear reader."""
        self._data = memoryview(b'')
        self._data_size = 0
        self._offset = 0
        self._position = 0

    # Basic types

    def get_byte(self) -> int:
        """Read a single byte."""
        if self.available_bytes < 1:
            raise EOFError("Not enough bytes to read byte")
        value = self._data[self._position]
        self._position += 1
        return value

    def get_sbyte(self) -> int:
        """Read a signed byte."""
        b = self.get_byte()
        return b if b < 128 else b - 256

    def get_bool(self) -> bool:
        """Read a boolean (0 = False, 1 = True)."""
        return self.get_byte() == 1

    def get_short(self) -> int:
        """Read a 16-bit signed integer."""
        if self.available_bytes < 2:
            raise EOFError("Not enough bytes to read short")
        value = struct.unpack_from('<h', self._data, self._position)[0]
        self._position += 2
        return value

    def get_ushort(self) -> int:
        """Read a 16-bit unsigned integer."""
        if self.available_bytes < 2:
            raise EOFError("Not enough bytes to read ushort")
        value = struct.unpack_from('<H', self._data, self._position)[0]
        self._position += 2
        return value

    def get_int(self) -> int:
        """Read a 32-bit signed integer."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to read int")
        value = struct.unpack_from('<i', self._data, self._position)[0]
        self._position += 4
        return value

    def get_uint(self) -> int:
        """Read a 32-bit unsigned integer."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to read uint")
        value = struct.unpack_from('<I', self._data, self._position)[0]
        self._position += 4
        return value

    def get_long(self) -> int:
        """Read a 64-bit signed integer."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to read long")
        value = struct.unpack_from('<q', self._data, self._position)[0]
        self._position += 8
        return value

    def get_ulong(self) -> int:
        """Read a 64-bit unsigned integer."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to read ulong")
        value = struct.unpack_from('<Q', self._data, self._position)[0]
        self._position += 8
        return value

    def get_float(self) -> float:
        """Read a 32-bit float."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to read float")
        value = struct.unpack_from('<f', self._data, self._position)[0]
        self._position += 4
        return value

    def get_double(self) -> float:
        """Read a 64-bit double."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to read double")
        value = struct.unpack_from('<d', self._data, self._position)[0]
        self._position += 8
        return value

    def get_char(self) -> str:
        """Read a single character from ushort."""
        return chr(self.get_ushort())

    # String types

    def get_string(self, max_length: int = 0) -> str:
        """
        Read a string with length prefix.

        Args:
            max_length: Maximum character length (0 = no limit)

        Returns:
            Decoded string (empty if exceeds max_length)
        """
        size = self.get_ushort()
        if size == 0:
            return ""

        actual_size = size - 1

        if self.available_bytes < actual_size:
            raise EOFError(f"Not enough bytes to read string (need {actual_size})")

        data = bytes(self._data[self._position:self._position + actual_size])
        self._position += actual_size

        # Decode and check max_length
        try:
            result = data.decode('utf-8')
            if max_length > 0 and len(result) > max_length:
                return ""
            return result
        except UnicodeDecodeError:
            return ""

    def get_large_string(self) -> str:
        """
        Read a potentially large string with int length prefix.

        Returns:
            Decoded string
        """
        size = self.get_int()
        if size <= 0:
            return ""

        if self.available_bytes < size:
            raise EOFError(f"Not enough bytes to read large string (need {size})")

        data = bytes(self._data[self._position:self._position + size])
        self._position += size

        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return ""

    # Bytes and arrays

    def get_bytes(self, count: Optional[int] = None, destination: Optional[bytearray] = None, start: Optional[int] = None) -> Union[bytes, None]:
        """
        Read specified number of bytes, or read into destination array.

        Args:
            count: Number of bytes to read (if destination is None)
            destination: Destination byte array (if provided)
            start: Start position in destination

        Returns:
            Bytes read (if destination is None), None otherwise
        """
        if destination is not None:
            # Read into destination array
            if start is None:
                start = 0
            bytes_to_read = count if count is not None else len(destination) - start
            if self.available_bytes < bytes_to_read:
                raise EOFError(f"Not enough bytes (need {bytes_to_read}, have {self.available_bytes})")
            destination[start:start + bytes_to_read] = self._data[self._position:self._position + bytes_to_read]
            self._position += bytes_to_read
            return None
        else:
            # Read and return bytes
            bytes_to_read = count if count is not None else self.available_bytes
            if self.available_bytes < bytes_to_read:
                raise EOFError(f"Not enough bytes (need {bytes_to_read}, have {self.available_bytes})")
            data = bytes(self._data[self._position:self._position + bytes_to_read])
            self._position += bytes_to_read
            return data

    def get_bytes_with_length(self) -> bytes:
        """Read bytes with ushort length prefix."""
        length = self.get_ushort()
        return self.get_bytes(length)

    def get_remaining_bytes(self) -> bytes:
        """Read all remaining bytes."""
        if self.available_bytes == 0:
            return b''
        data = bytes(self._data[self._position:self._data_size])
        self._position = self._data_size
        return data

    def get_array(self, element_size: int = 1) -> List:
        """
        Read an array with length prefix.

        Args:
            element_size: Size of each element in bytes

        Returns:
            List of elements
        """
        length = self.get_ushort()
        if length == 0:
            return []

        total_size = length * element_size
        if self.available_bytes < total_size:
            raise EOFError(f"Not enough bytes for array (need {total_size})")

        result = []
        data_bytes = self._data[self._position:self._position + total_size]
        self._position += total_size

        for i in range(length):
            offset = i * element_size
            if element_size == 1:
                # byte or bool - preserve byte value as integer 0-255
                result.append(data_bytes[offset])
            elif element_size == 2:
                # short or ushort
                result.append(struct.unpack_from('<H', data_bytes, offset)[0])
            elif element_size == 4:
                # int or uint
                result.append(struct.unpack_from('<I', data_bytes, offset)[0])
            elif element_size == 8:
                # long or ulong
                result.append(struct.unpack_from('<Q', data_bytes, offset)[0])

        return result

    def get_string_array(self, max_length: int = 0) -> List[str]:
        """
        Read an array of strings.

        Args:
            max_length: Maximum length for each string

        Returns:
            List of strings
        """
        length = self.get_ushort()
        return [self.get_string(max_length) for _ in range(length)]

    # Special types

    def get_uuid(self) -> uuid.UUID:
        """Read a UUID (16 bytes)."""
        if self.available_bytes < 16:
            raise EOFError("Not enough bytes to read UUID")
        data = bytes(self._data[self._position:self._position + 16])
        self._position += 16
        return uuid.UUID(bytes=data)

    def get_ip_end_point(self) -> Tuple[str, int, str]:
        """
        Read an IP endpoint.

        Returns:
            Tuple of (address, port, family) where family is 'IPv4' or 'IPv6'
        """
        family_byte = self.get_byte()

        if family_byte == 0:
            # IPv4
            family = 'IPv4'
            addr_bytes = self.get_bytes(4)
            address = socket.inet_ntop(socket.AF_INET, addr_bytes)
        elif family_byte == 1:
            # IPv6
            family = 'IPv6'
            addr_bytes = self.get_bytes(16)
            address = socket.inet_ntop(socket.AF_INET6, addr_bytes)
        else:
            raise ValueError(f"Unknown address family: {family_byte}")

        port = self.get_ushort()
        return (address, port, family)

    # Peek methods (read without advancing position)

    def peek_byte(self) -> int:
        """Peek at next byte without advancing."""
        if self.available_bytes < 1:
            raise EOFError("Not enough bytes to peek")
        return self._data[self._position]

    def peek_bool(self) -> bool:
        """Peek at next boolean without advancing."""
        return self.peek_byte() == 1

    def peek_ushort(self) -> int:
        """Peek at next ushort without advancing."""
        if self.available_bytes < 2:
            raise EOFError("Not enough bytes to peek ushort")
        return struct.unpack_from('<H', self._data, self._position)[0]

    def peek_sbyte(self) -> int:
        """Peek at next sbyte without advancing."""
        b = self.peek_byte()
        return b if b < 128 else b - 256

    def peek_char(self) -> str:
        """Peek at next char without advancing."""
        return chr(self.peek_ushort())

    def peek_short(self) -> int:
        """Peek at next short without advancing."""
        if self.available_bytes < 2:
            raise EOFError("Not enough bytes to peek short")
        return struct.unpack_from('<h', self._data, self._position)[0]

    def peek_long(self) -> int:
        """Peek at next long without advancing."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to peek long")
        return struct.unpack_from('<q', self._data, self._position)[0]

    def peek_ulong(self) -> int:
        """Peek at next ulong without advancing."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to peek ulong")
        return struct.unpack_from('<Q', self._data, self._position)[0]

    def peek_int(self) -> int:
        """Peek at next int without advancing."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to peek int")
        return struct.unpack_from('<i', self._data, self._position)[0]

    def peek_uint(self) -> int:
        """Peek at next uint without advancing."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to peek uint")
        return struct.unpack_from('<I', self._data, self._position)[0]

    def peek_float(self) -> float:
        """Peek at next float without advancing."""
        if self.available_bytes < 4:
            raise EOFError("Not enough bytes to peek float")
        return struct.unpack_from('<f', self._data, self._position)[0]

    def peek_double(self) -> float:
        """Peek at next double without advancing."""
        if self.available_bytes < 8:
            raise EOFError("Not enough bytes to peek double")
        return struct.unpack_from('<d', self._data, self._position)[0]

    def peek_string(self, max_length: int = 0) -> str:
        """
        Peek at next string without advancing position.

        Args:
            max_length: Maximum character length (0 = no limit)

        Returns:
            String (empty if exceeds max_length)
        """
        size = struct.unpack_from('<H', self._data, self._position)[0]
        if size == 0:
            return ""

        actual_size = size - 1
        if self.available_bytes < 2 + actual_size:
            return ""

        try:
            result = bytes(self._data[self._position + 2:self._position + 2 + actual_size]).decode('utf-8')
            if max_length > 0 and len(result) > max_length:
                return ""
            return result
        except UnicodeDecodeError:
            return ""

    # Try methods (safe read with default)

    def try_get_byte(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a byte, return (success, value)."""
        if self.available_bytes >= 1:
            return True, self.get_byte()
        return False, default

    def try_get_bool(self, default: bool = False) -> Tuple[bool, bool]:
        """Try to read a bool, return (success, value)."""
        if self.available_bytes >= 1:
            return True, self.get_bool()
        return False, default

    def try_get_int(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read an int, return (success, value)."""
        if self.available_bytes >= 4:
            return True, self.get_int()
        return False, default

    def try_get_string(self, default: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Try to read a string, return (success, value)."""
        if self.available_bytes >= 2:
            size = struct.unpack_from('<H', self._data, self._position)[0]
            if self.available_bytes >= 2 + size - 1:
                return True, self.get_string()
        return False, default

    def try_get_sbyte(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read an sbyte, return (success, value)."""
        if self.available_bytes >= 1:
            return True, self.get_sbyte()
        return False, default

    def try_get_short(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a short, return (success, value)."""
        if self.available_bytes >= 2:
            return True, self.get_short()
        return False, default

    def try_get_ushort(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a ushort, return (success, value)."""
        if self.available_bytes >= 2:
            return True, self.get_ushort()
        return False, default

    def try_get_uint(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a uint, return (success, value)."""
        if self.available_bytes >= 4:
            return True, self.get_uint()
        return False, default

    def try_get_long(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a long, return (success, value)."""
        if self.available_bytes >= 8:
            return True, self.get_long()
        return False, default

    def try_get_ulong(self, default: int = 0) -> Tuple[bool, int]:
        """Try to read a ulong, return (success, value)."""
        if self.available_bytes >= 8:
            return True, self.get_ulong()
        return False, default

    def try_get_float(self, default: float = 0.0) -> Tuple[bool, float]:
        """Try to read a float, return (success, value)."""
        if self.available_bytes >= 4:
            return True, self.get_float()
        return False, default

    def try_get_double(self, default: float = 0.0) -> Tuple[bool, float]:
        """Try to read a double, return (success, value)."""
        if self.available_bytes >= 8:
            return True, self.get_double()
        return False, default

    def try_get_bytes_with_length(self, default: Optional[bytes] = None) -> Tuple[bool, Optional[bytes]]:
        """Try to read bytes with length prefix, return (success, value)."""
        if self.available_bytes >= 2:
            length = struct.unpack_from('<H', self._data, self._position)[0]
            if self.available_bytes >= 2 + length:
                return True, self.get_bytes_with_length()
        return False, default

    # Array methods

    def get_bool_array(self) -> List[bool]:
        """Read an array of bools."""
        length = self.get_ushort()
        return [self.get_bool() for _ in range(length)]

    def get_short_array(self) -> List[int]:
        """Read an array of shorts."""
        length = self.get_ushort()
        return [self.get_short() for _ in range(length)]

    def get_ushort_array(self) -> List[int]:
        """Read an array of ushorts."""
        length = self.get_ushort()
        return [self.get_ushort() for _ in range(length)]

    def get_int_array(self) -> List[int]:
        """Read an array of ints."""
        length = self.get_ushort()
        return [self.get_int() for _ in range(length)]

    def get_uint_array(self) -> List[int]:
        """Read an array of uints."""
        length = self.get_ushort()
        return [self.get_uint() for _ in range(length)]

    def get_long_array(self) -> List[int]:
        """Read an array of longs."""
        length = self.get_ushort()
        return [self.get_long() for _ in range(length)]

    def get_ulong_array(self) -> List[int]:
        """Read an array of ulongs."""
        length = self.get_ushort()
        return [self.get_ulong() for _ in range(length)]

    def get_float_array(self) -> List[float]:
        """Read an array of floats."""
        length = self.get_ushort()
        return [self.get_float() for _ in range(length)]

    def get_double_array(self) -> List[float]:
        """Read an array of doubles."""
        length = self.get_ushort()
        return [self.get_double() for _ in range(length)]

    # Special methods

    def get_sbytes_with_length(self) -> bytes:
        """Read sbytes with length prefix."""
        return self.get_bytes_with_length()

    def get_remaining_bytes_segment(self) -> bytes:
        """Read all remaining bytes (alias for get_remaining_bytes)."""
        return self.get_remaining_bytes()

    @property
    def raw_data(self) -> memoryview:
        """Get raw underlying data."""
        return self._data

    @property
    def raw_data_size(self) -> int:
        """Get raw data size."""
        return self._data_size

    def __len__(self) -> int:
        return self.available_bytes

    def __repr__(self) -> str:
        return f"NetDataReader(position={self._position}, available={self.available_bytes})"
