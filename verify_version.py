# -*- coding: utf-8 -*-
"""
Verify LiteNetLib v0.9.5.2 Python implementation
验证 LiteNetLib v0.9.5.2 Python 实现
"""

import sys
sys.path.insert(0, '.')

from litenetlib.core.constants import PacketProperty, NetConstants, DeliveryMethod

def verify_constants():
    """Verify critical constants match v0.9.5.2 / 验证关键常量匹配 v0.9.5.2"""
    print("=" * 60)
    print("LiteNetLib v0.9.5.2 Python Implementation Verification")
    print("LiteNetLib v0.9.5.2 Python implementation verification")
    print("=" * 60)

    # Check PROTOCOL_ID
    print("\n[OK] Protocol ID:")
    print(f"    PROTOCOL_ID = {NetConstants.PROTOCOL_ID}")
    assert NetConstants.PROTOCOL_ID == 11, "PROTOCOL_ID must be 11 for v0.9.5.2"
    print("    [OK] Correct (v0.9.5.2 uses 11, not 13)")

    # Check PacketProperty values
    print("\n[OK] PacketProperty enum values:")
    critical_props = {
        'ACK': 2,
        'EMPTY': 17,
        'MERGED': 12,
    }

    for name, expected_value in critical_props.items():
        actual_value = PacketProperty[name].value
        print(f"    {name} = {actual_value}")
        assert actual_value == expected_value, f"{name} must be {expected_value}"
        print(f"    [OK] Correct")

    # Check total count
    total_props = len(PacketProperty)
    print(f"\n    Total PacketProperty count: {total_props}")
    assert total_props == 18, "v0.9.5.2 should have 18 packet properties"
    print("    [OK] Correct (18 types, not 19)")

    # Check DeliveryMethod
    print("\n[OK] DeliveryMethod enum:")
    delivery_methods = {
        'UNRELIABLE': 4,
        'RELIABLE_UNORDERED': 0,
        'SEQUENCED': 1,
        'RELIABLE_ORDERED': 2,
        'RELIABLE_SEQUENCED': 3,
    }

    for name, expected_value in delivery_methods.items():
        actual_value = DeliveryMethod[name].value
        print(f"    {name} = {actual_value}")
        assert actual_value == expected_value, f"{name} must be {expected_value}"

    print("    [OK] All correct")

    # Check MTU options
    print("\n[OK] MTU options:")
    print(f"    Possible MTU count: {len(NetConstants.POSSIBLE_MTU)}")
    print(f"    MTU values: {NetConstants.POSSIBLE_MTU}")
    assert len(NetConstants.POSSIBLE_MTU) == 7, "v0.9.5.2 has 7 MTU options"
    print("    [OK] Correct (7 options)")

    print("\n" + "=" * 60)
    print("[OK] ALL CHECKS PASSED!")
    print("[OK] All checks passed!")
    print("=" * 60)
    print("\nThis implementation is correctly configured for v0.9.5.2")
    print("Key differences from v2.0.0:")
    print("  * PROTOCOL_ID = 11 (not 13)")
    print("  * ACK = 2 (not 3)")
    print("  * EMPTY = 17 (not 18)")
    print("  * No ReliableMerged packet type")
    print("  * 18 packet types (not 19)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        verify_constants()
    except AssertionError as e:
        print(f"\n[ERROR]: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
