"""
NtpPacket.cs 翻译

RFC4330 SNTP包实现，用于网络时间协议通信

C#源文件: Utils/NtpPacket.cs
C#行数: ~424行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了RFC4330 SNTP协议，包括客户端请求、服务器响应、时间同步计算。
      使用网络字节序（大端），时间戳从1900年1月1日开始计算。
      来源: GuerrillaNtp项目 (MIT License)
"""

import struct
import datetime
from typing import Optional
from enum import IntEnum


class NtpLeapIndicator(IntEnum):
    """
    闰秒指示器

    C#定义: public enum NtpLeapIndicator
    C#源位置: NtpPacket.cs:384-405

    说明:
        从服务器发送的闰秒警告，指示客户端添加或删除闰秒
    """
    NO_WARNING = 0          # C#值: 0 - 无闰秒警告
    LAST_MINUTE_61 = 1      # C#值: 1 - 当天最后一分钟有61秒
    LAST_MINUTE_59 = 2      # C#值: 2 - 当天最后一分钟有59秒
    ALARM_CONDITION = 3     # C#值: 3 - 服务器时钟未同步，返回时间不可靠


class NtpMode(IntEnum):
    """
    SNTP包模式

    C#定义: public enum NtpMode
    C#源位置: NtpPacket.cs:411-422

    说明:
        描述SNTP包模式，即客户端或服务器
    """
    CLIENT = 3    # C#值: 3 - 客户端到服务器的SNTP包
    SERVER = 4    # C#值: 4 - 服务器到客户端的SNTP包


class NtpPacket:
    """
    NTP包

    C#定义: public class NtpPacket
    C#源位置: NtpPacket.cs:27-378

    属性:
        bytes: bytes - RFC4330编码的SNTP包（至少48字节）
        leap_indicator: NtpLeapIndicator - 闰秒指示器
        version_number: int - 协议版本号
        mode: NtpMode - 包模式（客户端/服务器）
        stratum: int - 服务器距离参考时钟的层数
        poll: int - 服务器首选轮询间隔
        precision: int - 服务器时钟精度
        root_delay: float - 到参考时钟的往返延迟
        root_dispersion: float - 服务器报告时间的估计误差
        reference_id: int - 时间源ID或Kiss-o'-Death代码
        reference_timestamp: Optional[datetime] - 服务器时钟最后设置或校正的时间
        origin_timestamp: Optional[datetime] - 客户端发送请求的时间
        receive_timestamp: Optional[datetime] - 服务器接收请求的时间
        transmit_timestamp: Optional[datetime] - 包发送的时间
        destination_timestamp: Optional[datetime] - 客户端接收响应SNTP包的时间
        round_trip_time: float - 到服务器的往返时间
        correction_offset: float - 应添加到本地时间以同步服务器时间的偏移量

    方法:
        from_server_response() - 从服务器响应创建NTP包
        validate_request() - 验证请求包
        validate_reply() - 验证响应包
    """

    # NTP纪元开始时间（1900年1月1日）
    EPOCH = datetime.datetime(1900, 1, 1, tzinfo=datetime.timezone.utc)

    def __init__(self, data: Optional[bytes] = None):
        """
        创建NTP包

        C#构造函数:
        - public NtpPacket()
        - internal NtpPacket(byte[] bytes)
        C#源位置: NtpPacket.cs:268-283

        参数:
            data: Optional[bytes] - 收到的数据（至少48字节）
                C#对应: byte[] bytes

        异常:
            ValueError: 如果数据长度小于48字节

        说明:
            如果不提供data，创建默认客户端请求包
            如果提供data，从接收的数据创建包
        """
        if data is None:
            # 创建默认请求包
            self._bytes = bytearray(48)
            self.mode = NtpMode.CLIENT
            self.version_number = 4
            self.transmit_timestamp = datetime.datetime.now(datetime.timezone.utc)
        else:
            # 从接收的数据创建包
            if len(data) < 48:
                raise ValueError("SNTP reply packet must be at least 48 bytes long.")
            self._bytes = bytearray(data)
            self._destination_timestamp = None

    @property
    def bytes(self) -> bytes:
        """
        获取RFC4330编码的SNTP包

        C#属性: public byte[] Bytes { get; }
        C#源位置: NtpPacket.cs:41

        返回:
            bytes: 包含RFC4330编码的SNTP包的字节数组（至少48字节）
                C#对应: byte[]

        说明:
            这是唯一的真实属性。除DestinationTimestamp外的所有其他属性
            都从或写入此字节数组
        """
        return bytes(self._bytes)

    @property
    def leap_indicator(self) -> NtpLeapIndicator:
        """
        获取闰秒指示器

        C#属性: public NtpLeapIndicator LeapIndicator
        C#源位置: NtpPacket.cs:54

        返回:
            NtpLeapIndicator: 闰秒警告（如果有）
                C#对应: NtpLeapIndicator

        说明:
            特殊值AlarmCondition表示服务器时钟未同步
            默认值为NoWarning
            只有服务器填充此属性，客户端可以查询此属性以获取可能的闰秒警告
        """
        return NtpLeapIndicator((self._bytes[0] & 0xC0) >> 6)

    @property
    def version_number(self) -> int:
        """
        获取或设置协议版本号

        C#属性: public int VersionNumber { get; private set; }
        C#源位置: NtpPacket.cs:66-70

        返回:
            int: SNTP协议版本。默认为4，这是撰写本文时的最新版本
                C#对应: int

        说明:
            在请求包中，客户端应将此属性保留为默认值4
            服务器通常以相同的协议版本回复
        """
        return (self._bytes[0] & 0x38) >> 3

    @version_number.setter
    def version_number(self, value: int) -> None:
        """设置协议版本号"""
        self._bytes[0] = (self._bytes[0] & ~0x38) | ((value & 0x07) << 3)

    @property
    def mode(self) -> NtpMode:
        """
        获取或设置SNTP包模式

        C#属性: public NtpMode Mode { get; private set; }
        C#源位置: NtpPacket.cs:79-83

        返回:
            NtpMode: SNTP包模式。新创建的包中默认为Client
                C#对应: NtpMode

        说明:
            服务器回复应将此属性设置为Server
        """
        return NtpMode(self._bytes[0] & 0x07)

    @mode.setter
    def mode(self, value: NtpMode) -> None:
        """设置SNTP包模式"""
        self._bytes[0] = (self._bytes[0] & ~0x07) | (value & 0x07)

    @property
    def stratum(self) -> int:
        """
        获取服务器距离参考时钟的距离

        C#属性: public int Stratum
        C#源位置: NtpPacket.cs:99

        返回:
            int: 距离参考时钟的距离
                C#对应: int

        说明:
            此属性仅在服务器回复包中设置
            直接连接到参考时钟硬件的服务器将此属性设置为1
            在NTP服务器层次结构中，每向下一跳，层数增加1
            特殊值0表示这是一个Kiss-o'-Death消息，kiss代码存储在ReferenceId中
        """
        return self._bytes[1]

    @property
    def poll(self) -> int:
        """
        获取服务器首选轮询间隔

        C#属性: public int Poll
        C#源位置: NtpPacket.cs:107

        返回:
            int: 以log2秒为单位的轮询间隔
                C#对应: int

        说明:
            例如，4代表16秒，17代表131,072秒
        """
        return self._bytes[2]

    @property
    def precision(self) -> int:
        """
        获取服务器时钟的精度

        C#属性: public int Precision
        C#源位置: NtpPacket.cs:115

        返回:
            int: 以log2秒为单位的时钟精度
                C#对应: int

        说明:
            例如，-20表示微秒精度
        """
        # 转换为有符号字节
        value = self._bytes[3]
        if value & 0x80:
            value = value - 256
        return value

    @property
    def root_delay(self) -> float:
        """
        获取服务器到参考时钟的总往返延迟

        C#属性: public TimeSpan RootDelay
        C#源位置: NtpPacket.cs:123

        返回:
            float: 到参考时钟的往返延迟。通常为小于1秒的正值
                C#对应: TimeSpan（秒）
        """
        value = struct.unpack('>I', self._bytes[4:8])[0]
        return value / (1 << 16)

    @property
    def root_dispersion(self) -> float:
        """
        获取服务器报告的时间的估计误差

        C#属性: public TimeSpan RootDispersion
        C#源位置: NtpPacket.cs:131

        返回:
            float: 服务器报告的时间的估计误差。通常为小于1秒的正值
                C#对应: TimeSpan（秒）
        """
        value = struct.unpack('>I', self._bytes[8:12])[0]
        return value / (1 << 16)

    @property
    def reference_id(self) -> int:
        """
        获取服务器使用的时间源的ID或服务器发送的Kiss-o'-Death代码

        C#属性: public uint ReferenceId
        C#源位置: NtpPacket.cs:153

        返回:
            int: 服务器时间源的ID或Kiss-o'-Death代码
                C#对应: uint

        说明:
            此属性的用途取决于Stratum属性的值
            Stratum 1服务器在此写入描述其使用的硬件时钟类型的特殊值之一
            Stratum 2及更低层的服务器将此属性设置为其上游服务器的IPv4地址
            如果上游服务器具有IPv6地址，则对该地址进行哈希，因为它不适合此属性
            当服务器将Stratum设置为特殊值0时，此属性包含所谓的kiss代码，
            指示客户端停止查询服务器
        """
        return struct.unpack('>I', self._bytes[12:16])[0]

    @property
    def reference_timestamp(self) -> Optional[datetime.datetime]:
        """
        获取或设置服务器时钟最后设置或校正的时间

        C#属性: public DateTime? ReferenceTimestamp { get; }
        C#源位置: NtpPacket.cs:165

        返回:
            Optional[datetime]: 服务器时钟最后设置或校正的时间，未指定时为None
                C#对应: DateTime?

        说明:
            此属性通常仅由服务器设置。它通常比服务器当前时间晚几分钟，
            所以不要使用此属性进行时间同步
        """
        return self._get_datetime64(16)

    @property
    def origin_timestamp(self) -> Optional[datetime.datetime]:
        """
        获取或设置客户端发送请求的时间

        C#属性: public DateTime? OriginTimestamp
        C#源位置: NtpPacket.cs:178

        返回:
            Optional[datetime]: 在请求包中为None
                在回复包中，是客户端发送请求的时间
                C#对应: DateTime?

        说明:
            服务器从接收到的请求包中的TransmitTimestamp复制此值
        """
        return self._get_datetime64(24)

    @property
    def receive_timestamp(self) -> Optional[datetime.datetime]:
        """
        获取或设置服务器接收请求的时间

        C#属性: public DateTime? ReceiveTimestamp
        C#源位置: NtpPacket.cs:189

        返回:
            Optional[datetime]: 在请求包中为None
                在回复包中，是服务器接收客户端请求的时间
                C#对应: DateTime?
        """
        return self._get_datetime64(32)

    @property
    def transmit_timestamp(self) -> Optional[datetime.datetime]:
        """
        获取或设置包发送的时间

        C#属性: public DateTime? TransmitTimestamp { get; private set; }
        C#源位置: NtpPacket.cs:203

        返回:
            Optional[datetime]: 包发送的时间。永远不应为None
                默认值为当前UTC时间
                C#对应: DateTime?

        说明:
            客户端和服务器都必须设置此属性
        """
        return self._get_datetime64(40)

    @transmit_timestamp.setter
    def transmit_timestamp(self, value: datetime.datetime) -> None:
        """设置发送时间戳"""
        self._set_datetime64(40, value)

    @property
    def destination_timestamp(self) -> Optional[datetime.datetime]:
        """
        获取或设置客户端接收响应SNTP包的时间

        C#属性: public DateTime? DestinationTimestamp { get; private set; }
        C#源位置: NtpPacket.cs:216

        返回:
            Optional[datetime]: 客户端接收响应SNTP包的时间。在请求包中为None
                C#对应: DateTime?

        说明:
            此属性不是协议的一部分，必须在接收到回复包时设置
        """
        return getattr(self, '_destination_timestamp', None)

    @destination_timestamp.setter
    def destination_timestamp(self, value: datetime.datetime) -> None:
        """设置目标时间戳"""
        self._destination_timestamp = value

    @property
    def round_trip_time(self) -> float:
        """
        获取到服务器的往返时间

        C#属性: public TimeSpan RoundTripTime
        C#源位置: NtpPacket.cs:230-237

        返回:
            float: 请求发送到服务器的时间加上回复发送回的时间
                从包中的时间戳计算为 (t1 - t0) + (t3 - t2)
                其中t0是OriginTimestamp，t1是ReceiveTimestamp
                t2是TransmitTimestamp，t3是DestinationTimestamp
                在请求包中此属性抛出异常
                C#对应: TimeSpan（秒）

        异常:
            ValueError: 如果时间戳不完整
        """
        self._check_timestamps()
        t0 = self.origin_timestamp
        t1 = self.receive_timestamp
        t2 = self.transmit_timestamp
        t3 = self.destination_timestamp

        if t0 is None or t1 is None or t2 is None or t3 is None:
            raise ValueError("Missing timestamps")

        delta1 = (t1 - t0).total_seconds()
        delta2 = (t3 - t2).total_seconds()
        return delta1 + delta2

    @property
    def correction_offset(self) -> float:
        """
        获取应添加到本地时间以同步服务器时间的偏移量

        C#属性: public TimeSpan CorrectionOffset
        C#源位置: NtpPacket.cs:251-258

        返回:
            float: 服务器和客户端之间的时间差异
                应将其添加到本地时间以获取服务器时间
                从包中的时间戳计算为 0.5 * ((t1 - t0) - (t3 - t2))
                在请求包中此属性抛出异常
                C#对应: TimeSpan（秒）

        异常:
            ValueError: 如果时间戳不完整
        """
        self._check_timestamps()
        t0 = self.origin_timestamp
        t1 = self.receive_timestamp
        t2 = self.transmit_timestamp
        t3 = self.destination_timestamp

        if t0 is None or t1 is None or t2 is None or t3 is None:
            raise ValueError("Missing timestamps")

        delta1 = (t1 - t0).total_seconds()
        delta2 = (t3 - t2).total_seconds()
        return 0.5 * (delta1 - delta2)

    @staticmethod
    def from_server_response(data: bytes, destination_timestamp: datetime.datetime) -> 'NtpPacket':
        """
        从从服务器接收的数据初始化包

        C#方法: public static NtpPacket FromServerResponse(byte[] bytes, DateTime destinationTimestamp)
        C#源位置: NtpPacket.cs:291-294

        参数:
            data: bytes - 从服务器接收的数据
                C#对应: byte[] bytes
            destination_timestamp: datetime - 客户端接收响应SNTP包的UTC时间
                C#对应: DateTime destinationTimestamp

        返回:
            NtpPacket: NTP包实例
                C#对应: NtpPacket
        """
        packet = NtpPacket(data)
        packet.destination_timestamp = destination_timestamp
        return packet

    def validate_request(self) -> None:
        """
        验证请求包

        C#方法: internal void ValidateRequest()
        C#源位置: NtpPacket.cs:296-304

        异常:
            ValueError: 如果这不是有效的请求SNTP包

        验证项:
            - 模式必须是Client
            - 必须指定协议版本
            - 必须设置TransmitTimestamp
        """
        if self.mode != NtpMode.CLIENT:
            raise ValueError("This is not a request SNTP packet.")
        if self.version_number == 0:
            raise ValueError("Protocol version of the request is not specified.")
        if self.transmit_timestamp is None:
            raise ValueError("TransmitTimestamp must be set in request packet.")

    def validate_reply(self) -> None:
        """
        验证响应包

        C#方法: internal void ValidateReply()
        C#源位置: NtpPacket.cs:306-317

        异常:
            ValueError: 如果这不是有效的响应SNTP包

        验证项:
            - 模式必须是Server
            - 必须指定协议版本
            - 不应收到Kiss-o'-Death包
            - 服务器时钟必须已同步
            - 所有时间戳必须存在
        """
        if self.mode != NtpMode.SERVER:
            raise ValueError("This is not a reply SNTP packet.")
        if self.version_number == 0:
            raise ValueError("Protocol version of the reply is not specified.")
        if self.stratum == 0:
            raise ValueError(f"Received Kiss-o'-Death SNTP packet with code 0x{self.reference_id:x}.")
        if self.leap_indicator == NtpLeapIndicator.ALARM_CONDITION:
            raise ValueError("SNTP server has unsynchronized clock.")
        self._check_timestamps()

    def _check_timestamps(self) -> None:
        """
        检查所有时间戳是否都存在

        C#方法: private void CheckTimestamps()
        C#源位置: NtpPacket.cs:319-329

        异常:
            ValueError: 如果任何时间戳缺失
        """
        if self.origin_timestamp is None:
            raise ValueError("Origin timestamp is missing.")
        if self.receive_timestamp is None:
            raise ValueError("Receive timestamp is missing.")
        if self.transmit_timestamp is None:
            raise ValueError("Transmit timestamp is missing.")
        if self.destination_timestamp is None:
            raise ValueError("Destination timestamp is missing.")

    def _get_datetime64(self, offset: int) -> Optional[datetime.datetime]:
        """
        从64位NTP时间戳获取datetime

        C#方法: private DateTime? GetDateTime64(int offset)
        C#源位置: NtpPacket.cs:331-337

        参数:
            offset: int - 字节数组中的偏移量
                C#对应: int offset

        返回:
            Optional[datetime]: datetime对象，如果字段为0则返回None
                C#对应: DateTime?
        """
        field = struct.unpack('>Q', self._bytes[offset:offset+8])[0]
        if field == 0:
            return None
        # NTP时间戳是自1900年以来的秒数（高32位）+ 分数（低32位）
        seconds = field >> 32
        fraction = field & 0xFFFFFFFF
        # 转换为100纳秒单位（.NET Tick）
        ticks = int(seconds * 10000000 + fraction * (10000000.0 / (1 << 32)))
        return self.EPOCH + datetime.timedelta(microseconds=ticks / 10)

    def _set_datetime64(self, offset: int, value: datetime.datetime) -> None:
        """
        将datetime设置为64位NTP时间戳

        C#方法: private void SetDateTime64(int offset, DateTime? value)
        C#源位置: NtpPacket.cs:339-342

        参数:
            offset: int - 字节数组中的偏移量
                C#对应: int offset
            value: datetime.datetime - 要设置的值
                C#对应: DateTime? value
        """
        if value is None:
            field = 0
        else:
            # 计算自1900年以来的时间差
            delta = value - self.EPOCH
            seconds = int(delta.total_seconds())
            # 计算分数部分
            fraction = int((delta.microseconds / 1000000.0) * (1 << 32))
            field = (seconds << 32) | (fraction & 0xFFFFFFFF)

        struct.pack_into('>Q', self._bytes, offset, field)


__all__ = [
    "NtpLeapIndicator",
    "NtpMode",
    "NtpPacket",
]
