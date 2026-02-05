"""
NetPacketProcessor.cs 翻译

类型安全的包处理器和分发器，使用FNV-1a哈希进行类型识别

C#源文件: Utils/NetPacketProcessor.cs
C#行数: ~289行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括FNV-1a 64位哈希、订阅机制、可重用包实例等。
      使用字典存储回调函数，支持泛型类型的订阅/取消订阅。
"""

from typing import Type, TypeVar, Generic, Dict, Callable, Any, Optional
from .net_data_reader import NetDataReader
from .net_data_writer import NetDataWriter
from .net_serializer import NetSerializer, InvalidTypeException
from .serializable import INetSerializable


class ParseException(Exception):
    """
    解析异常

    C#定义: (在NetSerializer.cs中定义)
    C#源位置: NetSerializer.cs:15-18
    """
    pass


T = TypeVar('T')
TUserData = TypeVar('TUserData')


class _HashCache:
    """
    类型哈希缓存

    C#定义: private static class HashCache<T>
    C#源位置: NetPacketProcessor.cs:9-25

    说明:
        使用FNV-1a 64位哈希算法为类型生成唯一标识符
        哈希值在首次访问时计算并缓存
    """

    _cache: Dict[Type, int] = {}

    @classmethod
    def get_hash(cls, type_class: Type) -> int:
        """
        获取类型的哈希值

        C#方法: public static readonly ulong Id
        C#源位置: NetPacketProcessor.cs:11

        参数:
            type_class: Type - 类型
                C#对应: typeof(T)

        返回:
            int: FNV-1a 64位哈希值
                C#对应: ulong Id

        算法:
            FNV-1a 64位哈希:
            - offset basis: 14695981039346656037 (0xcbf29ce484222325)
            - prime: 1099511628211 (0x100000001b3)

            hash = offset
            for each byte in type_name:
                hash ^= byte
                hash *= prime
        """
        if type_class not in cls._cache:
            # FNV-1a 64 bit hash
            hash = 14695981039346656037  # offset basis (0xcbf29ce484222325)
            type_name = str(type_class)
            for char in type_name:
                hash ^= ord(char)
                hash *= 1099511628211  # prime (0x100000001b3)
                # 限制在64位
                hash &= 0xFFFFFFFFFFFFFFFF
            cls._cache[type_class] = hash

        return cls._cache[type_class]


class NetPacketProcessor:
    """
    网络包处理器

    C#定义: public class NetPacketProcessor
    C#源位置: NetPacketProcessor.cs:7-288

    属性:
        无公共属性

    方法:
        register_nested_type() - 注册嵌套类型
        read_all_packets() - 读取所有包
        read_packet() - 读取单个包
        write() - 写入包
        subscribe() - 订阅包类型
        subscribe_reusable() - 订阅可重用包
        subscribe_net_serializable() - 订阅INetSerializable包
        remove_subscription() - 移除订阅
    """

    def __init__(self, max_string_length: int = 0):
        """
        创建网络包处理器

        C#构造函数: public NetPacketProcessor(), public NetPacketProcessor(int maxStringLength)
        C#源位置: NetPacketProcessor.cs:31-39

        参数:
            max_string_length: int - 最大字符串长度（0表示无限制）
                C#对应: int maxStringLength

        说明:
            创建内部的NetSerializer实例用于序列化/反序列化
        """
        self._net_serializer = NetSerializer(max_string_length)
        self._callbacks: Dict[int, Callable[[NetDataReader, Any], None]] = {}

    def _get_hash(self, type_class: Type[T]) -> int:
        """
        获取类型的哈希值

        C#方法: protected virtual ulong GetHash<T>()
        C#源位置: NetPacketProcessor.cs:41-44

        参数:
            type_class: Type - 类型
                C#对应: T

        返回:
            int: 类型的FNV-1a哈希值
                C#对应: ulong
        """
        return _HashCache.get_hash(type_class)

    def _get_callback_from_data(self, reader: NetDataReader) -> Callable[[NetDataReader, Any], None]:
        """
        从数据中获取回调函数

        C#方法: protected virtual SubscribeDelegate GetCallbackFromData(NetDataReader reader)
        C#源位置: NetPacketProcessor.cs:46-54

        参数:
            reader: NetDataReader - 数据读取器
                C#对应: NetDataReader reader

        返回:
            Callable: 回调函数
                C#对应: SubscribeDelegate

        异常:
            ParseException: 如果包类型未定义
        """
        hash_value = reader.get_ulong()
        if hash_value not in self._callbacks:
            raise ParseException("Undefined packet in NetDataReader")
        return self._callbacks[hash_value]

    def _write_hash(self, writer: NetDataWriter, type_class: Type[T]) -> None:
        """
        写入类型哈希

        C#方法: protected virtual void WriteHash<T>(NetDataWriter writer)
        C#源位置: NetPacketProcessor.cs:56-59

        参数:
            writer: NetDataWriter - 数据写入器
                C#对应: NetDataWriter writer
            type_class: Type - 类型
                C#对应: T
        """
        writer.put_ulong(self._get_hash(type_class))

    def register_nested_type(self, cls: Type, constructor: Optional[Callable] = None,
                            writer: Optional[Callable] = None, reader: Optional[Callable] = None) -> None:
        """
        注册嵌套属性类型

        C#方法:
        - public void RegisterNestedType<T>() where T : struct, INetSerializable
        - public void RegisterNestedType<T>(Func<T> constructor) where T : class, INetSerializable
        - public void RegisterNestedType<T>(Action<NetDataWriter, T> writer, Func<NetDataReader, T> reader)
        C#源位置: NetPacketProcessor.cs:65-87

        参数:
            cls: Type - 类型
                C#对应: T
            constructor: Optional[Callable] - 构造函数
                C#对应: Func<T> constructor
            writer: Optional[Callable] - 自定义写入器
                C#对应: Action<NetDataWriter, T> writeDelegate
            reader: Optional[Callable] - 自定义读取器
                C#对应: Func<NetDataReader, T> readDelegate

        说明:
            委托给内部的NetSerializer实例
        """
        self._net_serializer.register_nested_type(cls, constructor, writer, reader)

    def read_all_packets(self, reader: NetDataReader, user_data: Any = None) -> None:
        """
        读取所有可用的包

        C#方法:
        - public void ReadAllPackets(NetDataReader reader)
        - public void ReadAllPackets(NetDataReader reader, object userData)
        C#源位置: NetPacketProcessor.cs:93-109

        参数:
            reader: NetDataReader - 包含包数据的读取器
                C#对应: NetDataReader reader
            user_data: Any - 传递给OnReceivedEvent的参数
                C#对应: object userData

        异常:
            ParseException: 包格式错误
        """
        while reader.available_bytes > 0:
            self.read_packet(reader, user_data)

    def read_packet(self, reader: NetDataReader, user_data: Any = None) -> None:
        """
        读取单个包

        C#方法:
        - public void ReadPacket(NetDataReader reader)
        - public void ReadPacket(NetDataReader reader, object userData)
        C#源位置: NetPacketProcessor.cs:116-119, 143-146

        参数:
            reader: NetDataReader - 包含包的读取器
                C#对应: NetDataReader reader
            user_data: Any - 传递给OnReceivedEvent的参数
                C#对应: object userData

        异常:
            ParseException: 包格式错误
        """
        callback = self._get_callback_from_data(reader)
        callback(reader, user_data)

    def write(self, writer: NetDataWriter, packet: T) -> None:
        """
        写入包

        C#方法: public void Write<T>(NetDataWriter writer, T packet) where T : class, new()
        C#源位置: NetPacketProcessor.cs:121-129

        参数:
            writer: NetDataWriter - 数据写入器
                C#对应: NetDataWriter writer
            packet: T - 要写入的包
                C#对应: T packet

        说明:
            首先写入类型哈希，然后序列化包数据
        """
        packet_type = type(packet)
        self._write_hash(writer, packet_type)
        self._net_serializer.serialize(writer, packet)

    def write_net_serializable(self, writer: NetDataWriter, packet: INetSerializable) -> None:
        """
        写入INetSerializable包

        C#方法: public void WriteNetSerializable<T>(NetDataWriter writer, ref T packet) where T : INetSerializable
        C#源位置: NetPacketProcessor.cs:131-135

        参数:
            writer: NetDataWriter - 数据写入器
                C#对应: NetDataWriter writer
            packet: INetSerializable - 要写入的包
                C#对应: ref T packet

        说明:
            首先写入类型哈希，然后调用包的Serialize方法
        """
        packet_type = type(packet)
        self._write_hash(writer, packet_type)
        packet.serialize(writer)

    def subscribe(self, cls: Type[T], on_receive: Callable[[T], None],
                 constructor: Optional[Callable[[], T]] = None,
                 user_data_type: Optional[Type] = None) -> None:
        """
        订阅包接收事件

        C#方法:
        - public void Subscribe<T>(Action<T> onReceive, Func<T> packetConstructor)
        - public void Subscribe<T, TUserData>(Action<T, TUserData> onReceive, Func<T> packetConstructor)
        C#源位置: NetPacketProcessor.cs:154-167, 175-188

        参数:
            cls: Type[T] - 包类型
                C#对应: T
            on_receive: Callable[[T], None] - 接收回调
                C#对应: Action<T> onReceive
            constructor: Optional[Callable[[], T]] - 包构造函数
                C#对应: Func<T> packetConstructor
            user_data_type: Optional[Type] - 用户数据类型（如果有）
                C#对应: TUserData

        异常:
            InvalidTypeException: 类的字段不支持或没有字段
        """
        self._net_serializer.register(cls)

        if user_data_type is None:
            # 无用户数据版本
            def callback(reader: NetDataReader, user_data: Any) -> None:
                if constructor is None:
                    # 使用默认构造函数
                    reference = cls()
                else:
                    reference = constructor()
                self._net_serializer.deserialize(reader, cls, reference)
                on_receive(reference)
        else:
            # 带用户数据版本
            def callback(reader: NetDataReader, user_data: Any) -> None:
                if constructor is None:
                    reference = cls()
                else:
                    reference = constructor()
                self._net_serializer.deserialize(reader, cls, reference)
                on_receive(reference, user_data)

        self._callbacks[self._get_hash(cls)] = callback

    def subscribe_reusable(self, cls: Type[T], on_receive: Callable[[T], None],
                          user_data_type: Optional[Type] = None) -> None:
        """
        订阅包接收事件（可重用实例，减少垃圾回收）

        C#方法:
        - public void SubscribeReusable<T>(Action<T> onReceive) where T : class, new()
        - public void SubscribeReusable<T, TUserData>(Action<T, TUserData> onReceive) where T : class, new()
        C#源位置: NetPacketProcessor.cs:196-209, 217-230

        参数:
            cls: Type[T] - 包类型
                C#对应: T
            on_receive: Callable[[T], None] - 接收回调
                C#对应: Action<T> onReceive
            user_data_type: Optional[Type] - 用户数据类型（如果有）
                C#对应: TUserData

        异常:
            InvalidTypeException: 类的字段不支持或没有字段

        说明:
            此方法将覆盖最后接收的包类实例（减少垃圾回收）
            每次接收到新数据时，会重用同一个实例
        """
        self._net_serializer.register(cls)
        reference = cls()  # 创建可重用实例

        if user_data_type is None:
            # 无用户数据版本
            def callback(reader: NetDataReader, user_data: Any) -> None:
                self._net_serializer.deserialize(reader, cls, reference)
                on_receive(reference)
        else:
            # 带用户数据版本
            def callback(reader: NetDataReader, user_data: Any) -> None:
                self._net_serializer.deserialize(reader, cls, reference)
                on_receive(reference, user_data)

        self._callbacks[self._get_hash(cls)] = callback

    def subscribe_net_serializable(self, cls: Type[T], on_receive: Callable[[T], None],
                                  constructor: Optional[Callable[[], T]] = None,
                                  user_data_type: Optional[Type] = None) -> None:
        """
        订阅INetSerializable包接收事件

        C#方法:
        - public void SubscribeNetSerializable<T>(Action<T> onReceive, Func<T> packetConstructor)
        - public void SubscribeNetSerializable<T, TUserData>(Action<T, TUserData> onReceive, Func<T> packetConstructor)
        - public void SubscribeNetSerializable<T>(Action<T> onReceive) where T : INetSerializable, new()
        - public void SubscribeNetSerializable<T, TUserData>(Action<T, TUserData> onReceive) where T : INetSerializable, new()
        C#源位置: NetPacketProcessor.cs:232-276

        参数:
            cls: Type[T] - INetSerializable包类型
                C#对应: T
            on_receive: Callable[[T], None] - 接收回调
                C#对应: Action<T> onReceive
            constructor: Optional[Callable[[], T]] - 包构造函数
                C#对应: Func<T> packetConstructor
            user_data_type: Optional[Type] - 用户数据类型（如果有）
                C#对应: TUserData

        说明:
            专门用于处理实现了INetSerializable接口的包
            如果不提供constructor且没有new()约束，则必须使用可重用版本
        """
        if constructor is None and user_data_type is None:
            # 可重用版本
            reference = cls()

            def callback(reader: NetDataReader, user_data: Any) -> None:
                reference.deserialize(reader)
                on_receive(reference)
        elif constructor is None:
            # 可重用版本（带用户数据）
            reference = cls()

            def callback(reader: NetDataReader, user_data: Any) -> None:
                reference.deserialize(reader)
                on_receive(reference, user_data)
        elif user_data_type is None:
            # 带构造函数版本（无用户数据）
            def callback(reader: NetDataReader, user_data: Any) -> None:
                pkt = constructor()
                pkt.deserialize(reader)
                on_receive(pkt)
        else:
            # 带构造函数版本（带用户数据）
            def callback(reader: NetDataReader, user_data: Any) -> None:
                pkt = constructor()
                pkt.deserialize(reader)
                on_receive(pkt, user_data)

        self._callbacks[self._get_hash(cls)] = callback

    def remove_subscription(self, cls: Type[T]) -> bool:
        """
        按类型移除订阅

        C#方法: public bool RemoveSubscription<T>()
        C#源位置: NetPacketProcessor.cs:283-286

        参数:
            cls: Type[T] - 包类型
                C#对应: T

        返回:
            bool: 如果移除成功返回true，否则返回false
                C#对应: bool
        """
        hash_value = self._get_hash(cls)
        if hash_value in self._callbacks:
            del self._callbacks[hash_value]
            return True
        return False


__all__ = [
    "ParseException",
    "NetPacketProcessor",
]
