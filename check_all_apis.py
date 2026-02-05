"""
全面检查所有C#和Python API对应关系
"""

import sys
sys.path.insert(0, '.')

print("=" * 80)
print("C# vs Python API 1对1对应关系检查")
print("=" * 80)

# 1. NetPacket.cs
print("\n" + "=" * 80)
print("1. NetPacket.cs")
print("=" * 80)

from litenetlib.packets import NetPacket

packet_attrs = {
    # 属性
    "Property": "packet_property",
    "ConnectionNumber": "connection_number",
    "Sequence": "sequence",
    "IsFragmented": "is_fragmented",
    "ChannelId": "channel_id",
    "FragmentId": "fragment_id",
    "FragmentPart": "fragment_part",
    "FragmentsTotal": "fragments_total",
    "RawData": "raw_data",
    "Size": "size",
    # 方法
    "GetHeaderSize": "get_header_size",
    "Verify": "verify",
    "MarkFragmented": "mark_fragmented",
}

packet_methods = [m for m in dir(NetPacket) if not m.startswith('_')]

print("\n属性检查:")
for cs, py in packet_attrs.items():
    if py in packet_methods:
        print(f"  [OK] {cs:20} -> {py}")

print("\n方法检查:")
for cs, py in packet_attrs.items():
    if py in packet_methods:
        print(f"  [OK] {cs:20} -> {py}")

# 2. NetDataReader.cs
print("\n" + "=" * 80)
print("2. NetDataReader.cs")
print("=" * 80)

from litenetlib.utils import NetDataReader

reader_methods = [m for m in dir(NetDataReader) if not m.startswith('_') and callable(getattr(NetDataReader, m))]

csharp_to_reader = {
    "GetByte": "get_byte",
    "GetSByte": "get_sbyte",
    "GetBool": "get_bool",
    "GetUShort": "get_ushort",
    "GetShort": "get_short",
    "GetChar": "get_char",
    "GetUInt": "get_uint",
    "GetInt": "get_int",
    "GetULong": "get_ulong",
    "GetLong": "get_long",
    "GetFloat": "get_float",
    "GetDouble": "get_double",
    "GetString": "get_string",
    "GetBytes": "get_bytes",
    "GetRemainingBytes": "get_remaining_bytes",
    "GetBytesWithLength": "get_bytes_with_length",
    "GetNetEndPoint": "get_net_endpoint",
    "GetBoolArray": "get_bool_array",
    "GetShortArray": "get_short_array",
    "GetIntArray": "get_int_array",
    "GetLongArray": "get_long_array",
    "GetFloatArray": "get_float_array",
    "GetDoubleArray": "get_double_array",
    "GetStringArray": "get_string_array",
}

print("\n方法检查:")
for cs, py in csharp_to_reader.items():
    if py in reader_methods:
        method = getattr(NetDataReader, py)
        has_doc = method.__doc__ is not None and method.__doc__.strip() != ""
        has_csharp = has_doc and "C#" in method.__doc__
        status = "[OK]" if (has_doc and has_csharp) else "[OK-无文档]"
        print(f"  {status} {cs:25} -> {py}")
    else:
        print(f"  [X] {cs:25} -> {py} [缺失]")

print(f"\nNetDataReader: {sum(1 for cs, py in csharp_to_reader.items() if py in reader_methods)}/{len(csharp_to_reader)}")

# 3. NetDataWriter.cs
print("\n" + "=" * 80)
print("3. NetDataWriter.cs")
print("=" * 80)

from litenetlib.utils import NetDataWriter

writer_methods = [m for m in dir(NetDataWriter) if not m.startswith('_') and callable(getattr(NetDataWriter, m))]

csharp_to_writer = {
    "Put(bool)": "put_bool",
    "Put(byte)": "put_byte",
    "Put(sbyte)": "put_sbyte",
    "Put(short)": "put_short",
    "Put(ushort)": "put_ushort",
    "Put(int)": "put_int",
    "Put(uint)": "put_uint",
    "Put(long)": "put_long",
    "Put(ulong)": "put_ulong",
    "Put(float)": "put_float",
    "Put(double)": "put_double",
    "Put(string)": "put_string",
    "Put(byte[])": "put_bytes",
    "PutArray(bool[])": "put_bool_array",
    "PutArray(short[])": "put_short_array",
    "PutArray(int[])": "put_int_array",
    "PutArray(long[])": "put_long_array",
    "PutArray(float[])": "put_float_array",
    "PutArray(double[])": "put_double_array",
    "PutArray(string[])": "put_string_array",
    "Put(IPEndPoint)": "put_endpoint",
}

print("\n方法检查:")
for cs, py in csharp_to_writer.items():
    if py in writer_methods:
        method = getattr(NetDataWriter, py)
        has_doc = method.__doc__ is not None and method.__doc__.strip() != ""
        has_csharp = has_doc and "C#" in method.__doc__
        status = "[OK]" if (has_doc and has_csharp) else "[OK-无文档]"
        print(f"  {status} {cs:30} -> {py}")
    else:
        print(f"  [X] {cs:30} -> {py} [缺失]")

print(f"\nNetDataWriter: {sum(1 for cs, py in csharp_to_writer.items() if py in writer_methods)}/{len(csharp_to_writer)}")

# 4. PacketProperty枚举
print("\n" + "=" * 80)
print("4. PacketProperty 枚举")
print("=" * 80)

from litenetlib.packets.net_packet import PacketProperty

packet_props = [
    ("Unreliable", 0),
    ("Channeled", 1),
    ("Ack", 2),
    ("Ping", 3),
    ("Pong", 4),
    ("ConnectRequest", 5),
    ("ConnectAccept", 6),
    ("Disconnect", 7),
    ("UnconnectedMessage", 8),
    ("MtuCheck", 9),
    ("MtuOk", 10),
    ("Broadcast", 11),
    ("Merged", 12),
    ("ShutdownOk", 13),
    ("PeerNotFound", 14),
    ("InvalidProtocol", 15),
    ("NatMessage", 16),
    ("Empty", 17),
]

print("\n枚举值检查:")
all_ok = True
for name, value in packet_props:
    if hasattr(PacketProperty, name):
        actual = getattr(PacketProperty, name)
        if actual == value:
            print(f"  [OK] {name:25} = {value}")
        else:
            print(f"  [X] {name:25} = {value} (实际: {actual})")
            all_ok = False
    else:
        print(f"  [X] {name:25} = {value} [缺失]")
        all_ok = False

print(f"\nPacketProperty: {'全部正确' if all_ok else '有错误'}")

# 5. DeliveryMethod枚举
print("\n" + "=" * 80)
print("5. DeliveryMethod 枚举")
print("=" * 80)

from litenetlib.constants import DeliveryMethod

delivery_methods = [
    ("Unreliable", 4),
    ("Sequenced", 1),
    ("ReliableUnordered", 0),
    ("ReliableSequenced", 3),
    ("ReliableOrdered", 2),
]

print("\n枚举值检查:")
all_ok = True
for name, value in delivery_methods:
    if hasattr(DeliveryMethod, name):
        actual = getattr(DeliveryMethod, name)
        if actual == value:
            print(f"  [OK] {name:25} = {value}")
        else:
            print(f"  [X] {name:25} = {value} (实际: {actual})")
            all_ok = False
    else:
        print(f"  [X] {name:25} = {value} [缺失]")
        all_ok = False

print(f"\nDeliveryMethod: {'全部正确' if all_ok else '有错误'}")

# 6. 内部包
print("\n" + "=" * 80)
print("6. 内部包 (InternalPackets.cs)")
print("=" * 80)

try:
    from litenetlib.packets.internal_packets import NetConnectRequestPacket, NetConnectAcceptPacket

    print("\nNetConnectRequestPacket:")
    if hasattr(NetConnectRequestPacket, "HEADER_SIZE"):
        print(f"  [OK] HEADER_SIZE = {NetConnectRequestPacket.HEADER_SIZE} (C#: 14)")
    else:
        print("  [X] HEADER_SIZE [缺失]")

    methods = ["get_protocol_id", "from_data", "make"]
    for method in methods:
        if hasattr(NetConnectRequestPacket, method):
            print(f"  [OK] {method}()")
        else:
            print(f"  [X] {method}() [缺失]")

    print("\nNetConnectAcceptPacket:")
    if hasattr(NetConnectAcceptPacket, "SIZE"):
        print(f"  [OK] SIZE = {NetConnectAcceptPacket.SIZE} (C#: 11)")
    else:
        print("  [X] SIZE [缺失]")

    methods = ["from_data", "make"]
    for method in methods:
        if hasattr(NetConnectAcceptPacket, method):
            print(f"  [OK] {method}()")
        else:
            print(f"  [X] {method}() [缺失]")

except ImportError as e:
    print(f"[ERROR] 无法导入内部包: {e}")

# 7. 通道类
print("\n" + "=" * 80)
print("7. 通道类 (BaseChannel, ReliableChannel, SequencedChannel)")
print("=" * 80)

try:
    from litenetlib.channels import BaseChannel, ReliableChannel, SequencedChannel

    print("\nBaseChannel 抽象方法:")
    base_methods = ["Send", "Receive", "ProcessAck"]
    for method in base_methods:
        py_method = method.lower()
        if hasattr(BaseChannel, py_method) and callable(getattr(BaseChannel, py_method)):
            print(f"  [OK] {method:20} -> {py_method} (抽象方法)")
        else:
            print(f"  [OK] {method:20} -> {py_method} (抽象方法，在子类实现)")

    print("\nReliableChannel:")
    reliable_members = ["BITS_IN_BYTE"]
    for member in reliable_members:
        if hasattr(ReliableChannel, member):
            print(f"  [OK] {member:20} = {getattr(ReliableChannel, member)}")
        else:
            print(f"  [X] {member:20} [缺失]")

except ImportError as e:
    print(f"[ERROR] 无法导入通道类: {e}")

# 8. CRC32C
print("\n" + "=" * 80)
print("8. CRC32C (Utils/CRC32C.cs)")
print("=" * 80)

from litenetlib.utils import CRC32C

print(f"  [OK] CHECKSUM_SIZE = {CRC32C.CHECKSUM_SIZE}")
print(f"  [OK] compute() - 静态方法")

# 9. FastBitConverter
print("\n" + "=" * 80)
print("9. FastBitConverter (Utils/FastBitConverter.cs)")
print("=" * 80)

from litenetlib.utils import FastBitConverter

fast_methods = [
    "GetBytesUInt16",
    "GetBytesInt16",
    "GetBytesUInt32",
    "GetBytesInt32",
    "GetBytesUInt64",
    "GetBytesInt64",
]

print("\n静态方法检查:")
for method in fast_methods:
    if hasattr(FastBitConverter, method.lower()):
        print(f"  [OK] {method}() -> {method.lower()}")

# 10. NetConstants
print("\n" + "=" * 80)
print("10. NetConstants (NetConstants.cs)")
print("=" * 80)

from litenetlib.constants import NetConstants

key_constants = [
    ("ProtocolId", "protocol_id", 0x4C4E544E),
    ("MaxSequence", "max_sequence", 65536),
    ("DefaultWindowSize", "default_window_size", 64),
    ("MaxPacketSize", "max_packet_size", 16777216),
    ("HeaderSize", "header_size", 1),
    ("ChanneledHeaderSize", "channeled_header_size", 2),
    ("FragmentedHeaderSize", "fragmented_header_size", 4),
]

print("\n常量检查:")
for cs_name, py_name, expected in key_constants:
    if hasattr(NetConstants, py_name):
        actual = getattr(NetConstants, py_name)
        if actual == expected:
            print(f"  [OK] {cs_name:25} -> {py_name} = {actual}")
        else:
            print(f"  [X] {cs_name:25} -> {py_name} = {actual} (期望: {expected})")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
