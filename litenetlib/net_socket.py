"""
NetSocket.cs translation

UDP socket wrapper for IPv4 and IPv6
"""

import socket
import threading
from typing import Optional, Callable, Tuple
from .constants import NetConstants


class NetSocket:
    """
    UDP Socket wrapper

    C# class: internal class NetSocket
    """

    # Class-level IPv6 support detection
    _ipv6_support: Optional[bool] = None

    def __init__(self, net_manager):
        """
        Initialize socket

        C# constructor: internal NetSocket(NetManager netManager)
        """
        self._net_manager = net_manager
        self._udp_socket_v4: Optional[socket.socket] = None
        self._udp_socket_v6: Optional[socket.socket] = None
        self._is_running: bool = False

        # Receive threads
        self._receive_thread_v4: Optional[threading.Thread] = None
        self._receive_thread_v6: Optional[threading.Thread] = None

    @classmethod
    def ipv6_support(cls) -> bool:
        """
        Check if IPv6 is supported

        C# property: internal static bool IPv6Support
        """
        if cls._ipv6_support is None:
            try:
                s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                s.close()
                cls._ipv6_support = True
            except OSError:
                cls._ipv6_support = False
        return cls._ipv6_support

    @property
    def is_running(self) -> bool:
        """Check if socket is running"""
        return self._is_running

    def start(self, port: int, listen_ipv4: bool, listen_ipv6: bool) -> bool:
        """
        Start socket

        C# method: internal bool Start(int port, bool listenIPv4, bool listenIPv6)
        """
        if self._is_running:
            return False

        try:
            if listen_ipv4:
                self._udp_socket_v4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._udp_socket_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._udp_socket_v4.setsockopt(
                    socket.SOL_SOCKET, socket.SO_RCVBUF, NetConstants.SocketBufferSize
                )
                self._udp_socket_v4.bind(("", port))

            if listen_ipv6 and NetSocket.ipv6_support():
                self._udp_socket_v6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._udp_socket_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._udp_socket_v6.setsockopt(
                    socket.SOL_SOCKET, socket.SO_RCVBUF, NetConstants.SocketBufferSize
                )
                # Set IPV6_V6ONLY to 0 to allow dual-stack
                self._udp_socket_v6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                self._udp_socket_v6.bind(("", port))

            self._is_running = True

            # Start receive threads
            if self._udp_socket_v4 is not None:
                self._receive_thread_v4 = threading.Thread(
                    target=self._receive_loop_v4, daemon=True
                )
                self._receive_thread_v4.start()

            if self._udp_socket_v6 is not None:
                self._receive_thread_v6 = threading.Thread(
                    target=self._receive_loop_v6, daemon=True
                )
                self._receive_thread_v6.start()

            return True

        except socket.error as e:
            self.stop()
            return False

    def _receive_loop_v4(self):
        """Receive loop for IPv4"""
        buffer = bytearray(NetConstants.SocketBufferSize)
        while self._is_running:
            try:
                data, addr = self._udp_socket_v4.recvfrom_into(buffer)
                self._net_manager.on_message_received(
                    bytes(buffer[:data]), (addr[0], addr[1])
                )
            except socket.error as e:
                if self._is_running:
                    self._net_manager.on_network_error(None, e)

    def _receive_loop_v6(self):
        """Receive loop for IPv6"""
        buffer = bytearray(NetConstants.SocketBufferSize)
        while self._is_running:
            try:
                data, addr = self._udp_socket_v6.recvfrom_into(buffer)
                self._net_manager.on_message_received(
                    bytes(buffer[:data]), (addr[0], addr[1])
                )
            except socket.error as e:
                if self._is_running:
                    self._net_manager.on_network_error(None, e)

    def send_packet(self, data: bytes, address: Tuple[str, int], ipv6: bool = False) -> int:
        """
        Send packet to address

        C# method: internal int SendPacket(byte[] data, int offset, int size, Socket target, EndPoint remoteEndPoint)
        """
        try:
            if ipv6 and self._udp_socket_v6 is not None:
                return self._udp_socket_v6.sendto(data, address)
            elif self._udp_socket_v4 is not None:
                return self._udp_socket_v4.sendto(data, address)
            return 0
        except socket.error:
            return 0

    def stop(self) -> None:
        """
        Stop socket

        C# method: internal void Stop()
        """
        self._is_running = False

        # Close sockets
        if self._udp_socket_v4 is not None:
            try:
                self._udp_socket_v4.close()
            except socket.error:
                pass
            self._udp_socket_v4 = None

        if self._udp_socket_v6 is not None:
            try:
                self._udp_socket_v6.close()
            except socket.error:
                pass
            self._udp_socket_v6 = None

        # Wait for threads to finish
        if self._receive_thread_v4 is not None:
            self._receive_thread_v4.join(timeout=1.0)
            self._receive_thread_v4 = None

        if self._receive_thread_v6 is not None:
            self._receive_thread_v6.join(timeout=1.0)
            self._receive_thread_v6 = None


__all__ = ["NetSocket"]
