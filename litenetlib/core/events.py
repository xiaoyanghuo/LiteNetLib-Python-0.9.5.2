"""
Event system for LiteNetLib.

Defines event listeners and related types for handling network events.
"""

from typing import Optional, Callable, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from litenetlib.core.constants import DisconnectReason, UnconnectedMessageType, DeliveryMethod
from litenetlib.utils.data_reader import NetDataReader


@dataclass
class DisconnectInfo:
    """
    Additional information about disconnection.

    Attributes:
        reason: The reason for disconnection
        socket_error: Socket error code (if applicable)
        additional_data: Additional data received with disconnect (only for RemoteConnectionClose)
    """
    reason: DisconnectReason
    socket_error: Optional[int] = None
    additional_data: Optional[NetDataReader] = None

    def __repr__(self) -> str:
        return f"DisconnectInfo(reason={self.reason.name}, socket_error={self.socket_error})"


class INetEventListener(ABC):
    """
    Interface for implementing network event listener.

    Implement this interface to handle network events.
    This is more efficient than using EventBasedNetListener.
    """

    @abstractmethod
    def on_peer_connected(self, peer) -> None:
        """
        Called when a new peer connects.

        Args:
            peer: The connected peer object
        """
        pass

    @abstractmethod
    def on_peer_disconnected(self, peer, disconnect_info: DisconnectInfo) -> None:
        """
        Called when a peer disconnects.

        Args:
            peer: The disconnected peer
            disconnect_info: Additional information about the disconnection
        """
        pass

    def on_network_error(self, address: Optional[tuple], socket_error: int) -> None:
        """
        Called when a network error occurs.

        Args:
            address: Remote address (can be None)
            socket_error: Socket error code
        """
        pass

    @abstractmethod
    def on_network_receive(
        self,
        peer,
        reader: NetDataReader,
        channel_number: int,
        delivery_method: DeliveryMethod
    ) -> None:
        """
        Called when data is received from a peer.

        Args:
            peer: The peer that sent the data
            reader: Data reader containing received data
            channel_number: Channel number the data was received on
            delivery_method: Delivery method of the received packet
        """
        pass

    def on_network_receive_unconnected(
        self,
        remote_address: tuple,
        reader: NetDataReader,
        message_type: UnconnectedMessageType
    ) -> None:
        """
        Called when an unconnected message is received.

        Args:
            remote_address: Remote endpoint (host, port)
            reader: Data reader containing message data
            message_type: Type of unconnected message
        """
        pass

    def on_network_latency_update(self, peer, latency: int) -> None:
        """
        Called when latency information is updated.

        Args:
            peer: The peer with updated latency
            latency: Latency value in milliseconds
        """
        pass

    @abstractmethod
    def on_connection_request(self, request) -> None:
        """
        Called when a connection request is received.

        Args:
            request: Connection request information
        """
        pass

    def on_message_delivered(self, peer, user_data: Any) -> None:
        """
        Called when a reliable message is delivered.

        Args:
            peer: The peer the message was delivered to
            user_data: User data attached to the message
        """
        pass

    def on_peer_address_changed(self, peer, previous_address: tuple) -> None:
        """
        Called when a peer's address changes.

        Args:
            peer: The peer with new address
            previous_address: The previous address
        """
        pass


class EventBasedNetListener(INetEventListener):
    """
    Event-based listener using Python callbacks.

    Simpler to use than implementing INetEventListener directly,
    but slightly less efficient due to callback overhead.
    """

    def __init__(self):
        self._peer_connected_callback: Optional[Callable] = None
        self._peer_disconnected_callback: Optional[Callable] = None
        self._network_error_callback: Optional[Callable] = None
        self._network_receive_callback: Optional[Callable] = None
        self._network_receive_unconnected_callback: Optional[Callable] = None
        self._network_latency_update_callback: Optional[Callable] = None
        self._connection_request_callback: Optional[Callable] = None
        self._message_delivered_callback: Optional[Callable] = None
        self._peer_address_changed_callback: Optional[Callable] = None

    # Callback setters

    def set_peer_connected_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for peer connected event."""
        self._peer_connected_callback = callback
        return self

    def set_peer_disconnected_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for peer disconnected event."""
        self._peer_disconnected_callback = callback
        return self

    def set_network_error_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for network error event."""
        self._network_error_callback = callback
        return self

    def set_network_receive_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for data received event."""
        self._network_receive_callback = callback
        return self

    def set_network_receive_unconnected_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for unconnected message received event."""
        self._network_receive_unconnected_callback = callback
        return self

    def set_network_latency_update_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for latency update event."""
        self._network_latency_update_callback = callback
        return self

    def set_connection_request_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for connection request event."""
        self._connection_request_callback = callback
        return self

    def set_message_delivered_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for message delivered event."""
        self._message_delivered_callback = callback
        return self

    def set_peer_address_changed_callback(self, callback: Callable) -> 'EventBasedNetListener':
        """Set callback for peer address changed event."""
        self._peer_address_changed_callback = callback
        return self

    # Clear callbacks

    def clear_all_callbacks(self) -> None:
        """Clear all registered callbacks."""
        self._peer_connected_callback = None
        self._peer_disconnected_callback = None
        self._network_error_callback = None
        self._network_receive_callback = None
        self._network_receive_unconnected_callback = None
        self._network_latency_update_callback = None
        self._connection_request_callback = None
        self._message_delivered_callback = None
        self._peer_address_changed_callback = None

    # INetEventListener implementation

    def on_peer_connected(self, peer) -> None:
        if self._peer_connected_callback:
            self._peer_connected_callback(peer)

    def on_peer_disconnected(self, peer, disconnect_info: DisconnectInfo) -> None:
        if self._peer_disconnected_callback:
            self._peer_disconnected_callback(peer, disconnect_info)

    def on_network_error(self, address: Optional[tuple], socket_error: int) -> None:
        if self._network_error_callback:
            self._network_error_callback(address, socket_error)

    def on_network_receive(
        self,
        peer,
        reader: NetDataReader,
        channel_number: int,
        delivery_method: DeliveryMethod
    ) -> None:
        if self._network_receive_callback:
            self._network_receive_callback(peer, reader, channel_number, delivery_method)

    def on_network_receive_unconnected(
        self,
        remote_address: tuple,
        reader: NetDataReader,
        message_type: UnconnectedMessageType
    ) -> None:
        if self._network_receive_unconnected_callback:
            self._network_receive_unconnected_callback(remote_address, reader, message_type)

    def on_network_latency_update(self, peer, latency: int) -> None:
        if self._network_latency_update_callback:
            self._network_latency_update_callback(peer, latency)

    def on_connection_request(self, request) -> None:
        if self._connection_request_callback:
            self._connection_request_callback(request)

    def on_message_delivered(self, peer, user_data: Any) -> None:
        if self._message_delivered_callback:
            self._message_delivered_callback(peer, user_data)

    def on_peer_address_changed(self, peer, previous_address: tuple) -> None:
        if self._peer_address_changed_callback:
            self._peer_address_changed_callback(peer, previous_address)


class ConnectionRequest:
    """
    Represents an incoming connection request.

    Provides methods to accept or reject the connection.
    """

    def __init__(self, remote_address: tuple, data: Optional[bytes] = None):
        """
        Create a new connection request.

        Args:
            remote_address: Remote endpoint (host, port)
            data: Additional data sent with request
        """
        self._remote_address = remote_address
        self._data = data
        self._accepted = False
        self._rejected = False

    @property
    def remote_address(self) -> tuple:
        """Get remote endpoint address."""
        return self._remote_address

    @property
    def data(self) -> Optional[bytes]:
        """Get additional request data."""
        return self._data

    def accept(self) -> None:
        """Accept the connection request."""
        if self._rejected:
            raise RuntimeError("Cannot accept: request already rejected")
        self._accepted = True

    def reject(self, reject_data: Optional[bytes] = None) -> None:
        """
        Reject the connection request.

        Args:
            reject_data: Optional data to send with rejection
        """
        if self._accepted:
            raise RuntimeError("Cannot reject: request already accepted")
        self._rejected = True
        self._reject_data = reject_data

    @property
    def is_accepted(self) -> bool:
        """Check if request was accepted."""
        return self._accepted

    @property
    def is_rejected(self) -> bool:
        """Check if request was rejected."""
        return self._rejected

    def __repr__(self) -> str:
        return f"ConnectionRequest(address={self._remote_address})"
