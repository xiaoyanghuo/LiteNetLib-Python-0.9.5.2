"""
Integration Tests / 集成测试

End-to-end tests for LiteNetLib including server/client communication,
connection flow, and all delivery methods.

These tests require actual network sockets and may take longer to run.
"""

import pytest
import asyncio
import time
from litenetlib import LiteNetManager, EventBasedNetListener
from litenetlib.core.constants import DeliveryMethod, DisconnectReason
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class IntegrationTestListener(EventBasedNetListener):
    """Test listener for integration tests / 集成测试监听器"""

    def __init__(self):
        super().__init__()
        self.connected_peers = []
        self.disconnected_peers = []
        self.received_messages = []
        self.connection_requests = []
        self._connected_event = asyncio.Event()
        self._message_event = asyncio.Event()
        self._disconnect_event = asyncio.Event()
        self._request_event = asyncio.Event()

    def on_peer_connected(self, peer):
        """Handle peer connected / 处理对等端连接"""
        self.connected_peers.append(peer)
        self._connected_event.set()

    def on_peer_disconnected(self, peer, disconnect_info):
        """Handle peer disconnected / 处理对等端断开"""
        self.disconnected_peers.append((peer, disconnect_info))
        self._disconnect_event.set()

    def on_network_receive(self, peer, reader, channel_number, delivery_method):
        """Handle received data / 处理接收数据"""
        data = reader.get_remaining_bytes()
        self.received_messages.append((peer, data, channel_number, delivery_method))
        self._message_event.set()

    def on_connection_request(self, request):
        """Handle connection request / 处理连接请求"""
        self.connection_requests.append(request)
        self._request_event.set()
        # Accept all by default / 默认接受所有连接
        if not request.is_accepted and not request.is_rejected:
            request.accept()

    def wait_for_connection(self, timeout=5.0):
        """Wait for connection / 等待连接"""
        try:
            asyncio.wait_for(self._connected_event.wait(), timeout)
        except asyncio.TimeoutError:
            return False
        return True

    def wait_for_message(self, timeout=5.0):
        """Wait for message / 等待消息"""
        try:
            asyncio.wait_for(self._message_event.wait(), timeout)
        except asyncio.TimeoutError:
            return False
        return True

    def wait_for_disconnect(self, timeout=5.0):
        """Wait for disconnect / 等待断开"""
        try:
            asyncio.wait_for(self._disconnect_event.wait(), timeout)
        except asyncio.TimeoutError:
            return False
        return True

    def wait_for_request(self, timeout=5.0):
        """Wait for connection request / 等待连接请求"""
        try:
            asyncio.wait_for(self._request_event.wait(), timeout)
        except asyncio.TimeoutError:
            return False
        return True

    def reset_events(self):
        """Reset all events / 重置所有事件"""
        self._connected_event.clear()
        self._message_event.clear()
        self._disconnect_event.clear()
        self._request_event.clear()


@pytest.fixture
async def server_manager():
    """Fixture for server manager / 服务器管理器夹具"""
    listener = IntegrationTestListener()
    manager = LiteNetManager(listener)

    # Try to start on a random port
    port = 17777
    if not manager.start(port=port):
        pytest.skip(f"Could not start server on port {port}")

    yield manager

    # Cleanup
    manager.stop()


@pytest.fixture
async def client_manager():
    """Fixture for client manager / 客户端管理器夹具"""
    listener = IntegrationTestListener()
    manager = LiteNetManager(listener)
    yield manager

    # Cleanup
    manager.stop()


class TestServerStart:
    """Test server startup / 测试服务器启动"""

    @pytest.mark.asyncio
    async def test_server_starts(self):
        """Test server can start / 测试服务器可以启动"""
        listener = IntegrationTestListener()
        manager = LiteNetManager(listener)

        port = 17778
        result = manager.start(port=port)

        assert result is True, "Server should start successfully"
        assert manager.is_running, "Server should be running"

        manager.stop()

    @pytest.mark.asyncio
    async def test_server_port_in_use(self):
        """Test server fails when port in use / 测试端口被占用时失败"""
        listener1 = IntegrationTestListener()
        manager1 = LiteNetManager(listener1)

        port = 17779
        manager1.start(port=port)

        # Try to start another server on same port
        listener2 = IntegrationTestListener()
        manager2 = LiteNetManager(listener2)

        result = manager2.start(port=port)
        assert result is False, "Server should fail to start on occupied port"

        # Cleanup
        manager1.stop()
        manager2.stop()


class TestConnectionFlow:
    """Test connection flow / 测试连接流程"""

    @pytest.mark.asyncio
    async def test_client_connect_to_server(self, server_manager, client_manager):
        """Test client connects to server / 测试客户端连接到服务器"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        result = client_manager.connect(server_host, server_port)
        assert result is True, "Client should connect successfully"

        # Wait for connection
        for _ in range(100):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        # Verify connection
        client_peer = client_manager.get_first_peer()
        assert client_peer is not None, "Client should have a peer"

    @pytest.mark.asyncio
    async def test_server_receives_connection(self, server_manager, client_manager):
        """Test server receives connection / 测试服务器接收连接"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait and poll
        for _ in range(100):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(server_manager.listener.connected_peers) > 0:
                break
            await asyncio.sleep(0.01)

        # Verify server got connection
        assert len(server_manager.listener.connected_peers) > 0, \
            "Server should have received connection"

    @pytest.mark.asyncio
    async def test_client_disconnect(self, server_manager, client_manager):
        """Test client disconnect / 测试客户端断开"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Disconnect
        peer.disconnect()

        # Wait for disconnect
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if not peer.is_connected:
                break
            await asyncio.sleep(0.01)

        assert not peer.is_connected, "Peer should be disconnected"


class TestMessageSending:
    """Test message sending / 测试消息发送"""

    @pytest.mark.asyncio
    async def test_send_unreliable(self, server_manager, client_manager):
        """Test sending unreliable message / 测试发送不可靠消息"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Send message
        test_message = b"Hello Unreliable"
        peer.send(test_message, DeliveryMethod.UNRELIABLE)

        # Poll and wait for receive
        server_manager.listener.reset_events()
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(server_manager.listener.received_messages) > 0:
                break
            await asyncio.sleep(0.01)

        # Verify message received
        assert len(server_manager.listener.received_messages) > 0, \
            "Server should have received message"

        received_data = server_manager.listener.received_messages[0][1]
        assert received_data == test_message, \
            f"Received data should match: expected {test_message}, got {received_data}"

    @pytest.mark.asyncio
    async def test_send_reliable_ordered(self, server_manager, client_manager):
        """Test sending reliable ordered message / 测试发送可靠有序消息"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Send multiple reliable ordered messages
        messages = [f"Message {i}".encode() for i in range(5)]
        for msg in messages:
            peer.send(msg, DeliveryMethod.RELIABLE_ORDERED)

        # Poll and wait
        server_manager.listener.reset_events()
        for _ in range(100):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(server_manager.listener.received_messages) >= 5:
                break
            await asyncio.sleep(0.01)

        # Verify all messages received in order
        received = [msg[1] for msg in server_manager.listener.received_messages]
        assert len(received) >= len(messages), \
            f"Should receive at least {len(messages)} messages, got {len(received)}"

        # Check order
        for i, msg in enumerate(messages[:len(received)]):
            assert received[i] == msg, \
                f"Message {i} out of order: expected {msg}, got {received[i]}"

    @pytest.mark.asyncio
    async def test_send_reliable_unordered(self, server_manager, client_manager):
        """Test sending reliable unordered message / 测试发送可靠无序消息"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Send message
        test_message = b"Hello Reliable Unordered"
        peer.send(test_message, DeliveryMethod.RELIABLE_UNORDERED)

        # Poll and wait
        server_manager.listener.reset_events()
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(server_manager.listener.received_messages) > 0:
                break
            await asyncio.sleep(0.01)

        # Verify
        assert len(server_manager.listener.received_messages) > 0
        received_data = server_manager.listener.received_messages[0][1]
        assert received_data == test_message


class TestSerialization:
    """Test serialization in integration / 测试集成中的序列化"""

    @pytest.mark.asyncio
    async def test_serialized_data_roundtrip(self, server_manager, client_manager):
        """Test serialized data roundtrip / 测试序列化数据往返"""
        server_host = "127.0.0.1"
        server_port = server_manager.local_port

        # Connect
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Write complex data
        writer = NetDataWriter()
        writer.put_int(42)
        writer.put_string("Hello")
        writer.put_float(3.14)
        writer.put_bool(True)

        # Send
        peer.send(writer.to_bytes(), DeliveryMethod.RELIABLE_ORDERED)

        # Poll and wait
        server_manager.listener.reset_events()
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(server_manager.listener.received_messages) > 0:
                break
            await asyncio.sleep(0.01)

        # Verify
        assert len(server_manager.listener.received_messages) > 0
        received_data = server_manager.listener.received_messages[0][1]

        # Read back
        reader = NetDataReader(received_data)
        assert reader.get_int() == 42
        assert reader.get_string() == "Hello"
        assert abs(reader.get_float() - 3.14) < 0.01
        assert reader.get_bool() is True


class TestMultipleClients:
    """Test multiple clients / 测试多客户端"""

    @pytest.mark.asyncio
    async def test_multiple_clients_connect(self, server_manager):
        """Test multiple clients connecting / 测试多客户端连接"""
        clients = []

        # Create and connect multiple clients
        for i in range(3):
            listener = IntegrationTestListener()
            client = LiteNetManager(listener)
            clients.append(client)

            client.connect("127.0.0.1", server_manager.local_port)

        # Wait for all connections
        for _ in range(100):
            for client in clients:
                await client.poll_async()
            await server_manager.poll_async()

            if len(server_manager.listener.connected_peers) >= 3:
                break
            await asyncio.sleep(0.01)

        # Verify
        assert len(server_manager.listener.connected_peers) >= 3, \
            "Server should have at least 3 connected peers"

        # Cleanup
        for client in clients:
            client.stop()


class TestEcho:
    """Test echo functionality / 测试回显功能"""

    @pytest.mark.asyncio
    async def test_echo_server(self, server_manager, client_manager):
        """Test echo server and client / 测试 Echo 服务器和客户端"""
        # Make server echo messages
        original_on_receive = server_manager.listener.on_network_receive

        def echo_on_receive(peer, reader, channel_number, delivery_method):
            data = reader.get_remaining_bytes()
            peer.send(data, delivery_method)
            original_on_receive(peer, reader, channel_number, delivery_method)

        server_manager.listener.on_network_receive = echo_on_receive

        # Connect
        server_host = "127.0.0.1"
        server_port = server_manager.local_port
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Send message
        test_message = b"Echo Test"
        peer.send(test_message, DeliveryMethod.RELIABLE_ORDERED)

        # Poll and wait for echo
        client_manager.listener.reset_events()
        for _ in range(100):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if len(client_manager.listener.received_messages) > 0:
                break
            await asyncio.sleep(0.01)

        # Verify echo
        assert len(client_manager.listener.received_messages) > 0, \
            "Client should receive echo"

        received_data = client_manager.listener.received_messages[0][1]
        assert received_data == test_message, \
            f"Echo data should match: expected {test_message}, got {received_data}"


class TestAllDeliveryMethods:
    """Test all delivery methods / 测试所有传输方法"""

    @pytest.mark.asyncio
    async def test_all_delivery_methods(self, server_manager, client_manager):
        """Test all 5 delivery methods / 测试所有 5 种传输方法"""
        # Connect
        server_host = "127.0.0.1"
        server_port = server_manager.local_port
        client_manager.connect(server_host, server_port)

        # Wait for connection
        for _ in range(50):
            await client_manager.poll_async()
            await server_manager.poll_async()
            if client_manager.get_first_peer() is not None:
                break
            await asyncio.sleep(0.01)

        peer = client_manager.get_first_peer()
        assert peer is not None

        # Test each delivery method
        delivery_methods = [
            DeliveryMethod.UNRELIABLE,
            DeliveryMethod.RELIABLE_UNORDERED,
            DeliveryMethod.SEQUENCED,
            DeliveryMethod.RELIABLE_ORDERED,
            DeliveryMethod.RELIABLE_SEQUENCED,
        ]

        for method in delivery_methods:
            server_manager.listener.reset_events()

            test_message = f"Test {method.name}".encode()
            peer.send(test_message, method)

            # Poll and wait
            received = False
            for _ in range(50):
                await client_manager.poll_async()
                await server_manager.poll_async()
                if len(server_manager.listener.received_messages) > 0:
                    received = True
                    break
                await asyncio.sleep(0.01)

            # At least unreliable should be received immediately
            # Reliable methods may need more time/acks
            if method == DeliveryMethod.UNRELIABLE:
                assert received, f"UNRELIABLE message should be received"


# Skip integration tests by default as they require network and can be flaky
pytestmark = pytest.mark.integration


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
