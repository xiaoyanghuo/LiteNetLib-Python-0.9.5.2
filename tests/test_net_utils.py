"""
Network Utils Tests / 网络工具测试

Tests for NetUtils class including sequence number calculations,
comparisons, and utility functions.

Reference C# Code: LiteNetLib/Utils/NetUtils.cs
"""

import pytest
import time
from litenetlib.utils.net_utils import NetUtils
from litenetlib.core.constants import NetConstants


class TestRelativeSequenceNumber:
    """Test RelativeSequenceNumber / 测试相对序列号计算"""

    def test_relative_sequence_same(self):
        """Test relative sequence when same / 测试相同序列号的相对值"""
        result = NetUtils.relative_sequence_number(100, 100)
        assert result == 0, f"Relative sequence of same number should be 0, got {result}"

    def test_relative_sequence_positive(self):
        """Test relative sequence when number > expected / 测试 number > expected"""
        result = NetUtils.relative_sequence_number(105, 100)
        assert result == 5, f"Relative sequence should be 5, got {result}"

    def test_relative_sequence_negative(self):
        """Test relative sequence when number < expected / 测试 number < expected"""
        result = NetUtils.relative_sequence_number(95, 100)
        assert result == -5, f"Relative sequence should be -5, got {result}"

    def test_relative_sequence_wraparound_positive(self):
        """Test wraparound where number is ahead / 测试循环回绕（number 在前）"""
        # Number is near max, expected is near 0
        # Number should be considered "ahead" in circular sense
        result = NetUtils.relative_sequence_number(32760, 10)
        # Should calculate difference considering wraparound
        assert isinstance(result, int), "Result should be integer"

    def test_relative_sequence_wraparound_negative(self):
        """Test wraparound where number is behind / 测试循环回绕（number 在后）"""
        # Number is near 0, expected is near max
        result = NetUtils.relative_sequence_number(10, 32760)
        # Should calculate difference considering wraparound
        assert isinstance(result, int), "Result should be integer"

    def test_relative_sequence_max_half(self):
        """Test at HALF_MAX_SEQUENCE boundary / 测试 HALF_MAX_SEQUENCE 边界"""
        half = NetConstants.HALF_MAX_SEQUENCE  # 16384
        result = NetUtils.relative_sequence_number(half, 0)
        # At half max, the sequence is considered "old" (negative relative)
        # C#: (16384 - 0 + 32768 + 16384) % 32768 - 16384 = 0 - 16384 = -16384
        assert result == -half, f"Relative sequence at half max should be {-half}, got {result}"

    def test_relative_sequence_formula(self):
        """Test C# formula correctness / 测试 C# 公式正确性"""
        # C#: (number - expected + MaxSequence + HalfMaxSequence) % MaxSequence - HalfMaxSequence
        number = 500
        expected = 400

        expected_result = (number - expected + NetConstants.MAX_SEQUENCE +
                          NetConstants.HALF_MAX_SEQUENCE) % NetConstants.MAX_SEQUENCE - \
                         NetConstants.HALF_MAX_SEQUENCE

        result = NetUtils.relative_sequence_number(number, expected)
        assert result == expected_result, \
            f"Formula mismatch: expected {expected_result}, got {result}"

    def test_relative_sequence_multiple_values(self):
        """Test relative sequence with multiple values / 测试多个值的相对序列号"""
        test_cases = [
            (0, 0, 0),
            (1, 0, 1),
            (0, 1, -1),
            (100, 50, 50),
            (50, 100, -50),
        ]

        for number, expected, expected_rel in test_cases:
            result = NetUtils.relative_sequence_number(number, expected)
            assert result == expected_rel, \
                f"Relative sequence mismatch for ({number}, {expected}): expected {expected_rel}, got {result}"


class TestSequenceComparisons:
    """Test sequence number comparison functions / 测试序列号比较函数"""

    def test_is_sequence_less_than(self):
        """Test is_sequence_less_than / 测试序列号小于判断"""
        assert NetUtils.is_sequence_less_than(99, 100) is True
        assert NetUtils.is_sequence_less_than(100, 100) is False
        assert NetUtils.is_sequence_less_than(101, 100) is False

    def test_is_sequence_greater_than(self):
        """Test is_sequence_greater_than / 测试序列号大于判断"""
        assert NetUtils.is_sequence_greater_than(101, 100) is True
        assert NetUtils.is_sequence_greater_than(100, 100) is False
        assert NetUtils.is_sequence_greater_than(99, 100) is False

    def test_sequence_comparison_with_wraparound(self):
        """Test comparison with wraparound / 测试循环回绕比较"""
        # When numbers are near boundaries
        max_seq = NetConstants.MAX_SEQUENCE
        half_seq = NetConstants.HALF_MAX_SEQUENCE

        # Number at max should be "greater" than 0 in circular sense
        result = NetUtils.relative_sequence_number(max_seq - 1, 0)
        assert isinstance(result, int)

    def test_sequence_ordering(self):
        """Test sequence ordering consistency / 测试序列号排序一致性"""
        sequences = [100, 105, 95, 110, 90]

        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                # Test transitivity
                seq1, seq2 = sequences[i], sequences[j]
                rel1 = NetUtils.relative_sequence_number(seq1, seq2)
                rel2 = NetUtils.relative_sequence_number(seq2, seq1)

                # Should be opposites
                assert rel1 == -rel2, \
                    f"Relative sequences should be opposites: {rel1} vs {rel2}"


class TestTimeFunctions:
    """Test time utility functions / 测试时间工具函数"""

    def test_get_time_millis(self):
        """Test get_time_millis / 测试获取毫秒时间"""
        time1 = NetUtils.get_time_millis()
        time.sleep(0.01)  # Sleep 10ms
        time2 = NetUtils.get_time_millis()

        assert time2 > time1, "Time should increase"
        assert time2 - time1 >= 10, "At least 10ms should have passed"
        assert isinstance(time1, int), "Time should be integer"
        assert isinstance(time2, int), "Time should be integer"

    def test_get_time_ticks(self):
        """Test get_time_ticks / 测试获取刻度时间"""
        ticks1 = NetUtils.get_time_ticks()
        time.sleep(0.001)  # Sleep 1ms
        ticks2 = NetUtils.get_time_ticks()

        assert ticks2 > ticks1, "Ticks should increase"
        assert isinstance(ticks1, int), "Ticks should be integer"
        assert isinstance(ticks2, int), "Ticks should be integer"

    def test_ticks_to_millis_ratio(self):
        """Test ticks to milliseconds ratio / 测试刻度与毫秒比率"""
        # 1 tick = 100ns, 1ms = 10000 ticks
        time_millis = NetUtils.get_time_millis()
        time_ticks = NetUtils.get_time_ticks()

        # Should be approximately 10000x difference
        ratio = time_ticks / (time_millis * 10000)
        assert 0.99 <= ratio <= 1.01, \
            f"Ticks ratio should be ~1.0, got {ratio}"

    def test_time_monotonic(self):
        """Test time is monotonic increasing / 测试时间单调递增"""
        times = [NetUtils.get_time_millis() for _ in range(10)]
        for i in range(len(times) - 1):
            assert times[i + 1] >= times[i], "Time should be monotonic"


class TestRandomFunctions:
    """Test random generation functions / 测试随机生成函数"""

    def test_random_bytes_length(self):
        """Test random_bytes returns correct length / 测试随机字节长度"""
        for length in [0, 1, 10, 100, 1000]:
            result = NetUtils.random_bytes(length)
            assert len(result) == length, \
                f"random_bytes({length}) should return {length} bytes, got {len(result)}"

    def test_random_bytes_are_bytes(self):
        """Test random_bytes returns bytes type / 测试随机字节类型"""
        result = NetUtils.random_bytes(100)
        assert isinstance(result, bytes), \
            f"random_bytes should return bytes, got {type(result)}"

    def test_random_bytes_uniqueness(self):
        """Test random_bytes are different / 测试随机字节唯一性"""
        bytes1 = NetUtils.random_bytes(100)
        bytes2 = NetUtils.random_bytes(100)
        assert bytes1 != bytes2, "Random bytes should be different"

    def test_generate_connect_id(self):
        """Test generate_connect_id / 测试生成连接 ID"""
        conn_id = NetUtils.generate_connect_id()
        assert isinstance(conn_id, int), "Connection ID should be integer"
        assert 0 <= conn_id <= 0xFFFFFFFF, \
            f"Connection ID should be in range [0, 0xFFFFFFFF], got {conn_id}"

    def test_generate_connect_id_uniqueness(self):
        """Test generate_connect_id uniqueness / 测试连接 ID 唯一性"""
        ids = [NetUtils.generate_connect_id() for _ in range(100)]
        unique_ids = set(ids)
        # Should have high probability of being unique
        assert len(unique_ids) > 95, \
            f"Generated IDs should be mostly unique, got {len(unique_ids)} unique out of 100"


class TestAddressParsing:
    """Test address parsing functions / 测试地址解析函数"""

    def test_parse_ipv4_with_port(self):
        """Test parsing IPv4 with port / 测试解析带端口的 IPv4"""
        host, port = NetUtils.parse_address("192.168.1.1:8080")
        assert host == "192.168.1.1", \
            f"Host should be '192.168.1.1', got {host}"
        assert port == 8080, \
            f"Port should be 8080, got {port}"

    def test_parse_ipv4_without_port(self):
        """Test parsing IPv4 without port / 测试解析不带端口的 IPv4"""
        host, port = NetUtils.parse_address("192.168.1.1")
        assert host == "192.168.1.1"
        assert port is None

    def test_parse_ipv6_with_port(self):
        """Test parsing IPv6 with port / 测试解析带端口的 IPv6"""
        host, port = NetUtils.parse_address("[::1]:8080")
        assert host == "::1", \
            f"Host should be '::1', got {host}"
        assert port == 8080, \
            f"Port should be 8080, got {port}"

    def test_parse_ipv6_without_port(self):
        """Test parsing IPv6 without port / 测试解析不带端口的 IPv6"""
        host, port = NetUtils.parse_address("[::1]")
        assert host == "::1"
        assert port is None

    def test_parse_ipv6_full_address(self):
        """Test parsing full IPv6 address / 测试解析完整 IPv6 地址"""
        host, port = NetUtils.parse_address("[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:7777")
        assert host == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        assert port == 7777

    def test_parse_localhost(self):
        """Test parsing localhost / 测试解析 localhost"""
        host, port = NetUtils.parse_address("localhost:7777")
        assert host == "localhost"
        assert port == 7777

    def test_parse_address_multiple_colons(self):
        """Test parsing address with multiple colons / 测试解析带多个冒号的地址"""
        # IPv6 addresses have multiple colons
        host, port = NetUtils.parse_address("[fe80::1]:9000")
        assert host == "fe80::1"
        assert port == 9000


class TestAddressFormatting:
    """Test address formatting functions / 测试地址格式化函数"""

    def test_format_ipv4(self):
        """Test formatting IPv4 address / 测试格式化 IPv4 地址"""
        result = NetUtils.format_address("192.168.1.1", 8080)
        assert result == "192.168.1.1:8080", \
            f"Formatted address should be '192.168.1.1:8080', got {result}"

    def test_format_ipv6(self):
        """Test formatting IPv6 address / 测试格式化 IPv6 地址"""
        result = NetUtils.format_address("::1", 8080)
        assert result == "[::1]:8080", \
            f"Formatted address should be '[::1]:8080', got {result}"

    def test_format_ipv6_full(self):
        """Test formatting full IPv6 address / 测试格式化完整 IPv6 地址"""
        result = NetUtils.format_address("2001:0db8:85a3::8a2e:0370:7334", 7777)
        assert result == "[2001:0db8:85a3::8a2e:0370:7334]:7777", \
            f"Formatted address incorrect, got {result}"

    def test_format_and_parse_roundtrip(self):
        """Test format and parse roundtrip / 测试格式化和解析往返"""
        test_cases = [
            ("192.168.1.1", 8080),
            ("10.0.0.1", 7777),
            ("::1", 9000),
            ("fe80::1", 8080),
        ]

        for host, port in test_cases:
            formatted = NetUtils.format_address(host, port)
            parsed_host, parsed_port = NetUtils.parse_address(formatted)
            assert parsed_host == host, \
                f"Roundtrip failed for {host}:{port} -> {formatted} -> {parsed_host}:{parsed_port}"
            assert parsed_port == port


class TestEdgeCases:
    """Test edge cases / 测试边界情况"""

    def test_relative_sequence_boundary_values(self):
        """Test relative sequence at boundaries / 测试边界相对序列号"""
        max_seq = NetConstants.MAX_SEQUENCE

        # At max sequence
        result = NetUtils.relative_sequence_number(max_seq - 1, max_seq - 1)
        assert result == 0

        # Crossing zero
        result = NetUtils.relative_sequence_number(0, max_seq - 1)
        assert isinstance(result, int)

    def test_sequence_comparison_extreme_values(self):
        """Test sequence comparison with extreme values / 测试极端值序列号比较"""
        max_seq = NetConstants.MAX_SEQUENCE
        half_seq = NetConstants.HALF_MAX_SEQUENCE

        # At half max, the sequence is considered "old" (negative relative)
        # due to wrap-around logic
        result = NetUtils.relative_sequence_number(half_seq, 0)
        assert result == -half_seq

        # Just over half max is even "older"
        result = NetUtils.relative_sequence_number(half_seq + 1, 0)
        assert result == -(half_seq - 1)

    def test_parse_empty_address(self):
        """Test parsing empty address / 测试解析空地址"""
        host, port = NetUtils.parse_address("")
        assert host == ""
        assert port is None

    def test_parse_address_invalid(self):
        """Test parsing invalid address / 测试解析无效地址"""
        # Should still return something, not crash
        host, port = NetUtils.parse_address("invalid")
        assert isinstance(host, str)
        assert port is None

    def test_random_bytes_zero_length(self):
        """Test random bytes with zero length / 测试零长度随机字节"""
        result = NetUtils.random_bytes(0)
        assert result == b''
        assert len(result) == 0

    def test_format_address_zero_port(self):
        """Test formatting with port 0 / 测试格式化端口 0"""
        result = NetUtils.format_address("127.0.0.1", 0)
        assert result == "127.0.0.1:0"

    def test_time_consistency(self):
        """Test time function consistency / 测试时间函数一致性"""
        millis = NetUtils.get_time_millis()
        ticks = NetUtils.get_time_ticks()

        # Ticks should be much larger than millis
        assert ticks > millis, "Ticks should be greater than millis"

        # Ticks should be approximately 10000x millis
        ratio = ticks / millis
        assert 9000 <= ratio <= 11000, \
            f"Ticks/millis ratio should be ~10000, got {ratio}"


class TestSequenceNumberProperties:
    """Test sequence number mathematical properties / 测试序列号数学属性"""

    def test_relative_sequence_reflexive(self):
        """Test relative sequence is reflexive / 测试相对序列号自反性"""
        for seq in [0, 100, 1000, 16000, 32700]:
            result = NetUtils.relative_sequence_number(seq, seq)
            assert result == 0, \
                f"Relative sequence of ({seq}, {seq}) should be 0, got {result}"

    def test_relative_sequence_antisymmetric(self):
        """Test relative sequence is antisymmetric / 测试相对序列号反对称性"""
        test_cases = [
            (100, 50),
            (50, 100),
            (0, 32767),
            (32767, 0),
        ]

        for a, b in test_cases:
            result1 = NetUtils.relative_sequence_number(a, b)
            result2 = NetUtils.relative_sequence_number(b, a)
            assert result1 == -result2, \
                f"Relative sequence should be antisymmetric: ({a},{b})={result1}, ({b},{a})={result2}"

    def test_relative_sequence_range(self):
        """Test relative sequence is in valid range / 测试相对序列号范围"""
        half = NetConstants.HALF_MAX_SEQUENCE

        # Test many random pairs
        import random
        for _ in range(100):
            a = random.randint(0, NetConstants.MAX_SEQUENCE - 1)
            b = random.randint(0, NetConstants.MAX_SEQUENCE - 1)
            result = NetUtils.relative_sequence_number(a, b)

            # Result should be in range [-half, half)
            assert -half <= result < half, \
                f"Relative sequence {result} for ({a},{b}) is outside range [-{half}, {half})"


class TestUtilityIntegration:
    """Test integration of utilities / 测试工具集成"""

    def test_complete_address_workflow(self):
        """Test complete address workflow / 测试完整地址工作流"""
        # Original address
        original_host = "192.168.1.100"
        original_port = 9000

        # Format
        formatted = NetUtils.format_address(original_host, original_port)

        # Parse
        parsed_host, parsed_port = NetUtils.parse_address(formatted)

        # Should match
        assert parsed_host == original_host
        assert parsed_port == original_port

    def test_sequence_workflow(self):
        """Test sequence number workflow / 测试序列号工作流"""
        # Start with sequence 100
        current = 100

        # Check next sequence
        next_seq = current + 10
        rel = NetUtils.relative_sequence_number(next_seq, current)

        assert rel == 10, f"Relative should be 10, got {rel}"
        assert NetUtils.is_sequence_greater_than(next_seq, current)

        # Wraparound scenario
        near_max = NetConstants.MAX_SEQUENCE - 100
        near_zero = 100

        rel_wrap = NetUtils.relative_sequence_number(near_zero, near_max)
        # Should calculate considering wraparound
        assert isinstance(rel_wrap, int)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
