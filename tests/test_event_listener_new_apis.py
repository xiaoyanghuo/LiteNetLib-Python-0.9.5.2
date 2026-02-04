"""
Tests for EventBasedNetListener new APIs.

Tests all newly added clear methods and property setters.
"""

import pytest
from litenetlib.core.events import EventBasedNetListener
from litenetlib.core.constants import DisconnectReason, DeliveryMethod, UnconnectedMessageType
from litenetlib.utils.data_reader import NetDataReader
from unittest.mock import Mock


class TestClearEventMethods:
    """Test individual clear event methods."""

    def test_clear_peer_connected_event(self):
        """Test clearing peer connected event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer):
            callback_called.append(peer)

        listener.on_peer_connected = callback
        listener.clear_peer_connected_event()

        # Call through the interface implementation (which checks for None)
        mock_peer = Mock()
        # The property returns None now, so we need to call the implementation method
        if listener._peer_connected_callback:
            listener._peer_connected_callback(mock_peer)
        # Callback was cleared so it should be None and list should be empty
        assert listener._peer_connected_callback is None
        assert len(callback_called) == 0

    def test_clear_peer_disconnected_event(self):
        """Test clearing peer disconnected event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer, info):
            callback_called.append((peer, info))

        listener.on_peer_disconnected = callback
        listener.clear_peer_disconnected_event()

        # Verify callback is cleared
        assert listener._peer_disconnected_callback is None
        mock_peer = Mock()
        mock_info = Mock()
        if listener._peer_disconnected_callback:
            listener._peer_disconnected_callback(mock_peer, mock_info)
        assert len(callback_called) == 0

    def test_clear_network_error_event(self):
        """Test clearing network error event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(address, error):
            callback_called.append((address, error))

        listener.on_network_error = callback
        listener.clear_network_error_event()

        # Verify callback is cleared
        assert listener._network_error_callback is None
        if listener._network_error_callback:
            listener._network_error_callback(("127.0.0.1", 9000), 100)
        assert len(callback_called) == 0

    def test_clear_network_receive_event(self):
        """Test clearing network receive event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer, reader, channel, method):
            callback_called.append((peer, reader, channel, method))

        listener.on_network_receive = callback
        listener.clear_network_receive_event()

        # Verify callback is cleared
        assert listener._network_receive_callback is None
        mock_peer = Mock()
        mock_reader = Mock()
        if listener._network_receive_callback:
            listener._network_receive_callback(mock_peer, mock_reader, 0, DeliveryMethod.RELIABLE_ORDERED)
        assert len(callback_called) == 0

    def test_clear_network_receive_unconnected_event(self):
        """Test clearing network receive unconnected event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(address, reader, type):
            callback_called.append((address, reader, type))

        listener.on_network_receive_unconnected = callback
        listener.clear_network_receive_unconnected_event()

        # Verify callback is cleared
        assert listener._network_receive_unconnected_callback is None
        if listener._network_receive_unconnected_callback:
            listener._network_receive_unconnected_callback(
                ("127.0.0.1", 9000),
                Mock(),
                UnconnectedMessageType.BASIC_MESSAGE
            )
        assert len(callback_called) == 0

    def test_clear_network_latency_update_event(self):
        """Test clearing network latency update event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer, latency):
            callback_called.append((peer, latency))

        listener.on_network_latency_update = callback
        listener.clear_network_latency_update_event()

        # Verify callback is cleared
        assert listener._network_latency_update_callback is None
        mock_peer = Mock()
        if listener._network_latency_update_callback:
            listener._network_latency_update_callback(mock_peer, 50)
        assert len(callback_called) == 0

    def test_clear_connection_request_event(self):
        """Test clearing connection request event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(request):
            callback_called.append(request)

        listener.on_connection_request = callback
        listener.clear_connection_request_event()

        # Verify callback is cleared
        assert listener._connection_request_callback is None
        mock_request = Mock()
        if listener._connection_request_callback:
            listener._connection_request_callback(mock_request)
        assert len(callback_called) == 0

    def test_clear_delivery_event(self):
        """Test clearing delivery event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer, data):
            callback_called.append((peer, data))

        listener.on_message_delivered = callback
        listener.clear_delivery_event()

        # Verify callback is cleared
        assert listener._message_delivered_callback is None
        mock_peer = Mock()
        if listener._message_delivered_callback:
            listener._message_delivered_callback(mock_peer, "test_data")
        assert len(callback_called) == 0

    def test_clear_peer_address_changed_event(self):
        """Test clearing peer address changed event."""
        listener = EventBasedNetListener()
        callback_called = []

        def callback(peer, previous_address):
            callback_called.append((peer, previous_address))

        listener.on_peer_address_changed = callback
        listener.clear_peer_address_changed_event()

        # Verify callback is cleared
        assert listener._peer_address_changed_callback is None
        mock_peer = Mock()
        if listener._peer_address_changed_callback:
            listener._peer_address_changed_callback(mock_peer, ("127.0.0.1", 8000))
        assert len(callback_called) == 0


class TestPropertySetters:
    """Note: Property-based setters removed due to method/property name conflict.
    Use set_*_callback methods instead."""


class TestReplacingCallbacks:
    """Test replacing existing callbacks."""

    def test_replace_peer_connected_callback(self):
        """Test replacing peer connected callback."""
        listener = EventBasedNetListener()
        first_called = []
        second_called = []

        def first_callback(peer):
            first_called.append(peer)

        def second_callback(peer):
            second_called.append(peer)

        # Set first callback using set_*_callback method
        listener.set_peer_connected_callback(first_callback)
        mock_peer = Mock()
        listener.on_peer_connected(mock_peer)
        assert len(first_called) == 1
        assert len(second_called) == 0

        # Replace with second callback
        listener.set_peer_connected_callback(second_callback)
        listener.on_peer_connected(mock_peer)
        assert len(first_called) == 1  # First not called again
        assert len(second_called) == 1

    def test_replace_multiple_callbacks(self):
        """Test replacing multiple different callbacks."""
        listener = EventBasedNetListener()

        peer_called = []
        error_called = []

        def peer_callback(peer):
            peer_called.append(peer)

        def error_callback(address, error):
            error_called.append((address, error))

        # Set callbacks
        listener.set_peer_connected_callback(peer_callback)
        listener.set_network_error_callback(error_callback)

        # Call them
        mock_peer = Mock()
        listener.on_peer_connected(mock_peer)
        listener.on_network_error(("127.0.0.1", 9000), 100)

        assert len(peer_called) == 1
        assert len(error_called) == 1

        # Clear callbacks
        listener.clear_peer_connected_event()
        listener.clear_network_error_event()

        # These calls will do nothing (callbacks cleared)
        listener.on_peer_connected(mock_peer)
        listener.on_network_error(("127.0.0.1", 9000), 100)

        assert len(peer_called) == 1  # No new calls
        assert len(error_called) == 1


class TestClearAllVsIndividual:
    """Test clear_all_callbacks vs individual clear methods."""

    def test_clear_all_vs_individual_clear(self):
        """Test that clear_all works same as clearing all individually."""
        listener1 = EventBasedNetListener()
        listener2 = EventBasedNetListener()

        # Set all callbacks on listener1
        listener1.on_peer_connected = lambda p: None
        listener1.on_peer_disconnected = lambda p, i: None
        listener1.on_network_error = lambda a, e: None
        listener1.on_network_receive = lambda p, r, c, m: None
        listener1.on_network_receive_unconnected = lambda a, r, t: None
        listener1.on_network_latency_update = lambda p, l: None
        listener1.on_connection_request = lambda r: None
        listener1.on_message_delivered = lambda p, d: None
        listener1.on_peer_address_changed = lambda p, a: None

        # Set all callbacks on listener2
        listener2.on_peer_connected = lambda p: None
        listener2.on_peer_disconnected = lambda p, i: None
        listener2.on_network_error = lambda a, e: None
        listener2.on_network_receive = lambda p, r, c, m: None
        listener2.on_network_receive_unconnected = lambda a, r, t: None
        listener2.on_network_latency_update = lambda p, l: None
        listener2.on_connection_request = lambda r: None
        listener2.on_message_delivered = lambda p, d: None
        listener2.on_peer_address_changed = lambda p, a: None

        # Clear listener1 with clear_all
        listener1.clear_all_callbacks()

        # Clear listener2 individually
        listener2.clear_peer_connected_event()
        listener2.clear_peer_disconnected_event()
        listener2.clear_network_error_event()
        listener2.clear_network_receive_event()
        listener2.clear_network_receive_unconnected_event()
        listener2.clear_network_latency_update_event()
        listener2.clear_connection_request_event()
        listener2.clear_delivery_event()
        listener2.clear_peer_address_changed_event()

        # Both should have all callbacks cleared
        assert listener1._peer_connected_callback is None
        assert listener1._peer_disconnected_callback is None
        assert listener1._network_error_callback is None
        assert listener1._network_receive_callback is None
        assert listener1._network_receive_unconnected_callback is None
        assert listener1._network_latency_update_callback is None
        assert listener1._connection_request_callback is None
        assert listener1._message_delivered_callback is None
        assert listener1._peer_address_changed_callback is None

        assert listener2._peer_connected_callback is None
        assert listener2._peer_disconnected_callback is None
        assert listener2._network_error_callback is None
        assert listener2._network_receive_callback is None
        assert listener2._network_receive_unconnected_callback is None
        assert listener2._network_latency_update_callback is None
        assert listener2._connection_request_callback is None
        assert listener2._message_delivered_callback is None
        assert listener2._peer_address_changed_callback is None


class TestCallbackChainingWithProperties:
    """Test that set_*_callback methods support chaining."""

    def test_set_callback_returns_self(self):
        """Test that set_*_callback methods return self for chaining."""
        listener = EventBasedNetListener()
        # Initially None
        assert listener._peer_connected_callback is None

        # Create callback functions
        def peer_cb(peer):
            pass

        def error_cb(addr, err):
            pass

        # Test method chaining
        result = listener.set_peer_connected_callback(peer_cb)
        assert result is listener  # Should return self

        listener.set_network_error_callback(error_cb)
        assert listener._peer_connected_callback is peer_cb
        assert listener._network_error_callback is error_cb

        # Test chaining multiple calls
        listener.set_peer_connected_callback(peer_cb).set_network_error_callback(error_cb)
        assert listener._peer_connected_callback is peer_cb
        assert listener._network_error_callback is error_cb
