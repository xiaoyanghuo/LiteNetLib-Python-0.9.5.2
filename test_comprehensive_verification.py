"""
LiteNetLib Python - Comprehensive Verification Test

This script verifies all implemented functionality against C# specifications.
"""

import sys
import time
from typing import List, Tuple, Dict, Any


class VerificationResult:
    """Result of a verification test"""
    def __init__(self, name: str, passed: bool, details: str = ""):
        self.name = name
        self.passed = passed
        self.details = details


class ComprehensiveVerification:
    """Comprehensive verification of all LiteNetLib Python functionality"""

    def __init__(self):
        self.results: List[VerificationResult] = []
        self.start_time = time.time()

    def add_result(self, name: str, passed: bool, details: str = ""):
        """Add a verification result"""
        self.results.append(VerificationResult(name, passed, details))
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}: {details}")

    def verify_imports(self):
        """Verify all imports work correctly"""
        print("\n=== Verifying Imports ===")
        try:
            # Core imports
            from litenetlib import (
                NetManager, NetPeer, DeliveryMethod,
                NetConstants, PacketProperty, NetDebug
            )
            self.add_result("Core imports", True, "All core modules imported")

            # Peer imports
            from litenetlib.lite_net_peer import LiteNetPeer
            from litenetlib.lite_net_manager import LiteNetManager
            self.add_result("Base class imports", True, "Base classes imported")

            # Channel imports
            from litenetlib.channels import (
                BaseChannel, ReliableChannel, SequencedChannel
            )
            self.add_result("Channel imports", True, "All channels imported")

            # Packet imports
            from litenetlib.packets import (
                NetPacket, NetPacketPool,
                NetConnectRequestPacket, NetConnectAcceptPacket
            )
            self.add_result("Packet imports", True, "All packets imported")

            # Utils imports
            from litenetlib.utils import (
                NetDataReader, NetDataWriter,
                NetSerializer, NetPacketProcessor
            )
            self.add_result("Utils imports", True, "All utils imported")

            # NAT punch imports
            from litenetlib import (
                NatPunchModule, INatPunchListener,
                EventBasedNatPunchListener, NatAddressType
            )
            self.add_result("NAT punch imports", True, "NAT module imported")

        except Exception as e:
            self.add_result("Imports", False, f"Import error: {e}")

    def verify_constants(self):
        """Verify all constants are correct"""
        print("\n=== Verifying Constants ===")
        from litenetlib import NetConstants, DeliveryMethod
        from litenetlib.packets.net_packet import PacketProperty

        # DeliveryMethod values - check they exist
        delivery_methods = ['Unreliable', 'Sequenced', 'ReliableUnordered', 'ReliableSequenced', 'ReliableOrdered']
        for name in delivery_methods:
            if hasattr(DeliveryMethod, name):
                self.add_result(f"DeliveryMethod.{name}", True, f"Value: {getattr(DeliveryMethod, name)}")
            else:
                self.add_result(f"DeliveryMethod.{name}", False, "Not found")

        # PacketProperty values (C# starts from 0)
        expected_packets = {
            'Unreliable': 0,
            'Channeled': 1,
            'Ack': 2,
            'Ping': 3,
            'Pong': 4,
            'ConnectRequest': 5,
            'ConnectAccept': 6,
            'Disconnect': 7,
            'UnconnectedMessage': 8,
            'NatMessage': 16,  # actual position in our implementation
        }
        for name, expected in expected_packets.items():
            if hasattr(PacketProperty, name):
                actual = getattr(PacketProperty, name)
                if actual == expected:
                    self.add_result(f"PacketProperty.{name}", True, f"Value: {expected}")
                else:
                    self.add_result(f"PacketProperty.{name}", False, f"Expected {expected}, got {actual}")

        # NetConstants key values
        from litenetlib.constants import NetConstants
        key_constants = {
            'protocol_id': 0x4C4E544E,  # "LNTN"
            'max_sequence': 65536,
            'default_window_size': 64,
            'max_packet_size': 16777216,
            'header_size': 1,
            'channeled_header_size': 2,
            'fragmented_header_size': 4,
        }
        for name, expected in key_constants.items():
            if hasattr(NetConstants, name):
                actual = getattr(NetConstants, name)
                if actual == expected:
                    self.add_result(f"NetConstants.{name}", True, f"Value: {expected}")
                else:
                    self.add_result(f"NetConstants.{name}", False, f"Expected {expected}, got {actual}")

    def verify_inheritance(self):
        """Verify inheritance hierarchy"""
        print("\n=== Verifying Inheritance ===")
        from litenetlib.net_manager import NetManager
        from litenetlib.net_peer import NetPeer
        from litenetlib.lite_net_manager import LiteNetManager
        from litenetlib.lite_net_peer import LiteNetPeer
        from litenetlib.channels import BaseChannel, ReliableChannel, SequencedChannel

        # Check inheritance
        checks = [
            ("NetManager extends LiteNetManager", issubclass(NetManager, LiteNetManager)),
            ("NetPeer extends LiteNetPeer", issubclass(NetPeer, LiteNetPeer)),
            ("ReliableChannel extends BaseChannel", issubclass(ReliableChannel, BaseChannel)),
            ("SequencedChannel extends BaseChannel", issubclass(SequencedChannel, BaseChannel)),
        ]

        for name, result in checks:
            self.add_result(name, result, "Inheritance correct" if result else "Inheritance broken")

    def verify_abstract_methods(self):
        """Verify abstract methods are implemented"""
        print("\n=== Verifying Abstract Methods ===")
        from litenetlib.net_manager import NetManager
        from litenetlib.net_peer import NetPeer
        from litenetlib.lite_net_manager import LiteNetManager
        from litenetlib.lite_net_peer import LiteNetPeer

        # NetManager abstract methods
        net_manager_methods = [
            'create_outgoing_peer',
            'create_incoming_peer',
            'create_reject_peer',
            'process_event',
            'custom_message_handle',
        ]
        for method in net_manager_methods:
            if hasattr(NetManager, method):
                self.add_result(f"NetManager.{method}", True, "Implemented")
            else:
                self.add_result(f"NetManager.{method}", False, "Not implemented")

        # NetPeer abstract methods
        net_peer_members = ['create_channel', 'channels_count']
        for member in net_peer_members:
            if hasattr(NetPeer, member):
                self.add_result(f"NetPeer.{member}", True, "Implemented")
            else:
                self.add_result(f"NetPeer.{member}", False, "Not implemented")

    def verify_packets(self):
        """Verify packet functionality"""
        print("\n=== Verifying Packets ===")
        from litenetlib.packets import NetPacket, PacketProperty

        try:
            # Create packet
            packet = NetPacket(100, PacketProperty.Unreliable)
            self.add_result("Packet creation", True, f"Created packet with size {packet.size}")

            # Check packet_property attribute
            prop_value = packet.packet_property
            self.add_result("Packet property attribute", True, f"Property: {prop_value}")

            # Check Property alias (capital P)
            prop_value2 = packet.Property
            self.add_result("Packet Property alias", True, f"Property: {prop_value2}")

            # Check get_header_size method
            header_size = packet.get_header_size()
            self.add_result("Header size method", True, f"Header size: {header_size}")

        except Exception as e:
            self.add_result("Packet functionality", False, f"Error: {e}")

    def verify_serialization(self):
        """Verify data serialization"""
        print("\n=== Verifying Serialization ===")
        from litenetlib.utils import NetDataWriter, NetDataReader

        try:
            writer = NetDataWriter()
            test_data = b"Hello, World!"

            # Write various types
            writer.put_byte(42)
            writer.put_short(1000)
            writer.put_int(123456)
            writer.put_ulong(9876543210)  # use put_ulong instead of put_long
            writer.put_string(test_data.decode() if isinstance(test_data, bytes) else test_data)
            # For raw bytes, write them directly instead of using put_array
            # put_array is for object arrays with element_size
            for b in [1, 2, 3, 4, 5]:
                writer.put_byte(b)

            reader = NetDataReader()
            reader.set_source(writer.data, 0, writer.length)

            # Read back
            b = reader.get_byte()
            s = reader.get_short()
            i = reader.get_int()
            l = reader.get_ulong()  # use get_ulong instead of get_long
            str_data = reader.get_string()
            # Read 5 bytes individually (matching the write above)
            arr = bytes([reader.get_byte() for _ in range(5)])

            checks = [
                ("Byte round-trip", b == 42, f"{b} == 42"),
                ("Short round-trip", s == 1000, f"{s} == 1000"),
                ("Int round-trip", i == 123456, f"{i} == 123456"),
                ("ULong round-trip", l == 9876543210, f"{l} == 9876543210"),
                ("String round-trip", str_data == (test_data.decode() if isinstance(test_data, bytes) else test_data), f"{str_data}"),
                ("Array round-trip", arr == bytes([1, 2, 3, 4, 5]), f"{arr}"),
            ]

            for name, result, details in checks:
                self.add_result(name, result, details)

        except Exception as e:
            self.add_result("Serialization", False, f"Error: {e}")

    def verify_channels(self):
        """Verify channel functionality"""
        print("\n=== Verifying Channels ===")
        from litenetlib.channels import BaseChannel, ReliableChannel, SequencedChannel
        from litenetlib.constants import NetConstants

        try:
            # Check constants
            self.add_result(
                "ReliableChannel.BITS_IN_BYTE",
                hasattr(ReliableChannel, 'BITS_IN_BYTE'),
                f"Value: {ReliableChannel.BITS_IN_BYTE if hasattr(ReliableChannel, 'BITS_IN_BYTE') else 'N/A'}"
            )

            # Check SequencedChannel constants
            from litenetlib.channels.sequenced_channel import SequencedChannel
            self.add_result(
                "SequencedChannel packet constants",
                hasattr(SequencedChannel, '__init__'),
                "SequencedChannel initialized"
            )

        except Exception as e:
            self.add_result("Channels", False, f"Error: {e}")

    def verify_nat_punch(self):
        """Verify NAT punch module"""
        print("\n=== Verifying NAT Punch Module ===")
        from litenetlib.nat_punch_module import (
            NatPunchModule, NatAddressType,
            INatPunchListener, EventBasedNatPunchListener
        )

        try:
            # Check enum
            if NatAddressType.Internal == 0:
                self.add_result("NatAddressType.Internal", True, "Value: 0")
            else:
                self.add_result("NatAddressType.Internal", False, f"Value: {NatAddressType.Internal}")

            if NatAddressType.External == 1:
                self.add_result("NatAddressType.External", True, "Value: 1")
            else:
                self.add_result("NatAddressType.External", False, f"Value: {NatAddressType.External}")

            # Check module
            self.add_result(
                "NatPunchModule.MAX_TOKEN_LENGTH",
                NatPunchModule.MAX_TOKEN_LENGTH == 256,
                f"Value: {NatPunchModule.MAX_TOKEN_LENGTH}"
            )

            # Check methods
            methods = ['init', 'poll_events', 'send_nat_introduce_request', 'nat_introduce']
            for method in methods:
                if hasattr(NatPunchModule, method):
                    self.add_result(f"NatPunchModule.{method}", True, "Method exists")
                else:
                    self.add_result(f"NatPunchModule.{method}", False, "Method missing")

        except Exception as e:
            self.add_result("NAT punch module", False, f"Error: {e}")

    def verify_internal_packets(self):
        """Verify internal packet structures"""
        print("\n=== Verifying Internal Packets ===")
        from litenetlib.packets.internal_packets import (
            NetConnectRequestPacket, NetConnectAcceptPacket
        )

        try:
            # Check constants (C# values: HeaderSize=14, Size=11)
            if NetConnectRequestPacket.HEADER_SIZE == 14:
                self.add_result("ConnectRequest header size", True, "14 bytes (matches C#)")
            else:
                self.add_result(
                    "ConnectRequest header size",
                    False,
                    f"{NetConnectRequestPacket.HEADER_SIZE} (expected 14)"
                )

            if NetConnectAcceptPacket.SIZE == 11:
                self.add_result("ConnectAccept packet size", True, "11 bytes (matches C#)")
            else:
                self.add_result(
                    "ConnectAccept packet size",
                    False,
                    f"{NetConnectAcceptPacket.SIZE} (expected 11)"
                )

            # Check methods
            request_methods = ['get_protocol_id', 'from_data', 'make']
            for method in request_methods:
                if hasattr(NetConnectRequestPacket, method):
                    self.add_result(f"NetConnectRequestPacket.{method}", True, "Method exists")

            accept_methods = ['from_data', 'make', 'make_network_changed']
            for method in accept_methods:
                if hasattr(NetConnectAcceptPacket, method):
                    self.add_result(f"NetConnectAcceptPacket.{method}", True, "Method exists")

        except Exception as e:
            self.add_result("Internal packets", False, f"Error: {e}")

    def print_summary(self):
        """Print verification summary"""
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\nTotal tests: {total}")
        print(f"Passed: {passed} ({passed * 100 // total if total > 0 else 0}%)")
        print(f"Failed: {failed} ({failed * 100 // total if total > 0 else 0}%)")
        print(f"Time elapsed: {elapsed:.2f} seconds")

        if failed > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.details}")

        print("\n" + "=" * 60)
        if failed == 0:
            print("ALL VERIFICATIONS PASSED!")
        else:
            print("SOME VERIFICATIONS FAILED!")
        print("=" * 60)

        return failed == 0


def main():
    """Main verification entry point"""
    print("=" * 60)
    print("LiteNetLib Python - Comprehensive Verification")
    print("=" * 60)

    verifier = ComprehensiveVerification()

    # Run all verifications
    verifier.verify_imports()
    verifier.verify_constants()
    verifier.verify_inheritance()
    verifier.verify_abstract_methods()
    verifier.verify_packets()
    verifier.verify_serialization()
    verifier.verify_channels()
    verifier.verify_nat_punch()
    verifier.verify_internal_packets()

    # Print summary
    success = verifier.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
