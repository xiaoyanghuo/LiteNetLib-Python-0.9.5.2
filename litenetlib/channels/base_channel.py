"""
Base channel class for packet delivery (asyncio-compatible).

Channels are responsible for managing packet delivery with specific
reliability and ordering guarantees.

This version uses asyncio while maintaining C# protocol logic.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import NetConstants


class BaseChannel(ABC):
    """
    Base class for all delivery channels.

    Channels manage outgoing packet queues and implement different
    delivery strategies (reliable, sequenced, etc.).

    Uses asyncio.Queue for Python async compatibility while
    maintaining C# protocol logic and algorithms.
    """

    __slots__ = ('_peer', '_outgoing_queue', '_is_added_to_peer_channel_send_queue')

    def __init__(self, peer):
        """
        Initialize base channel.

        Args:
            peer: Associated peer instance
        """
        self._peer = peer

        # Async queue with capacity DefaultWindowSize (matching C#)
        # C#: Queue<NetPacket> OutgoingQueue = new Queue<NetPacket>(NetConstants.DefaultWindowSize)
        self._outgoing_queue = asyncio.Queue(maxsize=NetConstants.DEFAULT_WINDOW_SIZE)

        # Atomic flag (C#: Interlocked.CompareExchange)
        self._is_added_to_peer_channel_send_queue = 0

    @property
    def packets_in_queue(self) -> int:
        """
        Get number of packets in outgoing queue.

        C# Equivalent: public int PacketsInQueue => OutgoingQueue.Count;
        """
        return self._outgoing_queue.qsize()

    def add_to_queue(self, packet: NetPacket) -> None:
        """
        Add a packet to the outgoing queue.

        Args:
            packet: Packet to send

        C# Equivalent: public void AddToQueue(NetPacket packet)
        """
        # C#: lock (OutgoingQueue) { OutgoingQueue.Enqueue(packet); }
        self._outgoing_queue.put_nowait(packet)

        # C#: AddToPeerChannelSendQueue()
        self._add_to_peer_channel_send_queue()

    def _add_to_peer_channel_send_queue(self) -> None:
        """
        Add this channel to peer's channel send queue.

        C# Equivalent: protected void AddToPeerChannelSendQueue()
        """
        # C#: if (Interlocked.CompareExchange(ref _isAddedToPeerChannelSendQueue, 1, 0) == 0)
        if self._is_added_to_peer_channel_send_queue == 0:
            self._is_added_to_peer_channel_send_queue = 1
            # C#: Peer.AddToReliableChannelSendQueue(this)
            if hasattr(self._peer, 'add_channel_to_send_queue'):
                self._peer.add_channel_to_send_queue(self)

    @abstractmethod
    def send_next_packets(self) -> bool:
        """
        Send next packets from queue.

        Returns:
            True if more packets to send, False otherwise

        C# Equivalent: public abstract bool SendNextPackets();
        """
        pass

    @abstractmethod
    def process_packet(self, packet: NetPacket) -> bool:
        """
        Process incoming packet.

        Args:
            packet: Received packet

        Returns:
            True if packet was processed successfully

        C# Equivalent: public abstract bool ProcessPacket(NetPacket packet);
        """
        pass

    def mark_sent(self) -> None:
        """Mark channel as sent (removed from peer send queue)."""
        self._is_added_to_peer_channel_send_queue = 0

    def __repr__(self) -> str:
        return f"BaseChannel(queued={self.packets_in_queue})"
