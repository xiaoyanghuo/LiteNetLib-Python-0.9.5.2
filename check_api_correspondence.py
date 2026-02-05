"""
C# vs Python API 1对1对应关系检查

检查NetDataWriter和NetDataReader的所有方法是否都有对应实现
"""

import sys
sys.path.insert(0, '.')

from litenetlib.utils import NetDataReader, NetDataWriter

print("=" * 60)
print("C# vs Python API 1对1对应关系检查")
print("=" * 60)

# C# NetDataWriter方法（重载）到Python的对应
c_sharp_to_python_writer = {
    # 基本类型
    "Put(bool)": "put_bool",
    "Put(byte)": "put_byte",
    "Put(sbyte)": "put_sbyte",  # ⚠️ 检查
    "Put(short)": "put_short",
    "Put(ushort)": "put_ushort",
    "Put(int)": "put_int",
    "Put(uint)": "put_uint",
    "Put(long)": "put_long",
    "Put(ulong)": "put_ulong",
    "Put(float)": "put_float",
    "Put(double)": "put_double",
    "Put(string)": "put_string",
    "Put(string, int)": "put_string_max",  # 带max长度

    # 字节数组
    "Put(byte[])": "put_bytes",
    "Put(byte[], int, int)": "put_bytes_offset",  # offset, length
    "Put(Span<byte>)": "put_bytes",  # .NET 5+ Span

    # IPEndPoint
    "Put(IPEndPoint)": "put_endpoint",

    # 数组（泛型方法）
    "PutArray(bool[])": "put_bool_array",
    "PutArray(short[])": "put_short_array",
    "PutArray(ushort[])": "put_ushort_array",
    "PutArray(int[])": "put_int_array",
    "PutArray(uint[])": "put_uint_array",  # ⚠️ 检查
    "PutArray(long[])": "put_long_array",
    "PutArray(ulong[])": "put_ulong_array",  # ⚠️ 检查
    "PutArray(float[])": "put_float_array",
    "PutArray(double[])": "put_double_array",
    "PutArray(string[])": "put_string_array",
}

# C# NetDataReader方法到Python的对应
c_sharp_to_python_reader = {
    # 基本类型
    "GetBool()": "get_bool",
    "GetByte()": "get_byte",
    "GetSByte()": "get_sbyte",
    "GetShort()": "get_short",
    "GetUShort()": "get_ushort",
    "GetInt()": "get_int",
    "GetUInt()": "get_uint",
    "GetLong()": "get_long",
    "GetULong()": "get_ulong",
    "GetFloat()": "get_float",
    "GetDouble()": "get_double",
    "GetString()": "get_string",
    "GetString(int)": "get_string",  # maxLength

    # 字节数组到已有数组
    "GetBytes(byte[], int)": "get_bytes",  # destination, count

    # 数组返回
    "GetBoolArray()": "get_bool_array",
    "GetShortArray()": "get_short_array",
    "GetIntArray()": "get_int_array",
    "GetLongArray()": "get_long_array",
    "GetFloatArray()": "get_float_array",
    "GetDoubleArray()": "get_double_array",
    "GetStringArray()": "get_string_array",

    # 其他
    "GetNetEndPoint()": "get_net_endpoint",
    "GetRemainingBytes()": "get_remaining_bytes",
    "GetBytesWithLength()": "get_bytes_with_length",
}

print("\n=== NetDataWriter 方法检查 ===\n")

writer = NetDataWriter()
writer_methods = [m for m in dir(writer) if not m.startswith('_')]

missing_writer = []
for c_sharp, python in c_sharp_to_python_writer.items():
    if python in writer_methods:
        print(f"[OK] {c_sharp:30} -> {python}")
    else:
        print(f"[X] {c_sharp:30} -> {python} [MISSING]")
        missing_writer.append((c_sharp, python))

print(f"\nNetDataWriter 缺失方法数: {len(missing_writer)}")

print("\n=== NetDataReader 方法检查 ===\n")

reader = NetDataReader()
reader_methods = [m for m in dir(reader) if not m.startswith('_')]

missing_reader = []
for c_sharp, python in c_sharp_to_python_reader.items():
    if python in reader_methods:
        print(f"[OK] {c_sharp:30} -> {python}")
    else:
        print(f"[X] {c_sharp:30} -> {python} [MISSING]")
        missing_reader.append((c_sharp, python))

print(f"\nNetDataReader 缺失方法数: {len(missing_reader)}")

# 特别检查：uint/ulong数组
print("\n=== 特别检查：uint/ulong数组方法 ===\n")

has_uint_array = hasattr(writer, 'put_uint_array')
has_ulong_array = hasattr(writer, 'put_ulong_array')
has_get_uint_array = hasattr(reader, 'get_uint_array')
has_get_ulong_array = hasattr(reader, 'get_ulong_array')

print(f"NetDataWriter.put_uint_array:   {'[OK] Exists' if has_uint_array else '[X] Missing'}")
print(f"NetDataWriter.put_ulong_array:  {'[OK] Exists' if has_ulong_array else '[X] Missing'}")
print(f"NetDataReader.get_uint_array:   {'[OK] Exists' if has_get_uint_array else '[X] Missing'}")
print(f"NetDataReader.get_ulong_array:  {'[OK] Exists' if has_get_ulong_array else '[X] Missing'}")

# 特别检查：sbyte
print("\n=== 特别检查：sbyte方法 ===\n")

has_put_sbyte = hasattr(writer, 'put_sbyte')
has_get_sbyte = hasattr(reader, 'get_sbyte')

print(f"NetDataWriter.put_sbyte:  {'[OK] Exists' if has_put_sbyte else '[X] Missing'}")
print(f"NetDataReader.get_sbyte: {'[OK] Exists' if has_get_sbyte else '[X] Missing'}")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)

total_writer = len(c_sharp_to_python_writer)
missing_writer_count = len(missing_writer)
total_reader = len(c_sharp_to_python_reader)
missing_reader_count = len(missing_reader)

print(f"\nNetDataWriter: {total_writer - missing_writer_count}/{total_writer} 方法存在 ({100 * (total_writer - missing_writer_count) // total_writer}%)" )
print(f"NetDataReader: {total_reader - missing_reader_count}/{total_reader} 方法存在 ({100 * (total_reader - missing_reader_count) // total_reader}%)")

if missing_writer_count == 0 and missing_reader_count == 0:
    print("\n[SUCCESS] All C# APIs have 1-to-1 mapping in Python!")
else:
    print(f"\n[WARNING] Missing {missing_writer_count + missing_reader_count} methods")
    if missing_writer:
        print("\nMissing Writer methods:")
        for cs, py in missing_writer:
            print(f"  - {cs} -> {py}")
    if missing_reader:
        print("\nMissing Reader methods:")
        for cs, py in missing_reader:
            print(f"  - {cs} -> {py}")

print("=" * 60)
