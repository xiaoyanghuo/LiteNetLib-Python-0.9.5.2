"""
NetConstants.cs translation

Network constants. Can be tuned from sources for your purposes.
"""

from enum import IntEnum


class DeliveryMethod(IntEnum):
    """
    Sending method type

    C# enum: DeliveryMethod : byte
    """

    # Unreliable. Packets can be dropped, can be duplicated, can arrive without order.
    Unreliable = 4

    # Reliable. Packets won't be dropped, won't be duplicated, can arrive without order.
    ReliableUnordered = 0

    # Unreliable. Packets can be dropped, won't be duplicated, will arrive in order.
    Sequenced = 1

    # Reliable and ordered. Packets won't be dropped, won't be duplicated, will arrive in order.
    ReliableOrdered = 2

    # Reliable only last packet. Packets can be dropped (except the last one),
    # won't be duplicated, will arrive in order. Cannot be fragmented
    ReliableSequenced = 3


class NetConstants:
    """
    Network constants

    C# class: public static class NetConstants
    """

    # can be tuned
    DefaultWindowSize = 64
    SocketBufferSize = 1024 * 1024  # 1mb
    SocketTTL = 255

    HeaderSize = 1
    ChanneledHeaderSize = 4
    FragmentHeaderSize = 6
    FragmentedHeaderTotalSize = ChanneledHeaderSize + FragmentHeaderSize
    MaxSequence = 32768
    HalfMaxSequence = MaxSequence // 2

    # protocol
    _protocol_id = 11
    MaxUdpHeaderSize = 68

    _possible_mtu = [
        576 - MaxUdpHeaderSize,  # minimal (RFC 1191)
        1024,  # most games standard
        1232 - MaxUdpHeaderSize,
        1460 - MaxUdpHeaderSize,  # google cloud
        1472 - MaxUdpHeaderSize,  # VPN
        1492 - MaxUdpHeaderSize,  # Ethernet with LLC and SNAP, PPPoE (RFC 1042)
        1500 - MaxUdpHeaderSize,  # Ethernet II (RFC 1191)
    ]

    MaxPacketSize = _possible_mtu[-1]

    # peer specific
    MaxConnectionNumber = 4

    PacketPoolSize = 1000

    @classmethod
    def get_possible_mtu(cls) -> list:
        """Get list of possible MTU values"""
        return cls._possible_mtu.copy()

    @classmethod
    def get_protocol_id(cls) -> int:
        """Get protocol ID"""
        return cls._protocol_id


# PacketProperty enum (will be needed for NetPacket)
class PacketProperty(IntEnum):
    """
    Packet types

    C# enum: PacketProperty : byte (defined in NetPacket.cs)
    """

    UnconnectedMessage = 0
    Ack = 1
    Ping = 2
    Pong = 3
    ConnectRequest = 4
    ConnectAccept = 5
    Disconnect = 6
    UnconnectedData = 7
    MtuOk = 8
    MtuError = 9
    MtuRequest = 10
    NatIntroduction = 11
    NatPunchRequest = 12
    NatPunchReply = 13
    Broadcast = 14
    MtuSuccess = 15
    ShutdownOk = 16
    PeerNotFound = 17
    InvalidProtocol = 18
    NewHost = 19
    DiscoveryRequest = 20
    DiscoveryResponse = 21
    TrafficReset = 22


__all__ = ["DeliveryMethod", "NetConstants", "PacketProperty"]
