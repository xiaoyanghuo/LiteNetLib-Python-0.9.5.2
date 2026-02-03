"""
Event System Tests / 事件系统测试

Tests for event listener classes including INetEventListener,
EventBasedNetListener, and ConnectionRequest.

Reference C# Code: LiteNetLib/Utils/NetEventListener.cs
"""

import pytest
from litenetlib.core.events import (
    INetEventListener,
    EventBasedNetListener,
    ConnectionRequest,
    DisconnectInfo
)
from litenetlib.core.constants import DisconnectReason, UnconnectedMessageType, DeliveryMethod
from litenetlib.utils.data_reader import NetDataReader
from unittest.mock import Mock


class TestDisconnectInfo:
    """Test DisconnectInfo / 测试 DisconnectInfo"""

    def test_disconnect_info_creation(self):
        """Test creating DisconnectInfo / 测试创建 DisconnectInfo"""
        info = DisconnectInfo(reason=DisconnectReason.TIMEOUT)
        assert info.reason == DisconnectReason.TIMEOUT
        assert info.socket_error is None
        assert info.additional_data is None

    def test_disconnect_info_with_socket_error(self):
        """Test DisconnectInfo with socket error / 测试带套接字错误的 DisconnectInfo"""
        info = DisconnectInfo(
            reason=DisconnectReason.NETWORK_UNREACHABLE,
            socket_error=10054
        )
        assert info.reason == DisconnectReason.NETWORK_UNREACHABLE
        assert info.socket_error == 10054

    def test_disconnect_info_with_additional_data(self):
        """Test DisconnectInfo with additional data / 测试带附加数据的 DisconnectInfo"""
        reader = NetDataReader(b'Test data')
        info = DisconnectInfo(
            reason=DisconnectReason.REMOTE_CONNECTION_CLOSE,
            additional_data=reader
        )
        assert info.reason == DisconnectReason.REMOTE_CONNECTION_CLOSE
        assert info.additional_data == reader

    def test_disconnect_info_repr(self):
        """Test DisconnectInfo __repr__ / 测试 DisconnectInfo 字符串表示"""
        info = DisconnectInfo(reason=DisconnectReason.TIMEOUT, socket_error=100)
        repr_str = repr(info)
        assert 'TIMEOUT' in repr_str
        assert '100' in repr_str


class TestConnectionRequest:
    """Test ConnectionRequest / 测试 ConnectionRequest"""

    def test_connection_request_creation(self):
        """Test creating ConnectionRequest / 测试创建 ConnectionRequest"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        assert request.remote_address == ("127.0.0.1", 7777)
        assert request.data is None
        assert request.is_accepted is False
        assert request.is_rejected is False

    def test_connection_request_with_data(self):
        """Test ConnectionRequest with data / 测试带数据的 ConnectionRequest"""
        data = b'Connection data'
        request = ConnectionRequest(
            remote_address=("192.168.1.1", 8080),
            data=data
        )
        assert request.data == data

    def test_connection_request_accept(self):
        """Test accepting connection request / 测试接受连接请求"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        request.accept()
        assert request.is_accepted is True
        assert request.is_rejected is False

    def test_connection_request_reject(self):
        """Test rejecting connection request / 测试拒绝连接请求"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        request.reject()
        assert request.is_accepted is False
        assert request.is_rejected is True

    def test_connection_request_reject_with_data(self):
        """Test rejecting with data / 测试带数据拒绝"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        reject_data = b'Rejection reason'
        request.reject(reject_data)
        assert request.is_rejected is True
        assert request._reject_data == reject_data

    def test_connection_request_cannot_accept_after_reject(self):
        """Test cannot accept after reject / 测试拒绝后不能接受"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        request.reject()
        with pytest.raises(RuntimeError, match="Cannot accept"):
            request.accept()

    def test_connection_request_cannot_reject_after_accept(self):
        """Test cannot reject after accept / 测试接受后不能拒绝"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        request.accept()
        with pytest.raises(RuntimeError, match="Cannot reject"):
            request.reject()

    def test_connection_request_repr(self):
        """Test ConnectionRequest __repr__ / 测试 ConnectionRequest 字符串表示"""
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        repr_str = repr(request)
        assert 'ConnectionRequest' in repr_str
        assert '127.0.0.1' in repr_str
        assert '7777' in repr_str


class TestEventBasedNetListener:
    """Test EventBasedNetListener / 测试 EventBasedNetListener"""

    def test_listener_creation(self):
        """Test creating listener / 测试创建监听器"""
        listener = EventBasedNetListener()
        assert listener._peer_connected_callback is None
        assert listener._peer_disconnected_callback is None

    def test_set_peer_connected_callback(self):
        """Test setting peer connected callback / 测试设置连接回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        result = listener.set_peer_connected_callback(callback)
        assert result is listener  # Fluent interface
        assert listener._peer_connected_callback == callback

    def test_set_peer_disconnected_callback(self):
        """Test setting peer disconnected callback / 测试设置断开回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_disconnected_callback(callback)
        assert listener._peer_disconnected_callback == callback

    def test_set_network_error_callback(self):
        """Test setting network error callback / 测试设置网络错误回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_error_callback(callback)
        assert listener._network_error_callback == callback

    def test_set_network_receive_callback(self):
        """Test setting network receive callback / 测试设置接收回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_callback(callback)
        assert listener._network_receive_callback == callback

    def test_set_network_receive_unconnected_callback(self):
        """Test setting unconnected receive callback / 测试设置无连接接收回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_unconnected_callback(callback)
        assert listener._network_receive_unconnected_callback == callback

    def test_set_network_latency_update_callback(self):
        """Test setting latency update callback / 测试设置延迟更新回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_latency_update_callback(callback)
        assert listener._network_latency_update_callback == callback

    def test_set_connection_request_callback(self):
        """Test setting connection request callback / 测试设置连接请求回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_connection_request_callback(callback)
        assert listener._connection_request_callback == callback

    def test_set_message_delivered_callback(self):
        """Test setting message delivered callback / 测试设置消息发送回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_message_delivered_callback(callback)
        assert listener._message_delivered_callback == callback

    def test_set_peer_address_changed_callback(self):
        """Test setting address changed callback / 测试设置地址改变回调"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_address_changed_callback(callback)
        assert listener._peer_address_changed_callback == callback

    def test_clear_all_callbacks(self):
        """Test clearing all callbacks / 测试清除所有回调"""
        listener = EventBasedNetListener()
        callback = Mock()

        listener.set_peer_connected_callback(callback)
        listener.set_peer_disconnected_callback(callback)
        listener.clear_all_callbacks()

        assert listener._peer_connected_callback is None
        assert listener._peer_disconnected_callback is None
        assert listener._network_error_callback is None


class TestEventCallbacks:
    """Test event callback invocation / 测试事件回调调用"""

    def test_on_peer_connected_callback(self):
        """Test on_peer_connected invokes callback / 测试连接回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_connected_callback(callback)

        peer = Mock()
        listener.on_peer_connected(peer)

        callback.assert_called_once_with(peer)

    def test_on_peer_disconnected_callback(self):
        """Test on_peer_disconnected invokes callback / 测试断开回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_disconnected_callback(callback)

        peer = Mock()
        disconnect_info = DisconnectInfo(reason=DisconnectReason.TIMEOUT)
        listener.on_peer_disconnected(peer, disconnect_info)

        callback.assert_called_once_with(peer, disconnect_info)

    def test_on_network_error_callback(self):
        """Test on_network_error invokes callback / 测试网络错误回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_error_callback(callback)

        address = ("127.0.0.1", 7777)
        socket_error = 10054
        listener.on_network_error(address, socket_error)

        callback.assert_called_once_with(address, socket_error)

    def test_on_network_receive_callback(self):
        """Test on_network_receive invokes callback / 测试网络接收回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_callback(callback)

        peer = Mock()
        reader = NetDataReader(b'Test data')
        channel_number = 0
        delivery_method = DeliveryMethod.RELIABLE_ORDERED

        listener.on_network_receive(peer, reader, channel_number, delivery_method)

        callback.assert_called_once_with(peer, reader, channel_number, delivery_method)

    def test_on_network_receive_unconnected_callback(self):
        """Test on_network_receive_unconnected invokes callback / 测试无连接接收回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_unconnected_callback(callback)

        remote_address = ("192.168.1.1", 8080)
        reader = NetDataReader(b'Unconnected data')
        message_type = UnconnectedMessageType.BASIC_MESSAGE

        listener.on_network_receive_unconnected(remote_address, reader, message_type)

        callback.assert_called_once_with(remote_address, reader, message_type)

    def test_on_network_latency_update_callback(self):
        """Test on_network_latency_update invokes callback / 测试延迟更新回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_latency_update_callback(callback)

        peer = Mock()
        latency = 50  # milliseconds

        listener.on_network_latency_update(peer, latency)

        callback.assert_called_once_with(peer, latency)

    def test_on_connection_request_callback(self):
        """Test on_connection_request invokes callback / 测试连接请求回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_connection_request_callback(callback)

        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))
        listener.on_connection_request(request)

        callback.assert_called_once_with(request)

    def test_on_message_delivered_callback(self):
        """Test on_message_delivered invokes callback / 测试消息发送回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_message_delivered_callback(callback)

        peer = Mock()
        user_data = {"id": 123}

        listener.on_message_delivered(peer, user_data)

        callback.assert_called_once_with(peer, user_data)

    def test_on_peer_address_changed_callback(self):
        """Test on_peer_address_changed invokes callback / 测试地址改变回调调用"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_address_changed_callback(callback)

        peer = Mock()
        previous_address = ("192.168.1.1", 8080)

        listener.on_peer_address_changed(peer, previous_address)

        callback.assert_called_once_with(peer, previous_address)


class TestCallbackWithoutSetter:
    """Test callback when not set / 测试未设置回调时的行为"""

    def test_on_peer_connected_without_callback(self):
        """Test on_peer_connected without callback set / 测试未设置回调时的连接"""
        listener = EventBasedNetListener()
        peer = Mock()

        # Should not raise exception
        listener.on_peer_connected(peer)

    def test_on_peer_disconnected_without_callback(self):
        """Test on_peer_disconnected without callback set / 测试未设置回调时的断开"""
        listener = EventBasedNetListener()
        peer = Mock()
        info = DisconnectInfo(reason=DisconnectReason.TIMEOUT)

        # Should not raise exception
        listener.on_peer_disconnected(peer, info)

    def test_on_network_receive_without_callback(self):
        """Test on_network_receive without callback set / 测试未设置回调时的接收"""
        listener = EventBasedNetListener()
        peer = Mock()
        reader = NetDataReader(b'Test')

        # Should not raise exception
        listener.on_network_receive(peer, reader, 0, DeliveryMethod.RELIABLE_ORDERED)

    def test_on_connection_request_without_callback(self):
        """Test on_connection_request without callback set / 测试未设置回调时的连接请求"""
        listener = EventBasedNetListener()
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))

        # Should not raise exception
        listener.on_connection_request(request)


class TestINetEventListener:
    """Test INetEventListener interface / 测试 INetEventListener 接口"""

    def test_abstract_methods(self):
        """Test that INetEventListener is abstract / 测试 INetEventListener 是抽象的"""
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            INetEventListener()

    def test_concrete_implementation(self):
        """Test concrete implementation of INetEventListener / 测试 INetEventListener 的具体实现"""
        class ConcreteListener(INetEventListener):
            def on_peer_connected(self, peer):
                pass

            def on_peer_disconnected(self, peer, disconnect_info):
                pass

            def on_network_receive(self, peer, reader, channel_number, delivery_method):
                pass

            def on_connection_request(self, request):
                pass

        # Should be able to create concrete implementation
        listener = ConcreteListener()
        assert listener is not None

        # Should be able to call all methods
        peer = Mock()
        reader = NetDataReader(b'Test')
        info = DisconnectInfo(reason=DisconnectReason.TIMEOUT)
        request = ConnectionRequest(remote_address=("127.0.0.1", 7777))

        listener.on_peer_connected(peer)
        listener.on_peer_disconnected(peer, info)
        listener.on_network_error(None, 0)
        listener.on_network_receive(peer, reader, 0, DeliveryMethod.RELIABLE_ORDERED)
        listener.on_network_receive_unconnected(None, reader, UnconnectedMessageType.BASIC_MESSAGE)
        listener.on_network_latency_update(peer, 50)
        listener.on_connection_request(request)
        listener.on_message_delivered(peer, None)
        listener.on_peer_address_changed(peer, None)


class TestEventChaining:
    """Test event chaining and fluent interface / 测试事件链和流式接口"""

    def test_method_chaining(self):
        """Test callback setter chaining / 测试回调设置器链"""
        listener = EventBasedNetListener()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        result = (listener
                  .set_peer_connected_callback(callback1)
                  .set_peer_disconnected_callback(callback2)
                  .set_network_error_callback(callback3))

        assert result is listener  # All return self
        assert listener._peer_connected_callback == callback1
        assert listener._peer_disconnected_callback == callback2
        assert listener._network_error_callback == callback3


class TestEventWithData:
    """Test events with various data types / 测试带各种数据类型的事件"""

    def test_peer_connected_with_peer_object(self):
        """Test peer connected with peer object / 测试带 peer 对象的连接"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_connected_callback(callback)

        peer = Mock()
        peer.id = 123
        peer.address = ("127.0.0.1", 7777)

        listener.on_peer_connected(peer)

        callback.assert_called_once_with(peer)
        assert callback.call_args[0][0].id == 123

    def test_network_receive_with_reader(self):
        """Test network receive with data reader / 测试带数据读取器的网络接收"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_callback(callback)

        peer = Mock()
        reader = NetDataReader(b'\x05Hello')  # String with length

        listener.on_network_receive(peer, reader, 0, DeliveryMethod.RELIABLE_ORDERED)

        # Callback should receive the reader
        assert callback.called
        received_reader = callback.call_args[0][1]
        assert isinstance(received_reader, NetDataReader)

    def test_disconnect_with_all_reasons(self):
        """Test disconnect with all reasons / 测试所有断开原因"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_peer_disconnected_callback(callback)

        for reason in DisconnectReason:
            info = DisconnectInfo(reason=reason)
            peer = Mock()
            listener.on_peer_disconnected(peer, info)

        assert callback.call_count == len(DisconnectReason)

    def test_unconnected_message_all_types(self):
        """Test unconnected message with all types / 测试所有类型的无连接消息"""
        listener = EventBasedNetListener()
        callback = Mock()
        listener.set_network_receive_unconnected_callback(callback)

        for msg_type in UnconnectedMessageType:
            reader = NetDataReader(b'Test')
            listener.on_network_receive_unconnected(None, reader, msg_type)

        assert callback.call_count == len(UnconnectedMessageType)


class TestMultipleListeners:
    """Test multiple listener instances / 测试多个监听器实例"""

    def test_independent_listeners(self):
        """Test listeners are independent / 测试监听器独立"""
        listener1 = EventBasedNetListener()
        listener2 = EventBasedNetListener()

        callback1 = Mock()
        callback2 = Mock()

        listener1.set_peer_connected_callback(callback1)
        listener2.set_peer_connected_callback(callback2)

        peer = Mock()
        listener1.on_peer_connected(peer)
        listener2.on_peer_connected(peer)

        # Each callback should be called once
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_different_callbacks(self):
        """Test different callbacks on different listeners / 测试不同监听器的不同回调"""
        listener1 = EventBasedNetListener()
        listener2 = EventBasedNetListener()

        callback1 = Mock()
        callback2 = Mock()

        listener1.set_peer_connected_callback(callback1)
        listener2.set_peer_disconnected_callback(callback2)

        peer = Mock()
        info = DisconnectInfo(reason=DisconnectReason.TIMEOUT)

        listener1.on_peer_connected(peer)
        listener2.on_peer_disconnected(peer, info)

        callback1.assert_called_once()
        callback2.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
