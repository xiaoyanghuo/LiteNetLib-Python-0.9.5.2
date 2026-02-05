"""
INetEventListener.cs translation

Event listener interfaces for network events
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .net_peer import NetPeer


class INetEventListener(ABC):
    """
    Interface for network event listeners

    C# interface: public interface INetEventListener
    """

    def on_peer_connected(self, peer: "NetPeer") -> None:
        """
        Called when peer connects

        C# method: void OnPeerConnected(NetPeer peer)
        """
        pass

    def on_peer_disconnected(
        self, peer: "NetPeer", disconnect_info: "DisconnectInfo"
    ) -> None:
        """
        Called when peer disconnects

        C# method: void OnPeerDisconnected(NetPeer peer, DisconnectInfo disconnectInfo)
        """
        pass

    def on_network_error(
        self, endpoint: tuple, socket_error: Exception
    ) -> None:
        """
        Called on network error

        C# method: void OnNetworkError(IPEndPoint endPoint, SocketError socketError)
        """
        pass

    def on_network_receive(self, peer: "NetPeer", data: bytes) -> None:
        """
        Called when data is received

        C# method: void OnNetworkReceive(NetPeer peer, NetDataReader reader)
        """
        pass

    def on_network_receive_unconnected(self, address: tuple, data: bytes) -> None:
        """
        Called when unconnected data is received

        C# methods:
        - void OnNetworkReceiveUnconnected(IPEndPoint remoteEndPoint, NetDataReader reader, UnconnectedMessageType messageType)
        """
        pass

    def on_connection_request(self, request: "ConnectionRequest") -> None:
        """
        Called when connection request is received

        C# method: void OnConnectionRequest(ConnectionRequest request)
        """
        pass


class DisconnectInfo:
    """
    Disconnection information

    C# struct: public struct DisconnectInfo
    """

    def __init__(
        self,
        reason: "DisconnectReason",
        socket_error: Exception = None,
        additional_data: bytes = None,
    ):
        self.reason = reason
        self.socket_error = socket_error
        self.additional_data = additional_data


class DisconnectReason:
    """
    Disconnect reason constants

    C# enum: public enum DisconnectReason
    """

    ConnectionRejected = 0
    Timeout = 1
    HostUnreachable = 2
    NetworkUnreachable = 3
    RemoteConnectionClose = 4
    DisconnectPeerCalled = 5
    ConnectionFailed = 6
    InvalidProtocol = 7
    UnknownHost = 8
    Reconnect = 9
    PeerNotFound = 10


class EventBasedNetListener:
    """
    Event-based listener implementation

    C# class: public class EventBasedNetListener
    """

    def __init__(self):
        self._peer_connected_callbacks = []
        self._peer_disconnected_callbacks = []
        self._network_error_callbacks = []
        self._network_receive_callbacks = []
        self._network_receive_unconnected_callbacks = []
        self._connection_request_callbacks = []

    def add_peer_connected_callback(self, callback):
        """Add callback for peer connected"""
        self._peer_connected_callbacks.append(callback)

    def add_peer_disconnected_callback(self, callback):
        """Add callback for peer disconnected"""
        self._peer_disconnected_callbacks.append(callback)

    def add_network_error_callback(self, callback):
        """Add callback for network error"""
        self._network_error_callbacks.append(callback)

    def add_network_receive_callback(self, callback):
        """Add callback for network receive"""
        self._network_receive_callbacks.append(callback)

    def add_network_receive_unconnected_callback(self, callback):
        """Add callback for unconnected receive"""
        self._network_receive_unconnected_callbacks.append(callback)

    def add_connection_request_callback(self, callback):
        """Add callback for connection request"""
        self._connection_request_callbacks.append(callback)

    # INetEventListener implementation

    def on_peer_connected(self, peer: "NetPeer") -> None:
        for callback in self._peer_connected_callbacks:
            callback(peer)

    def on_peer_disconnected(
        self, peer: "NetPeer", disconnect_info: DisconnectInfo
    ) -> None:
        for callback in self._peer_disconnected_callbacks:
            callback(peer, disconnect_info)

    def on_network_error(self, endpoint: tuple, socket_error: Exception) -> None:
        for callback in self._network_error_callbacks:
            callback(endpoint, socket_error)

    def on_network_receive(self, peer: "NetPeer", data: bytes) -> None:
        for callback in self._network_receive_callbacks:
            callback(peer, data)

    def on_network_receive_unconnected(self, address: tuple, data: bytes) -> None:
        for callback in self._network_receive_unconnected_callbacks:
            callback(address, data)

    def on_connection_request(self, request: "ConnectionRequest") -> None:
        for callback in self._connection_request_callbacks:
            callback(request)


__all__ = [
    "INetEventListener",
    "EventBasedNetListener",
    "DisconnectInfo",
    "DisconnectReason",
]
