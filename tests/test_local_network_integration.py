"""
本机多进程网络集成测试

使用多进程在localhost上模拟实际网络通信
"""

import pytest
import socket
import threading
import time
from multiprocessing import Process, Queue
from litenetlib.utils import NetDataReader, NetDataWriter


class TestLocalhostSocketCommunication:
    """测试本机socket通信"""

    def test_localhost_tcp_connection(self):
        """测试localhost TCP连接"""
        server_ready = threading.Event()
        server_received = Queue()
        client_done = threading.Event()

        def server_thread():
            # Start a simple TCP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('127.0.0.1', 0))  # Bind to random port
            port = server_socket.getsockname()[1]
            server_socket.listen(1)

            server_ready.set()
            server_ready.port = port

            # Wait for connection
            conn, addr = server_socket.accept()

            # Receive data
            data = conn.recv(1024)
            server_received.put(data)

            # Send response
            conn.send(b"Server response")

            conn.close()
            server_socket.close()

        def client_thread(port):
            # Wait for server to be ready
            server_ready.wait()

            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))

            # Send data
            test_data = b"Hello from client"
            client_socket.send(test_data)

            # Receive response
            response = client_socket.recv(1024)

            client_socket.close()
            client_done.set()

        # Start server and client
        server = threading.Thread(target=server_thread)
        client = threading.Thread(target=client_thread, args=(None,))

        server.start()
        time.sleep(0.1)  # Let server start

        # Update client with actual port
        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        client_done.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify data was received
        received_data = server_received.get(timeout=1)
        assert received_data == b"Hello from client"

    def test_localhost_udp_connection(self):
        """测试localhost UDP通信"""
        server_received = Queue()
        server_ready = threading.Event()
        client_done = threading.Event()

        def server_thread():
            # Start UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive data
            data, addr = server_socket.recvfrom(1024)
            server_received.put((data, addr))

            # Send response
            server_socket.sendto(b"UDP response", addr)

            server_socket.close()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create UDP client
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send data
            test_data = b"Hello via UDP"
            client_socket.sendto(test_data, ('127.0.0.1', port))

            # Receive response
            response, _ = client_socket.recvfrom(1024)
            assert response == b"UDP response"

            client_socket.close()
            client_done.set()

        # Start threads
        server = threading.Thread(target=server_thread)
        client = threading.Thread(target=client_thread, args=(None,))

        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        client_done.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify data
        received_data, addr = server_received.get(timeout=1)
        assert received_data == b"Hello via UDP"


class TestNetDataWriterReaderUDPLocalhost:
    """测试通过UDP在localhost传输序列化数据"""

    def test_send_serialized_data_udp(self):
        """测试通过UDP发送NetDataWriter序列化的数据"""
        server_received = Queue()
        server_ready = threading.Event()
        test_complete = threading.Event()

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive data
            data, addr = server_socket.recvfrom(4096)
            server_received.put(data)

            server_socket.close()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Create test data using NetDataWriter
            writer = NetDataWriter()
            writer.put_int(12345)
            writer.put_string("Test message")
            writer.put_float(3.14159)

            # Send via UDP
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(writer.data, ('127.0.0.1', port))
            client_socket.close()

            test_complete.set()

        # Start threads
        server = threading.Thread(target=server_thread)
        client = threading.Thread(target=client_thread, args=(None,))

        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        test_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify received data can be deserialized
        received_data = server_received.get(timeout=1)
        reader = NetDataReader(received_data)

        value1 = reader.get_int()
        assert value1 == 12345

        value2 = reader.get_string()
        assert value2 == "Test message"

        value3 = reader.get_float()
        assert abs(value3 - 3.14159) < 0.0001

    def test_bidirectional_serialized_data(self):
        """测试双向序列化数据传输"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        client_complete = threading.Event()

        server_received_data = Queue()
        client_received_data = Queue()

        def server_thread():
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive from client
            data, client_addr = server_socket.recvfrom(4096)
            server_received_data.put(data)

            # Send response
            writer = NetDataWriter()
            writer.put_int(99999)
            writer.put_string("Server reply")
            server_socket.sendto(writer.data, client_addr)

            server_socket.close()
            server_complete.set()

        def client_thread(port):
            # Wait for server
            server_ready.wait()

            # Send to server
            writer = NetDataWriter()
            writer.put_int(11111)
            writer.put_string("Client message")

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(writer.data, ('127.0.0.1', port))

            # Receive response
            data, _ = client_socket.recvfrom(4096)
            client_received_data.put(data)

            client_socket.close()
            client_complete.set()

        # Start threads
        server = threading.Thread(target=server_thread)
        client = threading.Thread(target=client_thread, args=(None,))

        server.start()
        time.sleep(0.1)

        client = threading.Thread(target=client_thread, args=(server_ready.port,))
        client.start()

        # Wait for completion
        server_complete.wait(timeout=5)
        client_complete.wait(timeout=5)
        server.join(timeout=5)
        client.join(timeout=5)

        # Verify server received client data
        server_data = server_received_data.get(timeout=1)
        reader = NetDataReader(server_data)
        assert reader.get_int() == 11111
        assert reader.get_string() == "Client message"

        # Verify client received server response
        client_data = client_received_data.get(timeout=1)
        reader = NetDataReader(client_data)
        assert reader.get_int() == 99999
        assert reader.get_string() == "Server reply"


class TestMultipleClients:
    """测试多个客户端连接到服务器"""

    def test_multiple_udp_clients(self):
        """测试多个UDP客户端向同一服务器发送数据"""
        server_ready = threading.Event()
        server_complete = threading.Event()
        messages_received = Queue()

        def server_thread(num_clients=3):
            # UDP server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('127.0.0.1', 0))
            port = server_socket.getsockname()[1]

            server_ready.set()
            server_ready.port = port

            # Receive from multiple clients
            for i in range(num_clients):
                data, addr = server_socket.recvfrom(1024)
                reader = NetDataReader(data)
                msg = reader.get_string()
                messages_received.put((msg, addr))

            server_socket.close()
            server_complete.set()

        def client_thread(client_id, port):
            # Wait for server
            server_ready.wait()

            # Send message
            writer = NetDataWriter()
            writer.put_string(f"Client {client_id} message")

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(writer.data, ('127.0.0.1', port))
            client_socket.close()

        # Start server
        server = threading.Thread(target=server_thread)
        server.start()
        time.sleep(0.1)

        # Start multiple clients
        clients = []
        for i in range(3):
            client = threading.Thread(target=client_thread, args=(i, server_ready.port))
            client.start()
            clients.append(client)

        # Wait for completion
        server_complete.wait(timeout=5)
        server.join(timeout=5)
        for client in clients:
            client.join(timeout=5)

        # Verify all messages received
        messages = []
        while not messages_received.empty():
            msg, addr = messages_received.get()
            messages.append(msg)

        assert len(messages) == 3
        for i in range(3):
            assert f"Client {i} message" in messages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
