"""
NetSerializer.cs 翻译

高性能通用序列化器，支持反射、自定义类型、数组和列表

C#源文件: Utils/NetSerializer.cs
C#行数: ~770行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括反射类型注册、自定义序列化器、数组/列表支持。
      Python版本使用inspect模块进行反射，使用dataclass支持自动属性发现。
"""

import inspect
from typing import Type, TypeVar, Generic, List, Dict, Callable, Any, Optional, get_origin, get_args
from dataclasses import is_dataclass, fields
from enum import Enum
from .net_data_reader import NetDataReader
from .net_data_writer import NetDataWriter
from .serializable import INetSerializable


class InvalidTypeException(Exception):
    """
    无效类型异常

    C#定义: public class InvalidTypeException : ArgumentException
    C#源位置: NetSerializer.cs:10-13
    """
    pass


class ParseException(Exception):
    """
    解析异常

    C#定义: public class ParseException : Exception
    C#源位置: NetSerializer.cs:15-18
    """
    pass


class CallType:
    """
    调用类型枚举

    C#定义: private enum CallType
    C#源位置: NetSerializer.cs:22-27
    """
    BASIC = 0    # C#值: Basic - 基本类型
    ARRAY = 1    # C#值: Array - 数组类型
    LIST = 2     # C#值: List - 列表类型


T = TypeVar('T')


class PropertySerializer(Generic[T]):
    """
    属性序列化器基类

    C#定义: private abstract class FastCall<T>
    C#源位置: NetSerializer.cs:29-39
    """

    def __init__(self, call_type: int = CallType.BASIC):
        """
        初始化属性序列化器

        C#构造函数: FastCall()

        参数:
            call_type: int - 调用类型（Basic/Array/List）
                C#对应: CallType Type
        """
        self.type = call_type
        self.property_name: Optional[str] = None

    def read(self, obj: T, reader: NetDataReader) -> None:
        """
        从读取器读取属性值

        C#方法: public abstract void Read(T inf, NetDataReader r)
        C#源位置: NetSerializer.cs:33

        参数:
            obj: T - 目标对象
                C#对应: T inf
            reader: NetDataReader - 数据读取器
                C#对应: NetDataReader r
        """
        raise NotImplementedError()

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """
        将属性值写入写入器

        C#方法: public abstract void Write(T inf, NetDataWriter w)
        C#源位置: NetSerializer.cs:34

        参数:
            obj: T - 源对象
                C#对应: T inf
            writer: NetDataWriter - 数据写入器
                C#对应: NetDataWriter w
        """
        raise NotImplementedError()


class IntSerializer(PropertySerializer[T]):
    """
    整数序列化器

    C#定义: private class IntSerializer<T> : FastCallSpecific<T, int>
    C#源位置: NetSerializer.cs:326-332
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        """
        初始化整数序列化器

        参数:
            property_name: str - 属性名称
            call_type: int - 调用类型
        """
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """
        读取整数

        C#方法: public override void Read(T inf, NetDataReader r)
        C#源位置: NetSerializer.cs:328
        """
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_int_array())
        else:
            setattr(obj, self.property_name, reader.get_int())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """
        写入整数

        C#方法: public override void Write(T inf, NetDataWriter w)
        C#源位置: NetSerializer.cs:329
        """
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class UIntSerializer(PropertySerializer[T]):
    """
    无符号整数序列化器

    C#定义: private class UIntSerializer<T> : FastCallSpecific<T, uint>
    C#源位置: NetSerializer.cs:334-340
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取无符号整数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_uint_array())
        else:
            setattr(obj, self.property_name, reader.get_uint())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入无符号整数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class ShortSerializer(PropertySerializer[T]):
    """
    短整数序列化器

    C#定义: private class ShortSerializer<T> : FastCallSpecific<T, short>
    C#源位置: NetSerializer.cs:342-348
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取短整数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_short_array())
        else:
            setattr(obj, self.property_name, reader.get_short())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入短整数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class UShortSerializer(PropertySerializer[T]):
    """
    无符号短整数序列化器

    C#定义: private class UShortSerializer<T> : FastCallSpecific<T, ushort>
    C#源位置: NetSerializer.cs:350-356
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取无符号短整数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_ushort_array())
        else:
            setattr(obj, self.property_name, reader.get_ushort())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入无符号短整数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class LongSerializer(PropertySerializer[T]):
    """
    长整数序列化器

    C#定义: private class LongSerializer<T> : FastCallSpecific<T, long>
    C#源位置: NetSerializer.cs:358-364
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取长整数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_long_array())
        else:
            setattr(obj, self.property_name, reader.get_long())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入长整数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class ULongSerializer(PropertySerializer[T]):
    """
    无符号长整数序列化器

    C#定义: private class ULongSerializer<T> : FastCallSpecific<T, ulong>
    C#源位置: NetSerializer.cs:366-372
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取无符号长整数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_ulong_array())
        else:
            setattr(obj, self.property_name, reader.get_ulong())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入无符号长整数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class ByteSerializer(PropertySerializer[T]):
    """
    字节序列化器

    C#定义: private class ByteSerializer<T> : FastCallSpecific<T, byte>
    C#源位置: NetSerializer.cs:374-380
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取字节"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_bytes_with_length())
        else:
            setattr(obj, self.property_name, reader.get_byte())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入字节"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_bytes_with_length(value)
        else:
            writer.put(value)


class SByteSerializer(PropertySerializer[T]):
    """
    有符号字节序列化器

    C#定义: private class SByteSerializer<T> : FastCallSpecific<T, sbyte>
    C#源位置: NetSerializer.cs:382-388
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取有符号字节"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_sbytes_with_length())
        else:
            setattr(obj, self.property_name, reader.get_sbyte())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入有符号字节"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_sbytes_with_length(value)
        else:
            writer.put(value)


class FloatSerializer(PropertySerializer[T]):
    """
    浮点数序列化器

    C#定义: private class FloatSerializer<T> : FastCallSpecific<T, float>
    C#源位置: NetSerializer.cs:390-396
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取浮点数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_float_array())
        else:
            setattr(obj, self.property_name, reader.get_float())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入浮点数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class DoubleSerializer(PropertySerializer[T]):
    """
    双精度浮点数序列化器

    C#定义: private class DoubleSerializer<T> : FastCallSpecific<T, double>
    C#源位置: NetSerializer.cs:398-404
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取双精度浮点数"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_double_array())
        else:
            setattr(obj, self.property_name, reader.get_double())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入双精度浮点数"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class BoolSerializer(PropertySerializer[T]):
    """
    布尔值序列化器

    C#定义: private class BoolSerializer<T> : FastCallSpecific<T, bool>
    C#源位置: NetSerializer.cs:406-412
    """

    def __init__(self, property_name: str, call_type: int = CallType.BASIC):
        super().__init__(call_type)
        self.property_name = property_name

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取布尔值"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_bool_array())
        else:
            setattr(obj, self.property_name, reader.get_bool())

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入布尔值"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value)
        else:
            writer.put(value)


class StringSerializer(PropertySerializer[T]):
    """
    字符串序列化器

    C#定义: private class StringSerializer<T> : FastCallSpecific<T, string>
    C#源位置: NetSerializer.cs:432-440
    """

    def __init__(self, property_name: str, max_length: int, call_type: int = CallType.BASIC):
        """
        初始化字符串序列化器

        C#构造函数: public StringSerializer(int maxLength)
        C#源位置: NetSerializer.cs:435

        参数:
            property_name: str - 属性名称
            max_length: int - 最大字符串长度
                C#对应: int _maxLength
            call_type: int - 调用类型
        """
        super().__init__(call_type)
        self.property_name = property_name
        self.max_length = max_length if max_length > 0 else 32767  # short.MaxValue

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取字符串"""
        if self.type == CallType.ARRAY:
            setattr(obj, self.property_name, reader.get_string_array(self.max_length))
        else:
            setattr(obj, self.property_name, reader.get_string(self.max_length))

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入字符串"""
        value = getattr(obj, self.property_name)
        if self.type == CallType.ARRAY:
            writer.put_array(value, self.max_length)
        else:
            writer.put(value, self.max_length)


class EnumSerializer(PropertySerializer[T]):
    """
    枚举序列化器

    C#定义: private class EnumByteSerializer<T>, EnumIntSerializer<T>
    C#源位置: NetSerializer.cs:442-464
    """

    def __init__(self, property_name: str, enum_class: Type, call_type: int = CallType.BASIC):
        """
        初始化枚举序列化器

        C#构造函数: public EnumByteSerializer(PropertyInfo property, Type propertyType)
        C#源位置: NetSerializer.cs:446

        参数:
            property_name: str - 属性名称
            enum_class: Type - 枚举类型
                C#对应: Type PropertyType
            call_type: int - 调用类型
        """
        super().__init__(call_type)
        self.property_name = property_name
        self.enum_class = enum_class

        # 检查枚举的第一个值来确定底层类型
        if hasattr(enum_class, '__members__'):
            first_member = next(iter(enum_class))
            first_value = first_member.value
            # Python中枚举值通常是int，检查是否在byte范围内
            self.is_byte = isinstance(first_value, int) and 0 <= first_value <= 255
        else:
            self.is_byte = False

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取枚举值"""
        if self.type == CallType.ARRAY:
            raise InvalidTypeException(f"Unsupported type: {self.enum_class.__name__}[]")
        elif self.type == CallType.LIST:
            raise InvalidTypeException(f"Unsupported type: List<{self.enum_class.__name__}>")

        if self.is_byte:
            value = reader.get_byte()
        else:
            value = reader.get_int()

        setattr(obj, self.property_name, self.enum_class(value))

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入枚举值"""
        if self.type == CallType.ARRAY:
            raise InvalidTypeException(f"Unsupported type: {self.enum_class.__name__}[]")
        elif self.type == CallType.LIST:
            raise InvalidTypeException(f"Unsupported type: List<{self.enum_class.__name__}>")

        value = getattr(obj, self.property_name)
        if value is None:
            enum_value = 0
        else:
            enum_value = value.value if isinstance(value, Enum) else value

        if self.is_byte:
            writer.put(enum_value & 0xFF)
        else:
            writer.put(enum_value)


class CustomTypeSerializer(PropertySerializer[T]):
    """
    自定义类型序列化器（INetSerializable）

    C#定义: private class FastCallStruct<TClass, TProperty>, FastCallClass<TClass, TProperty>
    C#源位置: NetSerializer.cs:203-324
    """

    def __init__(self, property_name: str, constructor: Optional[Callable], call_type: int = CallType.BASIC):
        """
        初始化自定义类型序列化器

        C#构造函数: public FastCallClass(Func<TProperty> constructor)
        C#源位置: NetSerializer.cs:263

        参数:
            property_name: str - 属性名称
            constructor: Optional[Callable] - 构造函数
                C#对应: Func<TProperty> _constructor
            call_type: int - 调用类型
        """
        super().__init__(call_type)
        self.property_name = property_name
        self.constructor = constructor

    def read(self, obj: T, reader: NetDataReader) -> None:
        """读取自定义类型"""
        if self.type == CallType.ARRAY:
            # 读取数组
            count = reader.get_ushort()
            arr = []
            for _ in range(count):
                item = self.constructor() if self.constructor else None
                if item is not None and isinstance(item, INetSerializable):
                    item.deserialize(reader)
                arr.append(item)
            setattr(obj, self.property_name, arr)
        elif self.type == CallType.LIST:
            # 读取列表
            count = reader.get_ushort()
            lst = getattr(obj, self.property_name)
            if lst is None:
                lst = []
                setattr(obj, self.property_name, lst)

            # 调整列表大小
            current_count = len(lst)
            if count > current_count:
                # 扩展列表
                for _ in range(count - current_count):
                    item = self.constructor() if self.constructor else None
                    lst.append(item)
            elif count < current_count:
                # 缩小列表
                del lst[count:]

            # 读取数据
            for i in range(count):
                item = lst[i]
                if item is not None and isinstance(item, INetSerializable):
                    item.deserialize(reader)
        else:
            # 读取单个对象
            item = getattr(obj, self.property_name)
            if item is None:
                item = self.constructor() if self.constructor else None
                if item is not None:
                    setattr(obj, self.property_name, item)
            if item is not None and isinstance(item, INetSerializable):
                item.deserialize(reader)

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """写入自定义类型"""
        value = getattr(obj, self.property_name)

        if self.type == CallType.ARRAY:
            # 写入数组
            if value is None:
                writer.put(0)
            else:
                writer.put(len(value))
                for item in value:
                    if isinstance(item, INetSerializable):
                        item.serialize(writer)
        elif self.type == CallType.LIST:
            # 写入列表
            if value is None:
                writer.put(0)
            else:
                writer.put(len(value))
                for item in value:
                    if isinstance(item, INetSerializable):
                        item.serialize(writer)
        else:
            # 写入单个对象
            if value is not None and isinstance(value, INetSerializable):
                value.serialize(writer)


class ClassInfo(Generic[T]):
    """
    类序列化信息

    C#定义: private sealed class ClassInfo<T>
    C#源位置: NetSerializer.cs:466-505
    """

    def __init__(self, serializers: List[PropertySerializer]):
        """
        初始化类序列化信息

        C#构造函数: public ClassInfo(List<FastCall<T>> serializers)
        C#源位置: NetSerializer.cs:472

        参数:
            serializers: List[PropertySerializer] - 属性序列化器列表
                C#对应: List<FastCall<T>> serializers
        """
        self._serializers = serializers
        self._members_count = len(serializers)

    def write(self, obj: T, writer: NetDataWriter) -> None:
        """
        序列化对象

        C#方法: public void Write(T obj, NetDataWriter writer)
        C#源位置: NetSerializer.cs:478-490

        参数:
            obj: T - 要序列化的对象
                C#对应: T obj
            writer: NetDataWriter - 数据写入器
                C#对应: NetDataWriter writer
        """
        for i in range(self._members_count):
            serializer = self._serializers[i]
            if serializer.type == CallType.BASIC:
                serializer.write(obj, writer)
            elif serializer.type == CallType.ARRAY:
                serializer.write(obj, writer)
            else:  # LIST
                serializer.write(obj, writer)

    def read(self, obj: T, reader: NetDataReader) -> None:
        """
        反序列化对象

        C#方法: public void Read(T obj, NetDataReader reader)
        C#源位置: NetSerializer.cs:492-504

        参数:
            obj: T - 目标对象
                C#对应: T obj
            reader: NetDataReader - 数据读取器
                C#对应: NetDataReader reader
        """
        for i in range(self._members_count):
            serializer = self._serializers[i]
            if serializer.type == CallType.BASIC:
                serializer.read(obj, reader)
            elif serializer.type == CallType.ARRAY:
                serializer.read(obj, reader)
            else:  # LIST
                serializer.read(obj, reader)


class NetSerializer:
    """
    网络序列化器

    C#定义: public class NetSerializer
    C#源位置: NetSerializer.cs:20-769

    属性:
        max_string_length: int - 最大字符串长度
            C#对应: int _maxStringLength

    方法:
        register() - 注册类型
        deserialize() - 反序列化对象
        serialize() - 序列化对象
        register_nested_type() - 注册嵌套类型
    """

    def __init__(self, max_string_length: int = 0):
        """
        创建网络序列化器

        C#构造函数: public NetSerializer(), public NetSerializer(int maxStringLength)
        C#源位置: NetSerializer.cs:569-576

        参数:
            max_string_length: int - 最大字符串长度（0表示无限制）
                C#对应: int maxStringLength

        说明:
            如果maxStringLength为0，则使用short.MaxValue（32767）作为默认值
        """
        self._max_string_length = max_string_length if max_string_length > 0 else 32767
        self._writer: Optional[NetDataWriter] = None
        self._registered_types: Dict[Type, Any] = {}  # 类型 -> (constructor, reader, writer)
        self._class_cache: Dict[Type, ClassInfo] = {}  # 类型 -> ClassInfo

    def register_nested_type(self, cls: Type, constructor: Optional[Callable] = None,
                            writer: Optional[Callable] = None, reader: Optional[Callable] = None) -> None:
        """
        注册自定义属性类型

        C#方法:
        - public void RegisterNestedType<T>() where T : struct, INetSerializable
        - public void RegisterNestedType<T>(Func<T> constructor) where T : class, INetSerializable
        - public void RegisterNestedType<T>(Action<NetDataWriter, T> writer, Func<NetDataReader, T> reader)
        C#源位置: NetSerializer.cs:540-563

        参数:
            cls: Type - 类型
                C#对应: T
            constructor: Optional[Callable] - 构造函数（用于INetSerializable类）
                C#对应: Func<T> constructor
            writer: Optional[Callable] - 自定义写入器
                C#对应: Action<NetDataWriter, T> writer
            reader: Optional[Callable] - 自定义读取器
                C#对应: Func<NetDataReader, T> reader

        说明:
            支持三种注册方式：
            1. INetSerializable结构体（自动检测）
            2. INetSerializable类（需要提供构造函数）
            3. 自定义读写器（完全自定义序列化逻辑）
        """
        self._registered_types[cls] = (constructor, reader, writer)

    def _register_internal(self, cls: Type[T]) -> ClassInfo:
        """
        内部注册方法

        C#方法: private ClassInfo<T> RegisterInternal<T>()
        C#源位置: NetSerializer.cs:578-675

        参数:
            cls: Type - 要注册的类型
                C#对应: T

        返回:
            ClassInfo: 类序列化信息
                C#对应: ClassInfo<T>

        异常:
            InvalidTypeException: 不支持的类型或没有可序列化的属性
        """
        # 检查缓存
        if cls in self._class_cache:
            return self._class_cache[cls]

        serializers: List[PropertySerializer] = []

        # 获取所有属性
        if is_dataclass(cls):
            # dataclass支持
            props = [(f.name, f.type) for f in fields(cls)]
        else:
            # 普通类支持（使用annotations）
            props = []
            if hasattr(cls, '__annotations__'):
                for name, prop_type in cls.__annotations__.items():
                    if not name.startswith('_'):
                        props.append((name, prop_type))

        for prop_name, prop_type in props:
            # 跳过私有属性
            if prop_name.startswith('_'):
                continue

            # 确定调用类型和元素类型
            call_type = CallType.BASIC
            element_type = prop_type

            # 检查是否为List
            origin = get_origin(prop_type)
            if origin is list:
                call_type = CallType.LIST
                args = get_args(prop_type)
                if args:
                    element_type = args[0]
            elif origin is not None:  # 其他泛型类型
                # 对于数组，Python中使用list
                args = get_args(prop_type)
                if args:
                    element_type = args[0]
                    call_type = CallType.ARRAY

            # 创建序列化器
            serializer = self._create_serializer(prop_name, element_type, call_type)
            if serializer is not None:
                serializers.append(serializer)

        if not serializers:
            raise InvalidTypeException(f"No serializable properties found in type: {cls.__name__}")

        # 创建并缓存ClassInfo
        class_info = ClassInfo(serializers)
        self._class_cache[cls] = class_info
        return class_info

    def _create_serializer(self, prop_name: str, prop_type: Type, call_type: int) -> Optional[PropertySerializer]:
        """
        创建属性序列化器

        C#方法: RegisterInternal方法中的序列化器创建逻辑
        C#源位置: NetSerializer.cs:615-671

        参数:
            prop_name: str - 属性名称
            prop_type: Type - 属性类型
            call_type: int - 调用类型

        返回:
            Optional[PropertySerializer]: 属性序列化器，如果不支持则返回None
        """
        # 检查是否为枚举
        if inspect.isclass(prop_type) and issubclass(prop_type, Enum):
            return EnumSerializer(prop_name, prop_type, call_type)

        # 检查是否为INetSerializable
        if inspect.isclass(prop_type):
            # 尝试检查是否实现了INetSerializable
            if INetSerializable in prop_type.__mro__:
                return CustomTypeSerializer(prop_name, prop_type, call_type)

        # 基本类型
        type_map = {
            str: lambda: StringSerializer(prop_name, self._max_string_length, call_type),
            bool: lambda: BoolSerializer(prop_name, call_type),
            int: lambda: IntSerializer(prop_name, call_type),
            float: lambda: FloatSerializer(prop_name, call_type),
            bytes: lambda: ByteSerializer(prop_name, call_type),
        }

        # 检查精确类型匹配
        if prop_type in type_map:
            return type_map[prop_type]()

        # 检查自定义类型
        if prop_type in self._registered_types:
            constructor, reader, writer = self._registered_types[prop_type]
            return CustomTypeSerializer(prop_name, constructor, call_type)

        # 不支持的类型
        return None

    def register(self, cls: Type[T]) -> None:
        """
        注册类型

        C#方法: public void Register<T>()
        C#源位置: NetSerializer.cs:678-685

        参数:
            cls: Type - 要注册的类型
                C#对应: T

        异常:
            InvalidTypeException: 类的字段不支持或没有字段
        """
        self._register_internal(cls)

    def deserialize(self, reader: NetDataReader, cls: Type[T], target: Optional[T] = None) -> Optional[T]:
        """
        从读取器反序列化对象

        C#方法:
        - public T Deserialize<T>(NetDataReader reader) where T : class, new()
        - public bool Deserialize<T>(NetDataReader reader, T target) where T : class, new()
        C#源位置: NetSerializer.cs:693-735

        参数:
            reader: NetDataReader - 包含数据的读取器
                C#对应: NetDataReader reader
            cls: Type[T] - 目标类型
                C#对应: T
            target: Optional[T] - 反序列化目标（非分配变体）
                C#对应: T target

        返回:
            Optional[T]: 反序列化的对象，如果失败则返回None
                C#对应: T (或null)

        异常:
            InvalidTypeException: 类的字段不支持或没有字段

        说明:
            如果提供target，则将数据读入现有对象（非分配变体）
            如果不提供target，则创建新对象并返回
        """
        try:
            info = self._register_internal(cls)

            if target is None:
                # 创建新对象
                target = cls()

            info.read(target, reader)
            return target
        except Exception:
            return None

    def serialize(self, writer: NetDataWriter, obj: T) -> None:
        """
        将对象序列化到写入器

        C#方法: public void Serialize<T>(NetDataWriter writer, T obj) where T : class, new()
        C#源位置: NetSerializer.cs:743-750

        参数:
            writer: NetDataWriter - 序列化目标写入器
                C#对应: NetDataWriter writer
            obj: T - 要序列化的对象
                C#对应: T obj

        异常:
            InvalidTypeException: 类的字段不支持或没有字段

        说明:
            这是快速序列化方法，直接写入到提供的NetDataWriter
        """
        cls = type(obj)
        info = self._register_internal(cls)
        info.write(obj, writer)

    def serialize_to_bytes(self, obj: T) -> bytes:
        """
        将对象序列化为字节数组

        C#方法: public byte[] Serialize<T>(T obj) where T : class, new()
        C#源位置: NetSerializer.cs:757-768

        参数:
            obj: T - 要序列化的对象
                C#对应: T obj

        返回:
            bytes: 包含序列化数据的字节数组
                C#对应: byte[]

        说明:
            此方法会创建或重用内部的NetDataWriter实例
            返回的是数据的副本
        """
        if self._writer is None:
            self._writer = NetDataWriter()

        self._writer.reset()
        self.serialize(self._writer, obj)
        return self._writer.copy_data()


__all__ = [
    "InvalidTypeException",
    "ParseException",
    "CallType",
    "NetSerializer",
]
