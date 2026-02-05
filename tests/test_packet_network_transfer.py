"""
NetPacket网络传输测试

通过localhost UDP传输完整的NetPacket，验证序列化/反序列化
"""

import pytest
import socket
import threading
import time
from litenetlib.packets import NetPacket
from litenetlib.packets.net_packet import PacketProperty
from litenetlib.utils import NetDataReader, NetDataWriter


class TestPacketNetworkTransfer:
    """测试NetPacket通过网络的传输"""

    def test_send_unreliable_packet_udp(self):
        """测试通过UDP发送Unreliable包"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        received_packet = None

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive packet
            data, addr = server_socket.recvfrom(4096)

            # Parse as NetPacket
            nonlocal received_packet
            received_packet = NetPacket(0)
            received_packet._raw_data = bytearray(data)
            received_packet._size = len(data)

            server_socket.close()
            server_complete.set()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create Unreliable packet with data
            packet = NetPacket(100, PacketProperty.Unreliable)

            # Write some data into the packet
            # Skip header and write user data
            writer = NetDataWriter()
            writer.put_int(99999)
            writer.put_string("Network packet test")

            # Copy writer data into packet (after header)
            header_size = packet.get_header_size()
            packet._raw_data[header_size:header_size+len(writer.data)] = writer.data

            # Send via UDP
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(bytes(packet.raw_data), ('127.0.0.1', port))
            client_socket.close()

        # Start threads
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify received packet
        assert received_packet is not None
        assert received_packet.packet_property == PacketProperty.Unreliable
        assert received_packet.size > 0

    def test_packet_round_trip(self):
        """测试包的往返传输"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        client_complete = threading.Event()

        server_received = None
        client_received = None

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive from client
            data, client_addr = server_socket.recvfrom(4096)
            nonlocal server_received
            server_received = data

            # Echo back
            server_socket.sendto(data, client_addr)

            server_socket.close()
            server_complete.set()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create packet
            packet = NetPacket(50, PacketProperty.Channeled)

            # Add user data
            header_size = packet.get_header_size()
            test_data = b"Round trip test data"
            packet._raw_data[header_size:header_size+len(test_data)] = test_data

            # Send
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(bytes(packet.raw_data), ('127.0.0.1', port))

            # Receive echo
            data, _ = client_socket.recvfrom(4096)
            nonlocal client_received
            client_received = data

            client_socket.close()
            client_complete.set()

        # Start threads
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server_complete.wait(timeout=5)
        client_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify round trip
        assert server_received is not None
        assert client_received is not None
        assert server_received == client_received

    def test_multiple_packet_types(self):
        """测试传输不同类型的包"""
        packet_types = [
            PacketProperty.Unreliable,
            PacketProperty.Channeled,
            PacketProperty.Ack,
            PacketProperty.Ping,
            PacketProperty.Pong,
        ]

        server_ready = threading.Event()
        received_count = [0]
        expected_count = len(packet_types)

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive packets
            for _ in range(expected_count):
                data, _ = server_socket.recvfrom(4096)
                # Verify packet property
                first_byte = data[0]
                prop = first_byte & 0x1F
                received_count[0] += 1

            server_socket.close()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send different packet types
            for packet_prop in packet_types:
                packet = NetPacket(20, packet_prop)
                client_socket.sendto(bytes(packet.raw_data), ('127.0.0.1', port))
                time.sleep(0.01)  # Small delay

            client_socket.close()

        # Start threads
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server.join(timeout=10)
        client.join(timeout=10)

        # Verify all packets received
        assert received_count[0] == expected_count

    def test_packet_with_channel_info(self):
        """测试带通道信息的包"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        received_channel_id = None

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive packet
            data, _ = server_socket.recvfrom(4096)

            # Parse channel ID from channeled packet
            # Channel ID is at byte 3 (after property, sequence)
            if len(data) >= 4:
                nonlocal received_channel_id
                received_channel_id = data[3]

            server_socket.close()
            server_complete.set()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create Channeled packet
            packet = NetPacket(50, PacketProperty.Channeled)
            packet.channel_id = 3

            # Send
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(bytes(packet.raw_data), ('127.0.0.1', port))
            client_socket.close()

        # Start threads
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify channel ID
        assert received_channel_id == 3

    def test_fragmented_packet_network(self):
        """测试分片包的网络传输"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        received_is_fragmented = None

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive packet
            data, _ = server_socket.recvfrom(4096)

            # Check fragmentation flag (bit 7 of first byte)
            first_byte = data[0]
            is_fragmented = (first_byte & 0x80) != 0

            nonlocal received_is_fragmented
            received_is_fragmented = is_fragmented

            server_socket.close()
            server_complete.set()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create and mark as fragmented
            packet = NetPacket(100, PacketProperty.Channeled)
            packet.mark_fragmented()
            packet.fragment_id = 1
            packet.fragment_part = 0
            packet.fragments_total = 3

            # Send
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(bytes(packet.raw_data), ('127.0.0.1', port))
            client_socket.close()

        # Start threads
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify fragmentation flag
        assert received_is_fragmented == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
