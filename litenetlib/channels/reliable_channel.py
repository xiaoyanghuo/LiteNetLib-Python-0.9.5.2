"""
Reliable channel implementation with ACK and retransmission (asyncio-compatible).

Implements reliable ordered/unordered delivery with sequence numbers,
ACK packets, and automatic retransmission.

This version uses asyncio for Python compatibility while maintaining
exact C# protocol logic for interoperability.

Ported from: LiteNetLib/ReliableChannel.cs
"""

import asyncio
import time
from typing import Optional
from litenetlib.channels.base_channel import BaseChannel
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, DeliveryMethod, NetConstants
from litenetlib.utils.net_utils import NetUtils

# Constants matching C#
BITS_IN_BYTE = 8


class PendingPacket:
    """
    A packet awaiting acknowledgment.

    Matches C# PendingPacket struct protocol logic.
    """

    __slots__ = ('_packet', '_timestamp', '_is_sent')

    def __init__(self):
        """Create empty pending packet."""
        self._packet: Optional[NetPacket] = None
        self._timestamp: float = 0.0
        self._is_sent: bool = False

    def __repr__(self) -> str:
        """String representation."""
        if self._packet is None:
            return "Empty"
        return str(self._packet.sequence)

    def init(self, packet: NetPacket) -> None:
        """Initialize with a packet."""
        self._packet = packet
        self._is_sent = False

    def try_send(self, current_time: float, peer) -> bool:
        """
        Try to send packet if resend delay has passed.

        Args:
            current_time: Current time in seconds
            peer: Peer instance for sending

        Returns:
            True if packet exists (sent or waiting), False if empty

        C# Logic: check resendDelay, update timestamp, send packet
        """
        if self._packet is None:
            return False

        if self._is_sent:
            # C#: double resendDelay = peer.ResendDelay * TimeSpan.TicksPerMillisecond
            # We use milliseconds directly
            resend_delay = peer.resend_delay / 1000.0  # Convert to seconds
            packet_hold_time = current_time - self._timestamp

            if packet_hold_time < resend_delay:
                return True  # Still waiting for resend delay

        # C#: _timeStamp = currentTime; _isSent = true; peer.SendUserData(_packet)
        self._timestamp = current_time
        self._is_sent = True

        if hasattr(peer, 'send_user_data'):
            peer.send_user_data(self._packet)

        return True

    def clear(self, peer) -> bool:
        """
        Clear packet and return to pool.

        Args:
            peer: Peer instance for recycling

        Returns:
            True if packet was cleared, False if already empty
        """
        if self._packet is not None:
            # C#: peer.RecycleAndDeliver(_packet)
            if hasattr(peer, 'recycle_and_deliver'):
                peer.recycle_and_deliver(self._packet)
            self._packet = None
            return True
        return False


class ReliableChannel(BaseChannel):
    """
    Reliable channel with ACK/retransmission (asyncio-compatible).

    Supports both ordered and unordered reliable delivery.
    Implements sliding window protocol with selective ACK.

    Uses asyncio for Python compatibility while maintaining
    exact C# protocol logic for C# interoperability.

    C# Reference: internal sealed class ReliableChannel : BaseChannel
    """

    __slots__ = (
        '_outgoing_acks',
        '_pending_packets',
        '_received_packets',
        '_early_received',
        '_local_sequence',
        '_remote_sequence',
        '_local_window_start',
        '_remote_window_start',
        '_must_send_acks',
        '_delivery_method',
        '_ordered',
        '_window_size',
        '_id',
    )

    def __init__(self, peer, ordered: bool, channel_id: int):
        """
        Initialize reliable channel.

        Args:
            peer: Associated peer
            ordered: True for ordered delivery, False for unordered
            channel_id: Channel ID (0-3)

        C# Equivalent: public ReliableChannel(LiteNetPeer peer, bool ordered, byte id)
        """
        super().__init__(peer)

        self._id = channel_id
        self._window_size = NetConstants.DEFAULT_WINDOW_SIZE
        self._ordered = ordered

        # Create pending packets array
        # C#: _pendingPackets = new PendingPacket[_windowSize];
        self._pending_packets = [PendingPacket() for _ in range(self._window_size)]

        # Delivery method
        # C#: _deliveryMethod = DeliveryMethod.ReliableOrdered : DeliveryMethod.ReliableUnordered
        if ordered:
            self._delivery_method = DeliveryMethod.RELIABLE_ORDERED
            # C#: _receivedPackets = new NetPacket[_windowSize]
            self._received_packets = [None] * self._window_size
            self._early_received = None
        else:
            self._delivery_method = DeliveryMethod.RELIABLE_UNORDERED
            self._received_packets = None
            # C#: _earlyReceived = new bool[_windowSize]
            self._early_received = [False] * self._window_size

        # Initialize sequence numbers
        # C#: _localWindowStart = 0; _localSeqence = 0; _remoteSequence = 0; _remoteWindowStart = 0;
        self._local_window_start = 0
        self._local_sequence = 0
        self._remote_sequence = 0
        self._remote_window_start = 0

        # Create ACK packet
        # C#: _outgoingAcks = new NetPacket(PacketProperty.Ack, (_windowSize - 1) / BitsInByte + 2)
        ack_data_size = (self._window_size - 1) // BITS_IN_BYTE + 2
        self._outgoing_acks = NetPacket(PacketProperty.ACK, ack_data_size)
        self._outgoing_acks.channel_id = channel_id

        self._must_send_acks = False

    def send_next_packets(self) -> bool:
        """
        Send next packets from queue and handle retransmissions.

        Returns:
            True if more packets to send, False otherwise

        C# Equivalent: public override bool SendNextPackets()
        """
        # Send ACKs if needed
        # C#: if (_mustSendAcks) { ... }
        if self._must_send_acks:
            self._must_send_acks = False
            # C#: lock(_outgoingAcks) Peer.SendUserData(_outgoingAcks)
            if hasattr(self._peer, 'send_user_data'):
                # Send ACK packet (copy it since it's reused)
                ack_copy = NetPacket.from_bytes(self._outgoing_acks.get_bytes())
                self._peer.send_user_data(ack_copy)

        # Get current time in seconds
        current_time = time.time()
        has_pending_packets = False

        # Get packets from queue and add to pending
        # C#: lock (OutgoingQueue) { while (OutgoingQueue.Count > 0) ... }
        while not self._outgoing_queue.empty():
            # C#: int relate = NetUtils.RelativeSequenceNumber(_localSeqence, _localWindowStart)
            relate = NetUtils.relative_sequence_number(self._local_sequence, self._local_window_start)
            if relate >= self._window_size:
                break  # Window full

            # C#: var netPacket = OutgoingQueue.Dequeue()
            try:
                net_packet = self._outgoing_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            # Set sequence and channel
            # C#: netPacket.Sequence = (ushort) _localSeqence; netPacket.ChannelId = _id;
            net_packet.sequence = self._local_sequence & 0xFFFF
            net_packet.channel_id = self._id

            # Add to pending
            # C#: _pendingPackets[_localSeqence % _windowSize].Init(netPacket)
            self._pending_packets[self._local_sequence % self._window_size].init(net_packet)

            # Advance local sequence
            # C#: _localSeqence = (_localSeqence + 1) % NetConstants.MaxSequence
            self._local_sequence = (self._local_sequence + 1) % NetConstants.MAX_SEQUENCE

        # Send pending packets
        # C#: for (int pendingSeq = _localWindowStart; pendingSeq != _localSeqence; pendingSeq = ...)
        pending_seq = self._local_window_start
        while pending_seq != self._local_sequence:
            # C#: _pendingPackets[pendingSeq % _windowSize].TrySend(currentTime, Peer)
            if self._pending_packets[pending_seq % self._window_size].try_send(current_time, self._peer):
                has_pending_packets = True

            pending_seq = (pending_seq + 1) % NetConstants.MAX_SEQUENCE

        # C#: return hasPendingPackets || _mustSendAcks || OutgoingQueue.Count > 0
        return has_pending_packets or self._must_send_acks or not self._outgoing_queue.empty()

    def process_packet(self, packet: NetPacket) -> bool:
        """
        Process incoming packet.

        Args:
            packet: Received packet

        Returns:
            True if packet was processed successfully

        C# Equivalent: public override bool ProcessPacket(NetPacket packet)
        """
        # Check if ACK packet
        # C#: if (packet.Property == PacketProperty.Ack) { ProcessAck(packet); return false; }
        if packet.packet_property == PacketProperty.ACK:
            self._process_ack(packet)
            return False

        seq = packet.sequence

        # Validate sequence
        # C#: if (seq >= NetConstants.MaxSequence) { ... }
        if seq >= NetConstants.MAX_SEQUENCE:
            return False

        # C#: int relate = NetUtils.RelativeSequenceNumber(seq, _remoteWindowStart)
        #     int relateSeq = NetUtils.RelativeSequenceNumber(seq, _remoteSequence)
        relate = NetUtils.relative_sequence_number(seq, self._remote_window_start)
        relate_seq = NetUtils.relative_sequence_number(seq, self._remote_sequence)

        # C#: if (relateSeq > _windowSize) { ... }
        if relate_seq > self._window_size:
            return False

        # Drop old packets
        # C#: if (relate < 0) { ... }
        if relate < 0:
            return False

        # C#: if (relate >= _windowSize * 2) { ... }
        if relate >= self._window_size * 2:
            return False

        # Process ACK bitmap and window
        # C#: if (relate >= _windowSize) { ... }
        if relate >= self._window_size:
            # Calculate new window start
            # C#: int newWindowStart = (_remoteWindowStart + relate - _windowSize + 1) % NetConstants.MaxSequence
            new_window_start = (self._remote_window_start + relate - self._window_size + 1) % NetConstants.MAX_SEQUENCE
            self._outgoing_acks.sequence = new_window_start & 0xFFFF

            # Clean old ACK data
            # C#: while (_remoteWindowStart != newWindowStart) { ... }
            while self._remote_window_start != new_window_start:
                ack_idx = self._remote_window_start % self._window_size
                ack_byte = NetConstants.CHANNELED_HEADER_SIZE + ack_idx // BITS_IN_BYTE
                ack_bit = ack_idx % BITS_IN_BYTE
                # C#: _outgoingAcks.RawData[ackByte] &= (byte) ~(1 << ackBit)
                self._outgoing_acks._data[ack_byte] &= ~(1 << ack_bit)
                self._remote_window_start = (self._remote_window_start + 1) % NetConstants.MAX_SEQUENCE

        # Trigger ACKs send
        # C#: _mustSendAcks = true
        self._must_send_acks = True

        # Calculate ACK position
        # C#: ackIdx = seq % _windowSize
        #     ackByte = NetConstants.ChanneledHeaderSize + ackIdx / BitsInByte
        #     ackBit = ackIdx % BitsInByte
        ack_idx = seq % self._window_size
        ack_byte = NetConstants.CHANNELED_HEADER_SIZE + ack_idx // BITS_IN_BYTE
        ack_bit = ack_idx % BITS_IN_BYTE

        # Check for duplicate
        # C#: if ((_outgoingAcks.RawData[ackByte] & (1 << ackBit)) != 0) { ... }
        if (self._outgoing_acks._data[ack_byte] & (1 << ack_bit)) != 0:
            # Duplicate packet
            # C#: AddToPeerChannelSendQueue(); return false
            self._add_to_peer_channel_send_queue()
            return False

        # Save ACK
        # C#: _outgoingAcks.RawData[ackByte] |= (byte) (1 << ackBit)
        self._outgoing_acks._data[ack_byte] |= (1 << ack_bit)

        # Trigger send
        # C#: AddToPeerChannelSendQueue()
        self._add_to_peer_channel_send_queue()

        # Detailed check - expected packet?
        # C#: if (seq == _remoteSequence) { ... }
        if seq == self._remote_sequence:
            # Expected packet - deliver immediately
            # C#: Peer.AddReliablePacket(_deliveryMethod, packet)
            if hasattr(self._peer, 'add_reliable_packet'):
                self._peer.add_reliable_packet(self._delivery_method, packet)

            # Advance sequence
            # C#: _remoteSequence = (_remoteSequence + 1) % NetConstants.MaxSequence
            self._remote_sequence = (self._remote_sequence + 1) % NetConstants.MAX_SEQUENCE

            # Process held packets (for ordered mode)
            if self._ordered:
                # C#: while ((p = _receivedPackets[_remoteSequence % _windowSize]) != null) { ... }
                while True:
                    idx = self._remote_sequence % self._window_size
                    p = self._received_packets[idx]
                    if p is None:
                        break
                    # C#: _receivedPackets[_remoteSequence % _windowSize] = null
                    self._received_packets[idx] = None
                    # C#: Peer.AddReliablePacket(_deliveryMethod, p)
                    if hasattr(self._peer, 'add_reliable_packet'):
                        self._peer.add_reliable_packet(self._delivery_method, p)
                    # C#: _remoteSequence = (_remoteSequence + 1) % NetConstants.MaxSequence
                    self._remote_sequence = (self._remote_sequence + 1) % NetConstants.MAX_SEQUENCE
            else:
                # Unordered - process early received flags
                # C#: while (_earlyReceived[_remoteSequence % _windowSize]) { ... }
                while self._early_received[self._remote_sequence % self._window_size]:
                    self._early_received[self._remote_sequence % self._window_size] = False
                    self._remote_sequence = (self._remote_sequence + 1) % NetConstants.MAX_SEQUENCE

            return True

        # Hold packet for later delivery
        # C#: //holden packet
        if self._ordered:
            # C#: _receivedPackets[ackIdx] = packet
            self._received_packets[ack_idx] = packet
        else:
            # C#: _earlyReceived[ackIdx] = true; Peer.AddReliablePacket(_deliveryMethod, packet)
            self._early_received[ack_idx] = True
            if hasattr(self._peer, 'add_reliable_packet'):
                self._peer.add_reliable_packet(self._delivery_method, packet)

        return True

    def _process_ack(self, packet: NetPacket) -> None:
        """
        Process ACK packet.

        Args:
            packet: ACK packet to process

        C# Equivalent: private void ProcessAck(NetPacket packet)
        """
        # Validate ACK packet size
        # C#: if (packet.Size != _outgoingAcks.Size) { ... }
        if packet.size != self._outgoing_acks.size:
            return

        ack_window_start = packet.sequence
        window_rel = NetUtils.relative_sequence_number(self._local_window_start, ack_window_start)

        # Validate window start
        # C#: if (ackWindowStart >= NetConstants.MaxSequence || windowRel < 0) { ... }
        if ack_window_start >= NetConstants.MAX_SEQUENCE or window_rel < 0:
            return

        # Check relevance
        # C#: if (windowRel >= _windowSize) { ... }
        if window_rel >= self._window_size:
            return

        acks_data = packet._data

        # Process acknowledged packets
        # C#: for (int pendingSeq = _localWindowStart; pendingSeq != _localSeqence; pendingSeq = ...)
        pending_seq = self._local_window_start
        while pending_seq != self._local_sequence:
            rel = NetUtils.relative_sequence_number(pending_seq, ack_window_start)

            # C#: if (rel >= _windowSize) { ... }
            if rel >= self._window_size:
                break

            # Calculate position in ACK bitmap
            # C#: int pendingIdx = pendingSeq % _windowSize
            #     int currentByte = NetConstants.ChanneledHeaderSize + pendingIdx / BitsInByte
            #     int currentBit = pendingIdx % BitsInByte
            pending_idx = pending_seq % self._window_size
            current_byte = NetConstants.CHANNELED_HEADER_SIZE + pending_idx // BITS_IN_BYTE
            current_bit = pending_idx % BITS_IN_BYTE

            # Check if packet was acknowledged
            # C#: if ((acksData[currentByte] & (1 << currentBit)) == 0) { ... }
            if (acks_data[current_byte] & (1 << current_bit)) == 0:
                # Packet not acknowledged yet - skip
                pending_seq = (pending_seq + 1) % NetConstants.MAX_SEQUENCE
                continue

            # Move window if this is the start
            # C#: if (pendingSeq == _localWindowStart) { _localWindowStart = ... }
            if pending_seq == self._local_window_start:
                self._local_window_start = (self._local_window_start + 1) % NetConstants.MAX_SEQUENCE

            # Clear packet
            # C#: if (_pendingPackets[pendingIdx].Clear(Peer)) { ... }
            self._pending_packets[pending_idx].clear(self._peer)

            pending_seq = (pending_seq + 1) % NetConstants.MAX_SEQUENCE

    def __repr__(self) -> str:
        ordered_str = "ordered" if self._ordered else "unordered"
        return (f"ReliableChannel(id={self._id}, {ordered_str}, "
                f"local_seq={self._local_sequence}, remote_seq={self._remote_sequence})")
