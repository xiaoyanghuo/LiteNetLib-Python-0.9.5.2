"""
NetPacket.cs translation

Network packet structure and properties
"""

import struct
from typing import Optional
from ..constants import NetConstants
from ..utils.fast_bit_converter import FastBitConverter


class PacketProperty:
    """
    Packet property types

    C# enum: internal enum PacketProperty : byte
    """

    Unreliable = 0
    Channeled = 1
    Ack = 2
    Ping = 3
    Pong = 4
    ConnectRequest = 5
    ConnectAccept = 6
    Disconnect = 7
    UnconnectedMessage = 8
    MtuCheck = 9
    MtuOk = 10
    Broadcast = 11
    Merged = 12
    ShutdownOk = 13
    PeerNotFound = 14
    InvalidProtocol = 15
    NatMessage = 16
    Empty = 17

    _LAST_PROPERTY = Empty
    _HEADER_SIZES = None

    @classmethod
    def _initialize_header_sizes(cls):
        """Initialize header sizes for each packet type"""
        if cls._HEADER_SIZES is None:
            cls._HEADER_SIZES = {}
            for i in range(cls._LAST_PROPERTY + 1):
                prop = i
                if prop in [cls.Channeled, cls.Ack]:
                    size = NetConstants.ChanneledHeaderSize
                elif prop == cls.Ping:
                    size = NetConstants.HeaderSize + 2
                elif prop == cls.ConnectRequest:
                    size = 14  # NetConnectRequestPacket.HeaderSize (C# NetPacket.cs:171)
                elif prop == cls.ConnectAccept:
                    size = 11  # NetConnectAcceptPacket.Size (C# NetPacket.cs:231)
                elif prop == cls.Disconnect:
                    size = NetConstants.HeaderSize + 8
                elif prop == cls.Pong:
                    size = NetConstants.HeaderSize + 10
                else:
                    size = NetConstants.HeaderSize
                cls._HEADER_SIZES[prop] = size

    @classmethod
    def get_header_size(cls, property_value: int) -> int:
        """Get header size for packet property"""
        cls._initialize_header_sizes()
        return cls._HEADER_SIZES.get(property_value, NetConstants.HeaderSize)


class NetPacket:
    """
    Network packet

    C# class: internal sealed class NetPacket
    """

    def __init__(self, size: int, packet_property: Optional[int] = None):
        """
        Create packet

        C# constructors:
        - NetPacket(int size)
        - NetPacket(PacketProperty property, int size)
        """
        if packet_property is not None:
            size += PacketProperty.get_header_size(packet_property)
            self._raw_data = bytearray(size)
            self.packet_property = packet_property
        else:
            self._raw_data = bytearray(size)

        self._size = size
        self.user_data = None
        self.next = None  # Pool node

    @property
    def raw_data(self) -> bytearray:
        """Get raw packet data"""
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value: bytes):
        """Set raw packet data"""
        self._raw_data = bytearray(value)

    @property
    def size(self) -> int:
        """Get packet size"""
        return self._size

    @size.setter
    def size(self, value: int):
        """Set packet size"""
        self._size = value

    # Using packet_property instead of 'property' to avoid conflict with Python built-in
    @property
    def packet_property(self) -> int:
        """
        Get packet property

        C# property: public PacketProperty Property
        """
        return self._raw_data[0] & 0x1F

    @packet_property.setter
    def packet_property(self, value: int) -> None:
        """Set packet property"""
        self._raw_data[0] = (self._raw_data[0] & 0xE0) | (value & 0x1F)

    # Alias for C# compatibility (Property -> packet_property)
    @property
    def Property(self) -> int:
        return self._raw_data[0] & 0x1F

    @Property.setter
    def Property(self, value: int) -> None:
        self._raw_data[0] = (self._raw_data[0] & 0xE0) | (value & 0x1F)

    @property
    def connection_number(self) -> int:
        """
        Get connection number

        C# property: public byte ConnectionNumber
        """
        return (self._raw_data[0] & 0x60) >> 5

    @connection_number.setter
    def connection_number(self, value: int):
        """Set connection number"""
        self._raw_data[0] = (self._raw_data[0] & 0x9F) | ((value & 0x03) << 5)

    @property
    def sequence(self) -> int:
        """
        Get sequence number

        C# property: public ushort Sequence
        """
        return struct.unpack_from("<H", self._raw_data, 1)[0]

    @sequence.setter
    def sequence(self, value: int):
        """Set sequence number"""
        FastBitConverter.get_bytes_uint16(self._raw_data, 1, value)

    @property
    def is_fragmented(self) -> bool:
        """
        Check if packet is fragmented

        C# property: public bool IsFragmented
        """
        return (self._raw_data[0] & 0x80) != 0

    def mark_fragmented(self):
        """
        Mark packet as fragmented

        C# method: public void MarkFragmented()
        """
        self._raw_data[0] |= 0x80

    @property
    def channel_id(self) -> int:
        """
        Get channel ID

        C# property: public byte ChannelId
        """
        return self._raw_data[3]

    @channel_id.setter
    def channel_id(self, value: int):
        """Set channel ID"""
        self._raw_data[3] = value & 0xFF

    @property
    def fragment_id(self) -> int:
        """
        Get fragment ID

        C# property: public ushort FragmentId
        """
        return struct.unpack_from("<H", self._raw_data, 4)[0]

    @fragment_id.setter
    def fragment_id(self, value: int):
        """Set fragment ID"""
        FastBitConverter.get_bytes_uint16(self._raw_data, 4, value)

    @property
    def fragment_part(self) -> int:
        """
        Get fragment part

        C# property: public ushort FragmentPart
        """
        return struct.unpack_from("<H", self._raw_data, 6)[0]

    @fragment_part.setter
    def fragment_part(self, value: int):
        """Set fragment part"""
        FastBitConverter.get_bytes_uint16(self._raw_data, 6, value)

    @property
    def fragments_total(self) -> int:
        """
        Get total fragments

        C# property: public ushort FragmentsTotal
        """
        return struct.unpack_from("<H", self._raw_data, 8)[0]

    @fragments_total.setter
    def fragments_total(self, value: int):
        """Set total fragments"""
        FastBitConverter.get_bytes_uint16(self._raw_data, 8, value)

    def get_header_size(self) -> int:
        """
        Get header size for this packet

        C# method: public int GetHeaderSize()
        """
        return PacketProperty.get_header_size(self.packet_property)

    @staticmethod
    def get_header_size_for_property(property_value: int) -> int:
        """
        Get header size for a packet property

        C# method: public static int GetHeaderSize(PacketProperty property)
        """
        return PacketProperty.get_header_size(property_value)

    def verify(self) -> bool:
        """
        Verify packet integrity

        C# method: public bool Verify()
        """
        prop = self._raw_data[0] & 0x1F
        if prop > PacketProperty._LAST_PROPERTY:
            return False

        header_size = PacketProperty.get_header_size(prop)
        fragmented = (self._raw_data[0] & 0x80) != 0

        if self._size < header_size:
            return False

        if fragmented and self._size < header_size + NetConstants.FragmentHeaderSize:
            return False

        return True


__all__ = ["PacketProperty", "NetPacket"]
