# LiteNetLib Test Suite / LiteNetLib 测试套件

Comprehensive test suite for LiteNetLib-Python-0.9.5.2, ensuring full compatibility with C# v0.9.5.2.

LiteNetLib-Python-0.9.5.2 的全面测试套件，确保与 C# v0.9.5.2 完全兼容。

## Test Files / 测试文件

### 1. test_constants.py - Protocol Constants Tests / 协议常量测试
Tests for all protocol constants and enumerations matching C# v0.9.5.2:
- PROTOCOL_ID = 11
- All PacketProperty enum values (0-17)
- All DeliveryMethod enum values
- MTU options (7 values)
- Header size mappings for all packet types

### 2. test_packet.py - NetPacket Tests / 数据包测试
Tests for NetPacket class functionality:
- Packet creation with size and property
- Property getters/setters (packet_property, connection_number)
- Sequence number operations
- Fragmentation (is_fragmented, fragment_id, fragment_part, fragments_total)
- Channel ID
- Packet verification
- Header size calculation
- NetPacketPool functionality

### 3. test_serialization.py - Serialization Tests / 序列化测试
Tests for DataWriter and DataReader:
- All primitive types (byte, short, int, long, float, double)
- String encoding (UTF-8, empty strings, max length)
- Bytes and arrays
- Special types (UUID, IP endpoints)
- Little-endian byte order verification
- Round-trip consistency

### 4. test_net_utils.py - Network Utils Tests / 网络工具测试
Tests for NetUtils class:
- RelativeSequenceNumber calculations
- Sequence number comparisons
- Time functions (get_time_millis, get_time_ticks)
- Random generation (random_bytes, generate_connect_id)
- Address parsing and formatting

### 5. test_channels.py - Channel Tests / 通道测试
Tests for channel classes:
- BaseChannel basic functionality
- PendingPacket operations
- ReliableChannel (ordered and unordered)
- ACK packet processing
- Sequence number handling
- Window size management

### 6. test_events.py - Event System Tests / 事件系统测试
Tests for event listener classes:
- INetEventListener interface
- EventBasedNetListener callbacks
- ConnectionRequest handling
- DisconnectInfo
- All event types (connect, disconnect, receive, etc.)
- Callback chaining and fluent interface

### 7. test_integration.py - Integration Tests / 集成测试
End-to-end tests requiring actual network:
- Server startup and shutdown
- Client connection flow
- Message sending/receiving
- All 5 delivery methods
- Multiple clients
- Echo server functionality

### 8. test_protocol_compatibility.py - Protocol Compatibility Tests / 协议兼容性测试
Byte-level compatibility verification with C# v0.9.5.2:
- Packet header format
- Sequence number encoding (little-endian)
- Header sizes for all packet properties
- Float/double encoding
- String UTF-8 encoding
- Packet verification logic
- MTU values
- Protocol constants

## Running Tests / 运行测试

### Install pytest / 安装 pytest
```bash
pip install pytest pytest-asyncio
```

### Run all tests / 运行所有测试
```bash
pytest tests/ -v
```

### Run specific test file / 运行特定测试文件
```bash
pytest tests/test_constants.py -v
pytest tests/test_packet.py -v
pytest tests/test_serialization.py -v
pytest tests/test_net_utils.py -v
pytest tests/test_channels.py -v
pytest tests/test_events.py -v
pytest tests/test_protocol_compatibility.py -v
```

### Run integration tests (require network) / 运行集成测试（需要网络）
```bash
pytest tests/test_integration.py -v -m integration
```

### Run with coverage / 运行并生成覆盖率报告
```bash
pip install pytest-cov
pytest tests/ --cov=litenetlib --cov-report=html
```

## Test Organization / 测试组织

Each test file is independent and can be run standalone. Tests are organized by:
- **Class**: Group related tests
- **Function**: Individual test case with descriptive name
- **Assertions**: Clear error messages for debugging
- **Comments**: Bilingual (English/Chinese) for clarity

## C# Compatibility / C# 兼容性

All tests verify compatibility with C# LiteNetLib v0.9.5.2:
- Exact byte-level protocol compatibility
- All enum values match C# definitions
- Header structures match C# memory layout
- Serialization matches C# BinaryWriter/Reader
- Little-endian byte order throughout

## Key Test Areas / 关键测试领域

1. **Constants Matching**: All protocol constants exactly match C# v0.9.5.2
2. **Binary Protocol**: Byte-level verification of packet formats
3. **Serialization**: DataWriter/Reader produce/consume compatible bytes
4. **Edge Cases**: Boundary values, wraparound, invalid data
5. **Integration**: Real network communication where applicable

## Expected Results / 预期结果

All non-integration tests should pass without network dependencies.
Integration tests may be skipped in some environments but demonstrate
real-world interoperability.

## Debugging Failed Tests / 调试失败测试

Run with verbose output and detailed tracebacks:
```bash
pytest tests/test_name.py -v -vv --tb=long
```

Run a specific test:
```bash
pytest tests/test_name.py::TestClass::test_method -v
```

## Contributing / 贡献

When adding new features:
1. Add corresponding tests
2. Verify C# v0.9.5.2 compatibility
3. Include bilingual comments
4. Test edge cases
5. Update this README
