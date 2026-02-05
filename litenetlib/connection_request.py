"""
ConnectionRequest.cs translation

Connection request handling
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .net_peer import NetPeer

if False:  # Avoid circular import
    from .event_interfaces import INetEventListener


class ConnectionRequest:
    """
    Connection request from remote peer

    C# class: public class ConnectionRequest
    """

    def __init__(
        self,
        net_manager: "NetManager",
        remote_address: tuple,
        internal_packet: bytes,
        connection_time: int,
    ):
        self._net_manager = net_manager
        self._remote_address = remote_address
        self._internal_packet = internal_packet
        self._connection_time = connection_time

    @property
    def remote_address(self) -> tuple:
        """
        Get remote address

        C# property: public IPEndPoint RemoteEndPoint
        """
        return self._remote_address

    def accept(self):
        """
        Accept connection

        C# method: public NetPeer Accept()
        """
        return self._net_manager._accept_connection(self)

    def reject(self, data: bytes = None, reject_with_byte: int = 0) -> None:
        """
        Reject connection

        C# methods:
        - public void Reject()
        - public void Reject(byte[] additionalData)
        - public void Reject(byte rejectByte)
        """
        self._net_manager._reject_connection(
            self._remote_address, data, reject_with_byte
        )


__all__ = ["ConnectionRequest"]
