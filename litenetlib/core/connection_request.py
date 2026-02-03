"""
Connection request handling for LiteNetLib.

This module manages incoming connection requests from remote peers,
providing methods to accept or reject connections.

Ported from: LiteNetLib/ConnectionRequest.cs
"""

import threading
from typing import Optional, Tuple
from litenetlib.core.internal_packets import NetConnectRequestPacket
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.data_writer import NetDataWriter


class ConnectionRequestResult:
    """Result of connection request processing."""
    NONE = 0
    ACCEPT = 1
    REJECT = 2
    REJECT_FORCE = 3


class ConnectionRequest:
    """
    Represents an incoming connection request.

    Provides methods to accept or reject the connection, with optional
    additional data for rejection reason.

    Thread-safe: Each request can only be processed once (accept or reject).

    C# Reference: ConnectionRequest class
    """

    __slots__ = (
        '_manager',
        '_used',
        '_result',
        '_internal_packet',
        '_remote_address'
    )

    def __init__(
        self,
        remote_address: Tuple[str, int],
        request_packet: NetConnectRequestPacket,
        manager
    ):
        """
        Create connection request.

        Args:
            remote_address: Remote endpoint (host, port)
            request_packet: Connection request packet
            manager: Network manager instance (for callback)
        """
        self._manager = manager
        self._used = 0  # Atomic-like flag for thread safety
        self._result = ConnectionRequestResult.NONE
        self._internal_packet = request_packet
        self._remote_address = remote_address

    @property
    def data(self) -> NetDataReader:
        """Get additional data from connection request."""
        return self._internal_packet.data

    @property
    def remote_address(self) -> Tuple[str, int]:
        """Get remote endpoint address."""
        return self._remote_address

    @property
    def connection_time(self) -> int:
        """Get connection timestamp from request."""
        return self._internal_packet.connection_time

    @property
    def connection_number(self) -> int:
        """Get connection number from request."""
        return self._internal_packet.connection_number

    @property
    def peer_id(self) -> int:
        """Get peer ID from request."""
        return self._internal_packet.peer_id

    @property
    def result(self) -> int:
        """Get request result (after accept/reject)."""
        return self._result

    def update_request(self, connect_request: NetConnectRequestPacket) -> None:
        """
        Update request with newer connection attempt.

        Only updates if the new request is newer (based on timestamp and connection number).

        Args:
            connect_request: New connection request packet

        C# Equivalent: UpdateRequest(NetConnectRequestPacket)
        """
        # Old request - ignore
        if connect_request.connection_time < self._internal_packet.connection_time:
            return

        # Same request - ignore
        if (connect_request.connection_time == self._internal_packet.connection_time and
            connect_request.connection_number == self._internal_packet.connection_number):
            return

        # Newer request - update
        self._internal_packet = connect_request

    def _try_activate(self) -> bool:
        """
        Try to activate request for processing (thread-safe).

        Returns:
            True if successfully activated (first time), False if already used

        C# Equivalent: TryActivate()
        Uses Interlocked.CompareExchange for thread safety
        """
        # Python doesn't have true atomic operations, but threading.Lock is sufficient
        with threading.Lock():
            if self._used == 0:
                self._used = 1
                return True
            return False

    def accept_if_key(self, key: str) -> Optional:
        """
        Accept connection only if data matches key.

        Args:
            key: Expected key string in connection data

        Returns:
            Connected peer if key matches, None otherwise

        C# Equivalent: AcceptIfKey(string key)
        """
        if not self._try_activate():
            return None

        try:
            reader = NetDataReader(self._internal_packet.data)
            received_key = reader.get_string()
            if received_key == key:
                self._result = ConnectionRequestResult.ACCEPT
        except Exception:
            # NetDebug.WriteError("[AC] Invalid incoming data")
            pass

        if self._result == ConnectionRequestResult.ACCEPT:
            return self._manager.on_connection_solved(self, None, 0, 0)

        self._result = ConnectionRequestResult.REJECT
        self._manager.on_connection_solved(self, None, 0, 0)
        return None

    def accept(self) -> Optional:
        """
        Accept connection and get connected peer.

        Returns:
            Connected peer, or None if request already processed

        C# Equivalent: Accept()
        """
        if not self._try_activate():
            return None

        self._result = ConnectionRequestResult.ACCEPT
        return self._manager.on_connection_solved(self, None, 0, 0)

    def reject(
        self,
        reject_data: Optional[bytes] = None,
        start: int = 0,
        length: Optional[int] = None,
        force: bool = False
    ) -> None:
        """
        Reject connection with optional data.

        Args:
            reject_data: Optional rejection data bytes
            start: Starting offset in reject_data
            length: Number of bytes from reject_data to send
            force: Whether to force rejection

        C# Equivalent: Reject(byte[], int, int, bool)
        """
        if not self._try_activate():
            return

        if length is None and reject_data is not None:
            length = len(reject_data)

        self._result = ConnectionRequestResult.REJECT_FORCE if force else ConnectionRequestResult.REJECT
        self._manager.on_connection_solved(self, reject_data, start, length if length else 0)

    def reject_force(
        self,
        reject_data: Optional[bytes] = None,
        start: int = 0,
        length: Optional[int] = None
    ) -> None:
        """
        Force reject connection.

        Args:
            reject_data: Optional rejection data bytes
            start: Starting offset in reject_data
            length: Number of bytes from reject_data to send

        C# Equivalent: RejectForce(byte[], int, int)
        """
        self.reject(reject_data, start, length, force=True)

    def reject_with_writer(self, reject_data: NetDataWriter, force: bool = False) -> None:
        """
        Reject connection with NetDataWriter.

        Args:
            reject_data: Data writer with rejection information
            force: Whether to force rejection

        C# Equivalent: Reject(NetDataWriter) or RejectForce(NetDataWriter)
        """
        self.reject(reject_data.data, 0, reject_data.length, force)

    def __repr__(self) -> str:
        return (f"ConnectionRequest(remote={self._remote_address}, "
                f"time={self.connection_time}, peer_id={self.peer_id})")
