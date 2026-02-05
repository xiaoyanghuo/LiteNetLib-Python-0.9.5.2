"""
NetUtils.cs translation

Network utility functions
"""

import socket
import struct
from typing import List, Optional
from enum import IntFlag
from .constants import NetConstants


class LocalAddrType(IntFlag):
    """
    Address type for local IP detection

    C# enum: [Flags] public enum LocalAddrType
    """

    IPv4 = 1
    IPv6 = 2
    All = IPv4 | IPv6


class NetUtils:
    """
    Network utilities

    C# class: public static class NetUtils
    """

    @staticmethod
    def make_endpoint(host_str: str, port: int) -> tuple:
        """
        Create endpoint from host and port

        C# method: public static IPEndPoint MakeEndPoint(string hostStr, int port)
        """
        addr = NetUtils.resolve_address(host_str)
        return (addr, port)

    @staticmethod
    def resolve_address(host_str: str) -> str:
        """
        Resolve address string to IP

        C# method: public static IPAddress ResolveAddress(string hostStr)
        """
        if host_str == "localhost":
            return "127.0.0.1"

        try:
            # Try to parse as IP address
            socket.inet_pton(socket.AF_INET, host_str)
            return host_str
        except socket.error:
            pass

        try:
            socket.inet_pton(socket.AF_INET6, host_str)
            return host_str
        except socket.error:
            pass

        # DNS resolution
        try:
            # Try IPv6 first
            if NetUtils._is_ipv6_supported():
                result = NetUtils._resolve_address_family(host_str, socket.AF_INET6)
                if result:
                    return result
            # Fallback to IPv4
            result = NetUtils._resolve_address_family(host_str, socket.AF_INET)
            if result:
                return result
        except socket.gaierror:
            pass

        raise ValueError(f"Invalid address: {host_str}")

    @staticmethod
    def _is_ipv6_supported() -> bool:
        """Check if IPv6 is supported"""
        try:
            socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            return True
        except OSError:
            return False

    @staticmethod
    def _resolve_address_family(host_str: str, family) -> Optional[str]:
        """
        Resolve address with specific address family

        C# method: public static IPAddress ResolveAddress(string hostStr, AddressFamily addressFamily)
        """
        try:
            addrinfo = socket.getaddrinfo(host_str, None, family)
            for info in addrinfo:
                return info[4][0]
        except socket.gaierror:
            pass
        return None

    @staticmethod
    def get_local_ip_list(addr_type: LocalAddrType = LocalAddrType.All) -> List[str]:
        """
        Get all local IP addresses

        C# method: public static List<string> GetLocalIpList(LocalAddrType addrType)
        """
        result = []
        NetUtils.get_local_ip_list_ref(result, addr_type)
        return result

    @staticmethod
    def get_local_ip_list_ref(target_list: List[str], addr_type: LocalAddrType) -> None:
        """
        Get all local IP addresses (non-alloc version)

        C# method: public static void GetLocalIpList(IList<string> targetList, LocalAddrType addrType)
        """
        ipv4 = bool(addr_type & LocalAddrType.IPv4)
        ipv6 = bool(addr_type & LocalAddrType.IPv6)

        try:
            hostname = socket.gethostname()
            addrinfo = socket.getaddrinfo(hostname, None)

            for info in addrinfo:
                family = info[0]
                addr = info[4][0]

                if (ipv4 and family == socket.AF_INET) or (ipv6 and family == socket.AF_INET6):
                    # Skip loopback
                    if not addr.startswith("127.") and not addr == "::1":
                        if addr not in target_list:
                            target_list.append(addr)
        except socket.error:
            pass

        # Fallback
        if not target_list:
            if ipv4:
                target_list.append("127.0.0.1")
            if ipv6:
                target_list.append("::1")

    @staticmethod
    def get_local_ip(addr_type: LocalAddrType = LocalAddrType.All) -> str:
        """
        Get first detected local IP address

        C# method: public static string GetLocalIp(LocalAddrType addrType)
        """
        ip_list = NetUtils.get_local_ip_list(addr_type)
        return ip_list[0] if ip_list else ""

    @staticmethod
    def relative_sequence_number(number: int, expected: int) -> int:
        """
        Calculate relative sequence number

        C# method: internal static int RelativeSequenceNumber(int number, int expected)
        """
        return (
            (number - expected + NetConstants.MaxSequence + NetConstants.HalfMaxSequence)
            % NetConstants.MaxSequence
            - NetConstants.HalfMaxSequence
        )

    @staticmethod
    def print_interface_infos() -> None:
        """Print network interface information (debug)"""
        from .debug import NetDebug, NetLogLevel
        from .net_socket import NetSocket

        NetDebug.write_force_with_level(
            NetLogLevel.Info, f"IPv6Support: {NetSocket.ipv6_support}"
        )

        try:
            hostname = socket.gethostname()
            addrinfo = socket.getaddrinfo(hostname, None)

            for info in addrinfo:
                family = info[0]
                addr = info[4][0]

                if family in [socket.AF_INET, socket.AF_INET6]:
                    family_name = "IPv4" if family == socket.AF_INET else "IPv6"
                    NetDebug.write_force_with_level(
                        NetLogLevel.Info, f"Interface: {hostname}, Type: {family_name}, Ip: {addr}"
                    )
        except Exception as e:
            NetDebug.write_force_with_level(
                NetLogLevel.Info, f"Error while getting interface infos: {e}"
            )


__all__ = ["LocalAddrType", "NetUtils"]
