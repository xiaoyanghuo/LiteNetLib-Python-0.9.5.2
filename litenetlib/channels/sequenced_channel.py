"""
Sequenced channel implementation (asyncio-compatible).

Implements sequenced and reliable sequenced delivery where only
the newest packet matters (older packets are dropped).

This version uses asyncio for Python compatibility while maintaining
exact C# protocol logic for interoperability.

Ported from: LiteNetLib/SequencedChannel.cs
"""

import asyncio
import time
from typing import Optional
from litenetlib.channels.base_channel import BaseChannel
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, DeliveryMethod, NetConstants
from litenetlib.utils.net_utils import NetUtils


class SequencedChannel(BaseChannel):
    """
    Sequenced channel with optional reliability (asyncio-compatible).

    Sequenced: Can drop packets, no duplicates, arrives in order.
    ReliableSequenced: Only the last packet is reliable, cannot be fragmented.

    Uses asyncio for Python compatibility while maintaining
    exact C# protocol logic for C# interoperability.

    C# Reference: internal sealed class SequencedChannel : BaseChannel
    """

    __slots__ = (
        '_local_sequence',
        '_remote_sequence',
        '_reliable',
        '_last_packet',
        '_ack_packet',
        '_must_send_ack',
        '_id',
        '_last_packet_send_time',
    )

    def __init__(self, peer, reliable: bool, channel_id: int):
        """
        Initialize sequenced channel.

        Args:
            peer: Associated peer
            reliable: True for ReliableSequenced, False for Sequenced
            channel_id: Channel ID (1 or 3)

        C# Equivalent: public SequencedChannel(LiteNetPeer peer, bool reliable, byte id)
        """
        super().__init__(peer)

        self._id = channel_id
        self._reliable = reliable

        # C#: _ackPacket = new NetPacket(PacketProperty.Ack, 0) {ChannelId = id};
        if self._reliable:
            self._ack_packet = NetPacket(PacketProperty.ACK, 0)
            self._ack_packet.channel_id = channel_id
        else:
            self._ack_packet = None

        # Initialize sequences
        # C#: _localSequence = 0; _remoteSequence = 0;
        self._local_sequence = 0
        self._remote_sequence = 0

        # Last packet (for reliable sequenced)
        self._last_packet: Optional[NetPacket] = None
        self._last_packet_send_time: float = 0.0

        # ACK flag
        self._must_send_ack = False

    def send_next_packets(self) -> bool:
        """
        Send next packets from queue.

        Returns:
            True if more packets to send, False otherwise

        C# Equivalent: public override bool SendNextPackets()
        """
        # C#: if (_reliable && OutgoingQueue.Count == 0)
        if self._reliable and self._outgoing_queue.empty():
            # Resend last packet if needed (reliable sequenced)
            # C#: long packetHoldTime = currentTime - _lastPacketSendTime;
            #     if (packetHoldTime >= Peer.ResendDelay * TimeSpan.TicksPerMillisecond)
            current_time = time.time()
            packet_hold_time = current_time - self._last_packet_send_time
            resend_delay = self._peer.resend_delay / 1000.0  # Convert to seconds

            if packet_hold_time >= resend_delay:
                packet = self._last_packet
                if packet is not None:
                    # C#: _lastPacketSendTime = currentTime; Peer.SendUserData(packet);
                    self._last_packet_send_time = current_time
                    if hasattr(self._peer, 'send_user_data'):
                        self._peer.send_user_data(packet)
        else:
            # Send new packets
            # C#: while (OutgoingQueue.Count > 0)
            while not self._outgoing_queue.empty():
                try:
                    # C#: NetPacket packet = OutgoingQueue.Dequeue();
                    packet = self._outgoing_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                # Advance sequence and set packet properties
                # C#: _localSequence = (_localSequence + 1) % NetConstants.MaxSequence;
                #     packet.Sequence = (ushort)_localSequence;
                #     packet.ChannelId = _id;
                self._local_sequence = (self._local_sequence + 1) % NetConstants.MAX_SEQUENCE
                packet.sequence = self._local_sequence & 0xFFFF
                packet.channel_id = self._id

                # Send packet
                # C#: Peer.SendUserData(packet);
                if hasattr(self._peer, 'send_user_data'):
                    self._peer.send_user_data(packet)

                # Handle reliable sequenced (keep last packet)
                # C#: if (_reliable && OutgoingQueue.Count == 0)
                #     {
                #         _lastPacketSendTime = DateTime.UtcNow.Ticks;
                #         _lastPacket = packet;
                #     }
                #     else
                #     {
                #         Peer.NetManager.PoolRecycle(packet);
                #     }
                if self._reliable and self._outgoing_queue.empty():
                    self._last_packet_send_time = time.time()
                    self._last_packet = packet
                else:
                    # Packet sent, will be recycled by peer
                    pass

        # Send ACK if needed
        # C#: if (_reliable && _mustSendAck)
        #     {
        #         _mustSendAck = false;
        #         _ackPacket.Sequence = _remoteSequence;
        #         Peer.SendUserData(_ackPacket);
        #     }
        if self._reliable and self._must_send_ack:
            self._must_send_ack = False
            self._ack_packet.sequence = self._remote_sequence & 0xFFFF
            if hasattr(self._peer, 'send_user_data'):
                # Send ACK packet (copy it since it's reused)
                ack_copy = NetPacket.from_bytes(self._ack_packet.get_bytes())
                self._peer.send_user_data(ack_copy)

        # C#: return _lastPacket != null;
        return self._last_packet is not None

    def process_packet(self, packet: NetPacket) -> bool:
        """
        Process incoming packet.

        Args:
            packet: Received packet

        Returns:
            True if packet was processed successfully

        C# Equivalent: public override bool ProcessPacket(NetPacket packet)
        """
        # C#: if (packet.IsFragmented) return false;
        if packet.is_fragmented:
            return False

        # Handle ACK packet
        # C#: if (packet.Property == PacketProperty.Ack)
        #     {
        #         if (_reliable && _lastPacket != null && packet.Sequence == _lastPacket.Sequence)
        #             _lastPacket = null;
        #         return false;
        #     }
        if packet.packet_property == PacketProperty.ACK:
            if self._reliable and self._last_packet is not None and packet.sequence == self._last_packet.sequence:
                self._last_packet = None
            return False

        # Calculate relative sequence
        # C#: int relative = NetUtils.RelativeSequenceNumber(packet.Sequence, _remoteSequence);
        relative = NetUtils.relative_sequence_number(packet.sequence, self._remote_sequence)
        packet_processed = False

        # C#: if (packet.Sequence < NetConstants.MaxSequence && relative > 0)
        if packet.sequence < NetConstants.MAX_SEQUENCE and relative > 0:
            # Newer packet received - drop older packets
            # C#: if (Peer.NetManager.EnableStatistics)
            #     {
            #         Peer.Statistics.AddPacketLoss(relative - 1);
            #         Peer.NetManager.Statistics.AddPacketLoss(relative - 1);
            #     }
            # _remoteSequence = packet.Sequence;

            # Note: Statistics not implemented in Python yet
            self._remote_sequence = packet.sequence

            # Deliver packet to peer
            # C#: Peer.NetManager.CreateReceiveEvent(
            #     packet,
            #     _reliable ? DeliveryMethod.ReliableSequenced : DeliveryMethod.Sequenced,
            #     (byte)(packet.ChannelId / NetConstants.ChannelTypeCount),
            #     NetConstants.ChanneledHeaderSize,
            #     Peer);

            if hasattr(self._peer, 'add_reliable_packet'):
                delivery_method = DeliveryMethod.RELIABLE_SEQUENCED if self._reliable else DeliveryMethod.SEQUENCED
                self._peer.add_reliable_packet(delivery_method, packet)

            packet_processed = True

        # Send ACK if reliable
        # C#: if (_reliable)
        #     {
        #         _mustSendAck = true;
        #         AddToPeerChannelSendQueue();
        #     }
        if self._reliable:
            self._must_send_ack = True
            self._add_to_peer_channel_send_queue()

        return packet_processed

    def __repr__(self) -> str:
        reliable_str = "reliable" if self._reliable else "unreliable"
        return (f"SequencedChannel(id={self._id}, {reliable_str}, "
                f"local_seq={self._local_sequence}, remote_seq={self._remote_sequence})")
