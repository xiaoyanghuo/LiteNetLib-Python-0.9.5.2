"""
NetDataWriter.cs translation

Binary data writer for network packets
"""

from .fast_bit_converter import FastBitConverter
from typing import Optional, List, Union


class NetDataWriter:
    """
    Binary data writer for network packets

    C# class: public class NetDataWriter
    """

    INITIAL_SIZE = 64

    def __init__(self, auto_resize: bool = True, initial_size: int = INITIAL_SIZE):
        """
        Initialize writer

        C# constructors:
        - NetDataWriter() : this(true, InitialSize)
        - NetDataWriter(bool autoResize) : this(autoResize, InitialSize)
        - NetDataWriter(bool autoResize, int initialSize)
        """
        self._data: bytearray = bytearray(initial_size)
        self._position: int = 0
        self._auto_resize: bool = auto_resize

    @staticmethod
    def from_bytes(source: bytes, copy: bool = True) -> "NetDataWriter":
        """
        Create from bytes

        C# method: public static NetDataWriter FromBytes(byte[] bytes, bool copy)
        """
        if copy:
            writer = NetDataWriter(True, len(source))
            writer.put_bytes(source)
            return writer
        else:
            writer = NetDataWriter(True, 0)
            writer._data = bytearray(source)
            writer._position = len(source)
            return writer

    @staticmethod
    def from_bytes_offset(source: bytes, offset: int, length: int) -> "NetDataWriter":
        """
        Create from bytes with offset

        C# method: public static NetDataWriter FromBytes(byte[] bytes, int offset, int length)
        """
        writer = NetDataWriter(True, length)
        writer.put_bytes_offset(source, offset, length)
        return writer

    @staticmethod
    def from_string(value: str) -> "NetDataWriter":
        """
        Create from string

        C# method: public static NetDataWriter FromString(string value)
        """
        writer = NetDataWriter()
        writer.put_string(value)
        return writer

    @property
    def capacity(self) -> int:
        """Get capacity"""
        return len(self._data)

    @property
    def data(self) -> bytes:
        """
        Get data

        C# property: public byte[] Data
        """
        return bytes(self._data)

    @property
    def length(self) -> int:
        """
        Get length

        C# property: public int Length
        """
        return self._position

    def resize_if_need(self, new_size: int) -> None:
        """
        Resize if needed

        C# method: public void ResizeIfNeed(int newSize)
        """
        current_len = len(self._data)
        if current_len < new_size:
            while current_len < new_size:
                current_len *= 2
            self._data.extend(b"\x00" * (current_len - len(self._data)))

    def reset(self, size: int = None) -> None:
        """
        Reset writer

        C# methods:
        - public void Reset(int size)
        - public void Reset()
        """
        if size is not None:
            self.resize_if_need(size)
        self._position = 0

    def copy_data(self) -> bytes:
        """
        Copy data

        C# method: public byte[] CopyData()
        """
        return bytes(self._data[: self._position])

    def set_position(self, position: int) -> int:
        """
        Set position

        C# method: public int SetPosition(int position)
        """
        prev_position = self._position
        self._position = position
        return prev_position

    def put_float(self, value: float) -> None:
        """
        Put float value (4 bytes, IEEE 754)

        C# method: public void Put(float value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 4)
        FastBitConverter.get_bytes_float(self._data, self._position, value)
        self._position += 4

    def put_double(self, value: float) -> None:
        """
        Put double value (8 bytes, IEEE 754)

        C# method: public void Put(double value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 8)
        FastBitConverter.get_bytes_double(self._data, self._position, value)
        self._position += 8

    def put_long(self, value: int) -> None:
        """
        Put signed long value (8 bytes)

        C# method: public void Put(long value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 8)
        FastBitConverter.get_bytes_int64(self._data, self._position, value)
        self._position += 8

    def put_ulong(self, value: int) -> None:
        """
        Put unsigned long value (8 bytes)

        C# method: public void Put(ulong value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 8)
        FastBitConverter.get_bytes_uint64(self._data, self._position, value)
        self._position += 8

    def put_int(self, value: int) -> None:
        """
        Put signed integer value (4 bytes)

        C# method: public void Put(int value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 4)
        FastBitConverter.get_bytes_int32(self._data, self._position, value)
        self._position += 4

    def put_uint(self, value: int) -> None:
        """
        Put unsigned integer value (4 bytes)

        C# method: public void Put(uint value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 4)
        FastBitConverter.get_bytes_uint32(self._data, self._position, value)
        self._position += 4

    def put_char(self, value: str) -> None:
        """
        Put char value (2 bytes)

        C# method: public void Put(char value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 2)
        FastBitConverter.get_bytes_int16(self._data, self._position, ord(value))
        self._position += 2

    def put_ushort(self, value: int) -> None:
        """
        Put unsigned short value (2 bytes)

        C# method: public void Put(ushort value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 2)
        FastBitConverter.get_bytes_uint16(self._data, self._position, value)
        self._position += 2

    def put_short(self, value: int) -> None:
        """
        Put signed short value (2 bytes)

        C# method: public void Put(short value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 2)
        FastBitConverter.get_bytes_int16(self._data, self._position, value)
        self._position += 2

    def put_byte(self, value: int) -> None:
        """
        Put unsigned byte value (1 byte)

        C# method: public void Put(byte value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 1)
        self._data[self._position] = value & 0xFF
        self._position += 1

    def put_sbyte(self, value: int) -> None:
        """
        Put signed byte

        C# method: public void Put(sbyte value)
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 1)
        # Convert to unsigned byte representation (two's complement)
        self._data[self._position] = value & 0xFF
        self._position += 1

    def put_bytes(self, data: bytes) -> None:
        """
        Put byte array

        C# method: public void Put(byte[] data)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + len(data))
        self._data[self._position : self._position + len(data)] = data
        self._position += len(data)

    def put_bytes_offset(self, data: bytes, offset: int, length: int) -> None:
        """Put bytes with offset"""
        if self._auto_resize:
            self.resize_if_need(self._position + length)
        self._data[self._position : self._position + length] = data[offset : offset + length]
        self._position += length

    def put_bytes_with_length(self, data: bytes, offset: int = None, length: int = None) -> None:
        """Put bytes with length prefix"""
        if offset is None:
            offset = 0
        if length is None:
            length = len(data)

        if self._auto_resize:
            self.resize_if_need(self._position + length + 4)
        self.put_int(length)
        # After put_int, self._position has already advanced by 4
        # So we write data at the current position
        self._data[self._position : self._position + length] = data[offset : offset + length]
        self._position += length

    def put_bool(self, value: bool) -> None:
        """
        Put boolean value (1 byte)

        C# method: public void Put(bool value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if self._auto_resize:
            self.resize_if_need(self._position + 1)
        self._data[self._position] = 1 if value else 0
        self._position += 1

    def put_array(self, value: Optional[List], element_size: int) -> None:
        """
        Put array

        C# method: private void PutArray(Array arr, int sz)
        """
        length = 0 if value is None else len(value)
        total_size = element_size * length
        if self._auto_resize:
            self.resize_if_need(self._position + total_size + 2)
        self.put_ushort(length)
        if value is not None:
            for item in value:
                if element_size == 1:
                    self.put_byte(1 if item else 0)
                elif element_size == 2:
                    if isinstance(item, bool):
                        self.put_bool(item)
                    else:
                        self.put_short(item)
                elif element_size == 4:
                    if isinstance(item, float):
                        self.put_float(item)
                    else:
                        self.put_int(item)
                elif element_size == 8:
                    if isinstance(item, float):
                        self.put_double(item)
                    else:
                        self.put_long(item)
        # Note: This simplification won't match exact C# memory layout for arrays
        # For exact binary compatibility, we'd need to use struct.pack_into

    def put_float_array(self, value: Optional[List[float]]) -> None:
        """
        Put float array

        C# method: public void PutArray(float[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        import struct
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_float(v)

    def put_double_array(self, value: Optional[List[float]]) -> None:
        """
        Put double array

        C# method: public void PutArray(double[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_double(v)

    def put_long_array(self, value: Optional[List[int]]) -> None:
        """
        Put long array

        C# method: public void PutArray(long[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_long(v)

    def put_ulong_array(self, value: Optional[List[int]]) -> None:
        """
        Put unsigned long array

        C# method: public void PutArray(ulong[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_ulong(v)

    def put_int_array(self, value: Optional[List[int]]) -> None:
        """
        Put integer array

        C# method: public void PutArray(int[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_int(v)

    def put_uint_array(self, value: Optional[List[int]]) -> None:
        """
        Put unsigned integer array

        C# method: public void PutArray(uint[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_uint(v)

    def put_ushort_array(self, value: Optional[List[int]]) -> None:
        """
        Put unsigned short array

        C# method: public void PutArray(ushort[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_ushort(v)

    def put_short_array(self, value: Optional[List[int]]) -> None:
        """
        Put signed short array

        C# method: public void PutArray(short[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_short(v)

    def put_bool_array(self, value: Optional[List[bool]]) -> None:
        """
        Put boolean array

        C# method: public void PutArray(bool[] arr)
        C#源位置: Utils/NetDataWriter.cs
        """
        import struct
        length = 0 if value is None else len(value)
        if self._auto_resize:
            self.resize_if_need(self._position + length + 2)
        self.put_ushort(length)
        if value:
            for v in value:
                self.put_byte(1 if v else 0)

    def put_string_array(self, value: Optional[List[str]], max_length: int = 0) -> None:
        """
        Put string array

        C# method: public void PutArray(string[] arr), public void PutArray(string[] arr, int maxLength)
        C#源位置: Utils/NetDataWriter.cs
        """
        length = 0 if value is None else len(value)
        self.put_ushort(length)
        if value:
            for s in value:
                if max_length > 0:
                    self.put_string_max(s, max_length)
                else:
                    self.put_string(s)

    def put_endpoint(self, endpoint) -> None:
        """
        Put IP endpoint (address and port)

        C# method: public void Put(IPEndPoint endpoint)
        C#源位置: Utils/NetDataWriter.cs
        """
        self.put_string(endpoint[0])
        self.put_int(endpoint[1])

    def put_string(self, value: str) -> None:
        """
        Put string (UTF-8 encoded with length prefix)

        C# method: public void Put(string value)
        C#源位置: Utils/NetDataWriter.cs
        """
        if not value:
            self.put_int(0)
            return

        data = value.encode("utf-8")
        bytes_count = len(data)
        if self._auto_resize:
            self.resize_if_need(self._position + bytes_count + 4)
        self.put_int(bytes_count)
        self._data[self._position : self._position + bytes_count] = data
        self._position += bytes_count

    def put_string_max(self, value: str, max_length: int) -> None:
        """Put string with max length"""
        if not value:
            self.put_int(0)
            return

        data = value.encode("utf-8")
        bytes_count = len(data)
        if self._auto_resize:
            self.resize_if_need(self._position + bytes_count + 4)
        self.put_int(bytes_count)
        self._data[self._position : self._position + bytes_count] = data
        self._position += bytes_count

    def put(self, obj) -> None:
        """Put serializable object"""
        obj.serialize(self)


__all__ = ["NetDataWriter"]
