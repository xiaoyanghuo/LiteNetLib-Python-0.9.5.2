"""
NetDataReader.cs translation

Binary data reader for network packets
"""

import struct
from typing import Optional, Type, TypeVar, List, Any

# Avoid circular imports
if False:  # TYPE_CHECKING
    from .net_data_writer import NetDataWriter

T = TypeVar("T", bound="INetSerializable")


class NetDataReader:
    """
    Binary data reader for network packets

    C# class: public class NetDataReader
    """

    def __init__(self, source=None):
        """
        Initialize reader

        C# constructors:
        - NetDataReader()
        - NetDataReader(NetDataWriter writer)
        - NetDataReader(byte[] source)
        - NetDataReader(byte[] source, int offset)
        - NetDataReader(byte[] source, int offset, int maxSize)
        """
        self._data: Optional[bytes] = None
        self._position: int = 0
        self._data_size: int = 0
        self._offset: int = 0

        if source is not None:
            self.set_source(source)

    @property
    def raw_data(self) -> Optional[bytes]:
        """Get raw data bytes"""
        return self._data

    @property
    def raw_data_size(self) -> int:
        """Get raw data size"""
        return self._data_size

    @property
    def user_data_offset(self) -> int:
        """Get user data offset"""
        return self._offset

    @property
    def user_data_size(self) -> int:
        """Get user data size"""
        return self._data_size - self._offset

    @property
    def is_null(self) -> bool:
        """Check if data is null"""
        return self._data is None

    @property
    def position(self) -> int:
        """Get current position"""
        return self._position

    @property
    def end_of_data(self) -> bool:
        """Check if at end of data"""
        return self._position == self._data_size

    @property
    def available_bytes(self) -> int:
        """Get available bytes"""
        return self._data_size - self._position

    def skip_bytes(self, count: int) -> None:
        """
        Skip bytes

        C# method: public void SkipBytes(int count)
        """
        self._position += count

    def set_source(self, source, offset: int = None, max_size: int = None) -> None:
        """
        Set data source

        C# methods:
        - SetSource(NetDataWriter dataWriter)
        - SetSource(byte[] source)
        - SetSource(byte[] source, int offset)
        - SetSource(byte[] source, int offset, int maxSize)
        """
        from .net_data_writer import NetDataWriter

        if isinstance(source, NetDataWriter):
            self._data = bytes(source.data[: source.length])
            self._position = 0
            self._offset = 0
            self._data_size = source.length
        elif isinstance(source, bytes):
            self._data = source
            if offset is None:
                self._position = 0
                self._offset = 0
                self._data_size = len(source)
            elif max_size is None:
                self._position = offset
                self._offset = offset
                self._data_size = len(source)
            else:
                self._position = offset
                self._offset = offset
                self._data_size = max_size
        else:
            raise TypeError("Source must be bytes or NetDataWriter")

    def get_net_endpoint(self):
        """
        Read IPEndPoint

        C# method: public IPEndPoint GetNetEndPoint()
        """
        from ..net_utils import NetUtils

        host = self.get_string(1000)
        port = self.get_int()
        return NetUtils.make_endpoint(host, port)

    def get_byte(self) -> int:
        """
        Read byte

        C# method: public byte GetByte()
        """
        result = self._data[self._position]
        self._position += 1
        return result

    def get_sbyte(self) -> int:
        """
        Read signed byte

        C# method: public sbyte GetSByte()
        """
        result = struct.unpack_from("<b", self._data, self._position)[0]
        self._position += 1
        return result

    def get_bool_array(self) -> List[bool]:
        """
        Read bool array

        C# method: public bool[] GetBoolArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [bool(self._data[self._position + i]) for i in range(size)]
        self._position += size
        return arr

    def get_ushort_array(self) -> List[int]:
        """
        Read ushort array

        C# method: public ushort[] GetUShortArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<H", self._data, self._position + i * 2)[0]
            for i in range(size)
        ]
        self._position += size * 2
        return arr

    def get_short_array(self) -> List[int]:
        """
        Read short array

        C# method: public short[] GetShortArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<h", self._data, self._position + i * 2)[0]
            for i in range(size)
        ]
        self._position += size * 2
        return arr

    def get_long_array(self) -> List[int]:
        """
        Read long array

        C# method: public long[] GetLongArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<q", self._data, self._position + i * 8)[0]
            for i in range(size)
        ]
        self._position += size * 8
        return arr

    def get_ulong_array(self) -> List[int]:
        """
        Read ulong array

        C# method: public ulong[] GetULongArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<Q", self._data, self._position + i * 8)[0]
            for i in range(size)
        ]
        self._position += size * 8
        return arr

    def get_int_array(self) -> List[int]:
        """
        Read int array

        C# method: public int[] GetIntArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<i", self._data, self._position + i * 4)[0]
            for i in range(size)
        ]
        self._position += size * 4
        return arr

    def get_uint_array(self) -> List[int]:
        """
        Read uint array

        C# method: public uint[] GetUIntArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<I", self._data, self._position + i * 4)[0]
            for i in range(size)
        ]
        self._position += size * 4
        return arr

    def get_float_array(self) -> List[float]:
        """
        Read float array

        C# method: public float[] GetFloatArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<f", self._data, self._position + i * 4)[0]
            for i in range(size)
        ]
        self._position += size * 4
        return arr

    def get_double_array(self) -> List[float]:
        """
        Read double array

        C# method: public double[] GetDoubleArray()
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [
            struct.unpack_from("<d", self._data, self._position + i * 8)[0]
            for i in range(size)
        ]
        self._position += size * 8
        return arr

    def get_string_array(self) -> List[str]:
        """
        Read string array

        C# methods:
        - public string[] GetStringArray()
        - public string[] GetStringArray(int maxStringLength)
        """
        size = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        arr = [self.get_string() for _ in range(size)]
        return arr

    def get_bool(self) -> bool:
        """
        Read bool

        C# method: public bool GetBool()
        """
        result = self._data[self._position] > 0
        self._position += 1
        return result

    def get_char(self) -> str:
        """
        Read char

        C# method: public char GetChar()
        """
        result = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        return chr(result)

    def get_ushort(self) -> int:
        """
        Read ushort

        C# method: public ushort GetUShort()
        """
        result = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        return result

    def get_short(self) -> int:
        """
        Read short

        C# method: public short GetShort()
        """
        result = struct.unpack_from("<h", self._data, self._position)[0]
        self._position += 2
        return result

    def get_long(self) -> int:
        """
        Read long

        C# method: public long GetLong()
        """
        result = struct.unpack_from("<q", self._data, self._position)[0]
        self._position += 8
        return result

    def get_ulong(self) -> int:
        """
        Read ulong

        C# method: public ulong GetULong()
        """
        result = struct.unpack_from("<Q", self._data, self._position)[0]
        self._position += 8
        return result

    def get_int(self) -> int:
        """
        Read int

        C# method: public int GetInt()
        """
        result = struct.unpack_from("<i", self._data, self._position)[0]
        self._position += 4
        return result

    def get_uint(self) -> int:
        """
        Read uint

        C# method: public uint GetUInt()
        """
        result = struct.unpack_from("<I", self._data, self._position)[0]
        self._position += 4
        return result

    def get_float(self) -> float:
        """
        Read float

        C# method: public float GetFloat()
        """
        result = struct.unpack_from("<f", self._data, self._position)[0]
        self._position += 4
        return result

    def get_double(self) -> float:
        """
        Read double

        C# method: public double GetDouble()
        """
        result = struct.unpack_from("<d", self._data, self._position)[0]
        self._position += 8
        return result

    def get_string(self, max_length: int = 0) -> str:
        """
        Read string

        C# methods:
        - public string GetString(int maxLength)
        - public string GetString()
        """
        bytes_count = self.get_int()
        if bytes_count <= 0:
            return ""

        if max_length > 0 and bytes_count > max_length * 2:
            return ""

        result = self._data[self._position : self._position + bytes_count].decode("utf-8")
        self._position += bytes_count
        return result

    def get_remaining_bytes(self) -> bytes:
        """
        Get remaining bytes

        C# method: public byte[] GetRemainingBytes()
        """
        result = self._data[self._position : self._data_size]
        self._position = self._data_size
        return result

    def get_bytes(self, destination: bytearray, start: int = None, count: int = None) -> None:
        """
        Get bytes

        C# methods:
        - public void GetBytes(byte[] destination, int start, int count)
        - public void GetBytes(byte[] destination, int count)
        """
        if start is None:
            start = 0
        if count is None:
            count = len(destination)

        destination[start : start + count] = self._data[
            self._position : self._position + count
        ]
        self._position += count

    def get_bytes_with_length(self) -> bytes:
        """
        Get bytes with length prefix

        C# method: public byte[] GetBytesWithLength()
        """
        length = self.get_int()
        result = self._data[self._position : self._position + length]
        self._position += length
        return result

    # Peek methods (without advancing position)

    def peek_byte(self) -> int:
        """Peek byte"""
        return self._data[self._position]

    def peek_sbyte(self) -> int:
        """Peek sbyte"""
        return struct.unpack_from("<b", self._data, self._position)[0]

    def peek_bool(self) -> bool:
        """Peek bool"""
        return self._data[self._position] > 0

    def peek_char(self) -> str:
        """Peek char"""
        result = struct.unpack_from("<H", self._data, self._position)[0]
        return chr(result)

    def peek_ushort(self) -> int:
        """Peek ushort"""
        return struct.unpack_from("<H", self._data, self._position)[0]

    def peek_short(self) -> int:
        """Peek short"""
        return struct.unpack_from("<h", self._data, self._position)[0]

    def peek_long(self) -> int:
        """Peek long"""
        return struct.unpack_from("<q", self._data, self._position)[0]

    def peek_ulong(self) -> int:
        """Peek ulong"""
        return struct.unpack_from("<Q", self._data, self._position)[0]

    def peek_int(self) -> int:
        """Peek int"""
        return struct.unpack_from("<i", self._data, self._position)[0]

    def peek_uint(self) -> int:
        """Peek uint"""
        return struct.unpack_from("<I", self._data, self._position)[0]

    def peek_float(self) -> float:
        """Peek float"""
        return struct.unpack_from("<f", self._data, self._position)[0]

    def peek_double(self) -> float:
        """Peek double"""
        return struct.unpack_from("<d", self._data, self._position)[0]

    def peek_string(self, max_length: int = 0) -> str:
        """Peek string"""
        bytes_count = struct.unpack_from("<i", self._data, self._position)[0]
        if bytes_count <= 0:
            return ""

        if max_length > 0 and bytes_count > max_length * 2:
            return ""

        result = self._data[
            self._position + 4 : self._position + 4 + bytes_count
        ].decode("utf-8")
        return result

    # TryGet methods (safe get with bounds checking)

    def try_get_byte(self) -> Optional[int]:
        """Try get byte"""
        if self.available_bytes >= 1:
            return self.get_byte()
        return None

    def try_get_sbyte(self) -> Optional[int]:
        """Try get sbyte"""
        if self.available_bytes >= 1:
            return self.get_sbyte()
        return None

    def try_get_bool(self) -> Optional[bool]:
        """Try get bool"""
        if self.available_bytes >= 1:
            return self.get_bool()
        return False

    def try_get_char(self) -> Optional[str]:
        """Try get char"""
        if self.available_bytes >= 2:
            return self.get_char()
        return None

    def try_get_short(self) -> Optional[int]:
        """Try get short"""
        if self.available_bytes >= 2:
            return self.get_short()
        return None

    def try_get_ushort(self) -> Optional[int]:
        """Try get ushort"""
        if self.available_bytes >= 2:
            return self.get_ushort()
        return None

    def try_get_int(self) -> Optional[int]:
        """Try get int"""
        if self.available_bytes >= 4:
            return self.get_int()
        return None

    def try_get_uint(self) -> Optional[int]:
        """Try get uint"""
        if self.available_bytes >= 4:
            return self.get_uint()
        return None

    def try_get_long(self) -> Optional[int]:
        """Try get long"""
        if self.available_bytes >= 8:
            return self.get_long()
        return None

    def try_get_ulong(self) -> Optional[int]:
        """Try get ulong"""
        if self.available_bytes >= 8:
            return self.get_ulong()
        return None

    def try_get_float(self) -> Optional[float]:
        """Try get float"""
        if self.available_bytes >= 4:
            return self.get_float()
        return None

    def try_get_double(self) -> Optional[float]:
        """Try get double"""
        if self.available_bytes >= 8:
            return self.get_double()
        return None

    def try_get_string(self) -> Optional[str]:
        """Try get string"""
        if self.available_bytes >= 4:
            bytes_count = self.peek_int()
            if self.available_bytes >= bytes_count + 4:
                return self.get_string()
        return None

    def try_get_string_array(self) -> Optional[List[str]]:
        """Try get string array"""
        size = self.try_get_ushort()
        if size is None:
            return None

        result = []
        for _ in range(size):
            s = self.try_get_string()
            if s is None:
                return None
            result.append(s)
        return result

    def try_get_bytes_with_length(self) -> Optional[bytes]:
        """Try get bytes with length"""
        if self.available_bytes >= 4:
            length = self.peek_int()
            if length >= 0 and self.available_bytes >= length + 4:
                return self.get_bytes_with_length()
        return None

    def clear(self) -> None:
        """
        Clear reader

        C# method: public void Clear()
        """
        self._position = 0
        self._data_size = 0
        self._data = None


__all__ = ["NetDataReader"]
