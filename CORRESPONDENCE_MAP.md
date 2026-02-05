# LiteNetLib Python - C# 对应关系映射表

## 概述

本文档记录了LiteNetLib v0.9.5.2从C#到Python的完整对应关系映射。

**C#源目录**: `../LiteNetLib/LiteNetLib/`
**Python目标目录**: `./litenetlib/`

**总文件数**: 27个C#源文件 → 28个Python文件（含__init__.py）

**实现状态统计**:
- ✅ 完整实现: 19个文件
- ⚠️ 存根实现: 4个文件
- ❌ 完全缺失: 4个文件

**代码行数统计**:
- C#总行数: ~7,600行
- Python已完成行数: ~3,100行
- 完成度: ~41%

---

## 快速索引

### 按状态分类

#### ✅ 已完整实现 (19个文件)
1. constants.py (NetConstants.cs) - 118行
2. debug.py (NetDebug.cs) - 151行
3. net_utils.py (NetUtils.cs) - 202行
4. net_socket.py (NativeSocket.cs) - 182行
5. net_statistics.py (NetStatistics.cs) - 134行
6. connection_request.py (ConnectionRequest.cs) - 66行
7. event_interfaces.py (INetEventListener.cs) - 186行
8. packets/net_packet.py (NetPacket.cs) - 282行
9. packets/net_packet_pool.py (PooledPacket.cs) - 85行
10. layers/packet_layer_base.cs (PacketLayerBase.cs) - 36行
11. layers/crc32c_layer.py (Crc32cLayer.cs) - 50行
12. layers/xor_encrypt_layer.py (XorEncryptLayer.cs) - 46行
13. utils/serializable.py (INetSerializable.cs) - 41行
14. utils/fast_bit_converter.py (FastBitConverter.cs) - 121行
15. utils/crc32c.py (CRC32C.cs) - 116行
16. utils/net_data_reader.py (NetDataReader.cs) - 640行
17. utils/net_data_writer.py (NetDataWriter.cs) - 383行
18. net_packet_pool.py (NetPacketPool.cs, LiteNetManager.PacketPool.cs) - 85行
19. net_socket.py (NetSocket.cs, LiteNetManager.Socket.cs) - 182行

#### ⚠️ 存根实现 (4个文件)
1. net_manager.py (NetManager.cs, LiteNetManager.cs) - 161行 (需~2,000行C#翻译)
2. net_peer.py (NetPeer.cs, LiteNetPeer.cs) - 108行 (需~1,500行C#翻译)
3. nat_punch_module.py (NatPunchModule.cs) - 47行 (需264行C#翻译)
4. channels/ - 所有通道文件 (需~450行C#翻译)
   - base_channel.py (BaseChannel.cs) - 50行 (需45行)
   - reliable_channel.py (ReliableChannel.cs) - 44行 (需334行)
   - sequenced_channel.py (SequencedChannel.cs) - 42行 (需114行)

#### ❌ 完全缺失 (4个文件)
1. utils/net_serializer.py (NetSerializer.cs) - 0行 (需770行)
2. utils/net_packet_processor.py (NetPacketProcessor.cs) - 0行 (需288行)
3. utils/ntp_packet.py (NtpPacket.cs) - 0行 (需423行)
4. utils/ntp_request.py (NtpRequest.cs) - 0行 (需42行)

---

## 主目录文件映射（15个C#文件）

### 1. NetConstants.cs → constants.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetConstants.cs |
| **Python文件** | litenetlib/constants.py |
| **C#行数** | 78行 |
| **Python行数** | 118行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public enum DeliveryMethod : byte
public static class NetConstants
```

**Python对应**:
```python
class DeliveryMethod(IntEnum)
class NetConstants
```

**枚举映射**:

| C#枚举 | Python枚举 | 值 | 说明 |
|--------|-----------|-----|------|
| `DeliveryMethod` | `DeliveryMethod` | 5个值 | 传输方式 |

**DeliveryMethod枚举值**:

| C#值 | Python值 | 数值 | 说明 |
|------|---------|-----|------|
| `Unreliable = 4` | `Unreliable = 4` | 4 | 不可靠传输 |
| `ReliableUnordered = 0` | `ReliableUnordered = 0` | 0 | 可靠无序 |
| `Sequenced = 1` | `Sequenced = 1` | 1 | 顺序传输 |
| `ReliableOrdered = 2` | `ReliableOrdered = 2` | 2 | 可靠有序 |
| `ReliableSequenced = 3` | `ReliableSequenced = 3` | 3 | 仅最新可靠 |

**常量映射**:

| C#常量 | Python常量 | 值 | 说明 |
|--------|-----------|-----|------|
| `DefaultWindowSize = 64` | `DefaultWindowSize = 64` | 64 | 默认窗口大小 |
| `SocketBufferSize = 1048576` | `SocketBufferSize = 1048576` | 1MB | Socket缓冲区 |
| `SocketTTL = 255` | `SocketTTL = 255` | 255 | TTL值 |
| `HeaderSize = 1` | `HeaderSize = 1` | 1 | 基础包头 |
| `ChanneledHeaderSize = 4` | `ChanneledHeaderSize = 4` | 4 | 通道包头 |
| `FragmentHeaderSize = 6` | `FragmentHeaderSize = 6` | 6 | 分片包头 |
| `MaxSequence = 32768` | `MaxSequence = 32768` | 32768 | 最大序列号 |
| `ProtocolId = 13` | `ProtocolId = 13` | 13 | 协议ID |
| `MaxConnectionNumber = 4` | `MaxConnectionNumber = 4` | 4 | 最大连接数 |

**说明**: Python实现添加了额外的枚举类型（如PacketProperty, ConnectionState等），这些在C#中位于NetPacket.cs等文件中。

---

### 2. NetDebug.cs → debug.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetDebug.cs |
| **Python文件** | litenetlib/debug.py |
| **C#行数** | 92行 |
| **Python行数** | 151行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public interface INetLogger
public static class NetDebug
```

**Python对应**:
```python
class INetLogger
class NetDebug
```

**方法映射**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public static void WriteError(string str)` | `write_error(message: str)` | 写错误日志 |
| `public static void WriteInfo(string str)` | `write_info(message: str)` | 写信息日志 |
| `public static void WriteWarning(string str)` | `write_warning(message: str)` | 写警告日志 |
| `public static void ForceLog(string msg, ConsoleColor color)` | `force_log(message: str, color: str)` | 强制日志 |

**属性映射**:

| C#属性 | Python属性 | 类型 |
|--------|-----------|------|
| `public static INetLogger Logger` | `logger: INetLogger` | INetLogger |
| `public static bool DeveloperMode` | `developer_mode: bool` | bool |

---

### 3. NetUtils.cs → net_utils.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetUtils.cs |
| **Python文件** | litenetlib/net_utils.py |
| **C#行数** | 234行 |
| **Python行数** | 202行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public static class NetUtils
```

**Python对应**:
```python
class NetUtils
```

**方法映射**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public static IPEndPoint ResolveAddress(string hostStr, int port)` | `resolve_address(host: str, port: int) -> tuple` | 解析地址 |
| `public static IPEndPoint GetLocalIpEndPoint(bool ipv6)` | `get_local_endpoint(ipv6: bool) -> tuple` | 获取本地端点 |
| `public static List<IPEndPoint> GetLocalIpList(LocalAddrType type)` | `get_local_ip_list(addr_type: int) -> list` | 获取本地IP列表 |
| `public static int RelativeSequenceNumber(short number, short expected)` | `relative_sequence_number(number: int, expected: int) -> int` | 相对序列号 |
| `public static int GetDistance(short seqNumber, short expected)` | `get_distance(seq_number: int, expected: int) -> int` | 获取距离 |

---

### 4. NetManager.cs → net_manager.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetManager.cs (314行), LiteNetManager.cs (1,650行) |
| **Python文件** | litenetlib/net_manager.py |
| **C#总行数** | ~1,964行 |
| **Python行数** | 161行 |
| **实现状态** | ⚠️ 存根（需完整实现） |

**C#定义**:
```csharp
public class NetManager
public class LiteNetManager
```

**Python对应**:
```python
class NetManager
```

**关键方法（C# → Python）**:

| C#方法签名 | Python方法签名 | 实现状态 |
|-----------|---------------|----------|
| `public bool Start(int port)` | `start(port: int) -> bool` | ✅ 已实现 |
| `public void Stop()` | `stop() -> None` | ✅ 已实现 |
| `public NetPeer Connect(string host, int port)` | `connect(address: str, port: int) -> Optional[NetPeer]` | ⚠️ 存根 |
| `public void SendToAll(byte[] data, DeliveryMethod options)` | `send_to_all(data: bytes, method: DeliveryMethod) -> None` | ✅ 已实现 |
| `public void Update(int timeStep = 15)` | `update(time_step: int = 15) -> None` | ❌ 缺失 |
| `public NetPeer CreatePeer(IPEndPoint target, string key)` | `_create_peer(target: tuple, key: str) -> NetPeer` | ❌ 缺失 |
| `public void SendUnconnectedMessage(byte[] message, IPEndPoint remoteEndPoint)` | `send_unconnected_message(message: bytes, remote_addr: tuple) -> None` | ❌ 缺失 |
| `public bool DisconnectPeer(NetPeer peer)` | `disconnect_peer(peer: NetPeer) -> bool` | ❌ 缺失 |

**属性映射**:

| C#属性 | Python属性 | 实现状态 |
|--------|-----------|----------|
| `public int ConnectedPeersCount` | `peers_count: int` | ✅ 已实现 |
| `public bool IsRunning` | `is_running: bool` | ✅ 已实现 |
| `public int MaxConnections` | `max_connections: int` | ❌ 缺失 |
| `public bool NATPunchEnabled` | `nat_punch_enabled: bool` | ❌ 缺失 |
| `public bool UnconnectedMessagesEnabled` | `unconnected_messages_enabled: bool` | ❌ 缺失 |
| `public INetEventListener Listener` | `listener: INetEventListener` | ✅ 已实现 |

**待实现功能**:
- Peer生命周期管理
- 事件分发
- Poll/Update循环
- 连接请求处理
- 网络消息处理
- NAT punch模块集成
- 连接状态管理

---

### 5. NetPeer.cs → net_peer.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetPeer.cs (243行), LiteNetPeer.cs (1,288行) |
| **Python文件** | litenetlib/net_peer.py |
| **C#总行数** | ~1,531行 |
| **Python行数** | 108行 |
| **实现状态** | ⚠️ 存根（需完整实现） |

**C#定义**:
```csharp
public class NetPeer
public class LiteNetPeer
```

**Python对应**:
```python
class NetPeer
```

**关键方法（待实现）**:

| C#方法签名 | Python方法签名（待实现） | 说明 |
|-----------|---------------------|------|
| `public void Send(byte[] data, DeliveryMethod options)` | `send(data: bytes, method: DeliveryMethod) -> None` | 发送数据 |
| `public void Disconnect(byte[] data)` | `disconnect(data: bytes = None) -> None` | 断开连接 |
| `public NetStatistics Statistics` | `statistics: NetStatistics` | 统计信息 |
| `public ConnectionState ConnectionState` | `connection_state: ConnectionState` | 连接状态 |
| `public float Ping` | `ping: float` | Ping值 |
| `public int Mtu` | `mtu: int` | MTU值 |
| `public IPEndPoint EndPoint` | `endpoint: tuple` | 远程端点 |

**待实现功能**:
- 连接状态机（连接中、已连接、断开中、已断开）
- 通道初始化和管理
- 分片重组逻辑
- 超时处理
- MTU发现
- ACK/NACK处理
- 可靠窗口管理
- 包序号处理

---

### 6. NetSocket.cs → net_socket.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NativeSocket.cs (173行), LiteNetManager.Socket.cs (727行) |
| **Python文件** | litenetlib/net_socket.py |
| **C#总行数** | ~900行 |
| **Python行数** | 182行 |
| **实现状态** | ✅ 完整（简化版） |

**C#定义**:
```csharp
internal class NativeSocket
internal class NetSocket
```

**Python对应**:
```python
class NetSocket
```

**方法映射**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public bool Start(int port, bool reuseAddress, bool ipv6)` | `start(port: int, reuse_addr: bool, ipv6: bool) -> bool` | 启动Socket |
| `public void Stop()` | `stop() -> None` | 停止Socket |
| `public int SendTo(byte[] data, int offset, int size, IPEndPoint remoteEndPoint)` | `send_to(data: bytes, offset: int, size: int, remote_addr: tuple) -> int` | 发送数据 |
| `public bool Receive()` | `receive() -> bool` | 接收数据 |

**说明**: Python实现使用标准库的socket模块，功能完整但比C#版本更简洁。

---

### 7. NetStatistics.cs → net_statistics.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetStatistics.cs |
| **Python文件** | litenetlib/net_statistics.py |
| **C#行数** | 69行 |
| **Python行数** | 134行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public class NetStatistics
```

**Python对应**:
```python
class NetStatistics
```

**属性映射**:

| C#属性 | Python属性 | 类型 | 说明 |
|--------|-----------|------|------|
| `public long PacketsSent` | `packets_sent` | int | 发送包数 |
| `public long PacketsReceived` | `packets_received` | int | 接收包数 |
| `public long BytesSent` | `bytes_sent` | int | 发送字节数 |
| `public long BytesReceived` | `bytes_received` | int | 接收字节数 |
| `public int PacketLoss` | `packet_loss` | int | 丢包率 |
| `public float RTT` | `rtt` | float | 往返时间 |
| `public float Ping` | `ping` | float | Ping值 |

---

### 8. ConnectionRequest.cs → connection_request.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | ConnectionRequest.cs |
| **Python文件** | litenetlib/connection_request.py |
| **C#行数** | 115行 |
| **Python行数** | 66行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
internal sealed class ConnectionRequest
```

**Python对应**:
```python
class ConnectionRequest
```

**方法映射**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public byte[] Data` | `data: bytes` | 请求数据 |
| `public void Accept()` | `accept() -> None` | 接受连接 |
| `public void Reject(byte[] rejectData)` | `reject(data: bytes = None) -> None` | 拒绝连接 |
| `public IPEndPoint RemoteEndPoint` | `remote_endpoint: tuple` | 远程端点 |

---

### 9. INetEventListener.cs → event_interfaces.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | INetEventListener.cs |
| **Python文件** | litenetlib/event_interfaces.py |
| **C#行数** | 353行 |
| **Python行数** | 186行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public interface INetEventListener
public interface INetLogger
```

**Python对应**:
```python
class INetEventListener
class INetLogger
```

**方法映射（INetEventListener）**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `void OnPeerConnected(NetPeer peer)` | `on_peer_connected(peer: NetPeer) -> None` | 对等体连接 |
| `void OnPeerDisconnected(NetPeer peer, DisconnectInfo disconnectInfo)` | `on_peer_disconnected(peer: NetPeer, info: DisconnectInfo) -> None` | 对等体断开 |
| `void OnNetworkError(IPEndPoint endPoint, SocketError socketError)` | `on_network_error(endpoint: tuple, error: Exception) -> None` | 网络错误 |
| `void OnNetworkReceive(NetPeer peer, NetPacketReader reader, byte channelNumber, DeliveryMethod deliveryMethod)` | `on_network_receive(peer: NetPeer, reader: NetPacketReader, channel: int, method: DeliveryMethod) -> None` | 接收数据 |
| `void OnNetworkReceiveUnconnected(IPEndPoint remoteEndPoint, NetPacketReader reader, UnconnectedMessageType messageType)` | `on_network_receive_unconnected(endpoint: tuple, reader: NetPacketReader, msg_type: int) -> None` | 接收无连接数据 |
| `void OnConnectionRequest(ConnectionRequest request)` | `on_connection_request(request: ConnectionRequest) -> None` | 连接请求 |
| `void OnNetworkLatencyUpdate(NetPeer peer, int latency)` | `on_network_latency_update(peer: NetPeer, latency: int) -> None` | 延迟更新 |

---

### 10. NatPunchModule.cs → nat_punch_module.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NatPunchModule.cs |
| **Python文件** | litenetlib/nat_punch_module.py |
| **C#行数** | 264行 |
| **Python行数** | 47行 |
| **实现状态** | ⚠️ 存根 |

**C#定义**:
```csharp
public class NatPunchModule
```

**Python对应**:
```python
class NatPunchModule
```

**待实现功能**:
- Punch请求/响应
- 引导服务器协议
- 超时处理
- 事件通知
- NAT类型检测

---

### 11. NetPacket.cs → packets/net_packet.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | NetPacket.cs |
| **Python文件** | litenetlib/packets/net_packet.py |
| **C#行数** | 153行 |
| **Python行数** | 282行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
internal enum PacketProperty : byte
internal sealed class NetPacket
```

**Python对应**:
```python
class PacketProperty
class NetPacket
```

**属性映射**:

| C#属性 | Python属性 | 类型 | 说明 |
|--------|-----------|------|------|
| `public PacketProperty Property` | `packet_property` | int | 包属性 |
| `public byte ConnectionNumber` | `connection_number` | int | 连接号 |
| `public ushort Sequence` | `sequence` | int | 序列号 |
| `public bool IsFragmented` | `is_fragmented` | bool | 是否分片 |
| `public byte ChannelId` | `channel_id` | int | 通道ID |
| `public ushort FragmentId` | `fragment_id` | int | 分片ID |
| `public ushort FragmentPart` | `fragment_part` | int | 分片部分 |
| `public ushort FragmentsTotal` | `fragments_total` | int | 总分片数 |

**PacketProperty枚举值**:

| C#值 | Python值 | 数值 | 说明 |
|------|---------|-----|------|
| `Unreliable = 0` | `Unreliable = 0` | 0 | 不可靠 |
| `Channeled = 1` | `Channeled = 1` | 1 | 通道传输 |
| `Ack = 2` | `Ack = 2` | 2 | 确认包 |
| `Ping = 3` | `Ping = 3` | 3 | Ping包 |
| `Pong = 4` | `Pong = 4` | 4 | Pong包 |
| `ConnectRequest = 5` | `ConnectRequest = 5` | 5 | 连接请求 |
| `ConnectAccept = 6` | `ConnectAccept = 6` | 6 | 连接接受 |
| `Disconnect = 7` | `Disconnect = 7` | 7 | 断开连接 |
| `UnconnectedMessage = 8` | `UnconnectedMessage = 8` | 8 | 无连接消息 |
| `MtuCheck = 9` | `MtuCheck = 9` | 9 | MTU检查 |
| `MtuOk = 10` | `MtuOk = 10` | 10 | MTU确认 |
| `Broadcast = 11` | `Broadcast = 11` | 11 | 广播 |
| `Merged = 12` | `Merged = 12` | 12 | 合并包 |
| `ShutdownOk = 13` | `ShutdownOk = 13` | 13 | 关闭确认 |
| `PeerNotFound = 14` | `PeerNotFound = 14` | 14 | 对等体未找到 |
| `InvalidProtocol = 15` | `InvalidProtocol = 15` | 15 | 无效协议 |
| `NatMessage = 16` | `NatMessage = 16` | 16 | NAT消息 |
| `Empty = 17` | `Empty = 17` | 17 | 空包 |

---

### 12. PooledPacket.cs → packets/net_packet_pool.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | PooledPacket.cs (32行), LiteNetManager.PacketPool.cs (82行) |
| **Python文件** | litenetlib/packets/net_packet_pool.py |
| **C#总行数** | ~114行 |
| **Python行数** | 85行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
internal class PooledPacket
internal static class PacketPool
```

**Python对应**:
```python
class NetPacketPool
```

**方法映射**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public static NetPacket GetPacket(int size)` | `get_packet(size: int) -> NetPacket` | 获取包 |
| `public static NetPacket GetPacket(PacketProperty property, int size)` | `get_packet_with_property(property: int, size: int) -> NetPacket` | 获取带属性的包 |
| `public static void Recycle(NetPacket packet)` | `recycle(packet: NetPacket) -> None` | 回收包 |

---

### 13-15. 通道文件映射

#### BaseChannel.cs → channels/base_channel.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | BaseChannel.cs |
| **Python文件** | litenetlib/channels/base_channel.py |
| **C#行数** | 45行 |
| **Python行数** | 50行 |
| **实现状态** | ⚠️ 存根 |

**C#定义**:
```csharp
internal abstract class BaseChannel
```

**Python对应**:
```python
class BaseChannel
```

#### ReliableChannel.cs → channels/reliable_channel.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | ReliableChannel.cs |
| **Python文件** | litenetlib/channels/reliable_channel.py |
| **C#行数** | 334行 |
| **Python行数** | 44行 |
| **实现状态** | ⚠️ 存根 |

**C#定义**:
```csharp
internal sealed class ReliableChannel : BaseChannel
```

**Python对应**:
```python
class ReliableChannel(BaseChannel)
```

**待实现功能**:
- 滑动窗口协议
- 包确认和重传
- 序列号处理
- 超时重传

#### SequencedChannel.cs → channels/sequenced_channel.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | SequencedChannel.cs |
| **Python文件** | litenetlib/channels/sequenced_channel.py |
| **C#行数** | 114行 |
| **Python行数** | 42行 |
| **实现状态** | ⚠️ 存根 |

**C#定义**:
```csharp
internal sealed class SequencedChannel : BaseChannel
```

**Python对应**:
```python
class SequencedChannel(BaseChannel)
```

**待实现功能**:
- 顺序保证
- 丢弃旧包
- 序列号验证

---

## Layers目录映射（3个文件）

### 16. PacketLayerBase.cs → layers/packet_layer_base.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Layers/PacketLayerBase.cs |
| **Python文件** | litenetlib/layers/packet_layer_base.py |
| **C#行数** | 17行 |
| **Python行数** | 36行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public abstract class PacketLayerBase
```

**Python对应**:
```python
class PacketLayerBase
```

### 17. Crc32cLayer.cs → layers/crc32c_layer.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Layers/Crc32cLayer.cs |
| **Python文件** | litenetlib/layers/crc32c_layer.py |
| **C#行数** | 41行 |
| **Python行数** | 50行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public class Crc32cLayer : PacketLayerBase
```

**Python对应**:
```python
class Crc32cLayer(PacketLayerBase)
```

### 18. XorEncryptLayer.cs → layers/xor_encrypt_layer.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Layers/XorEncryptLayer.cs |
| **Python文件** | litenetlib/layers/xor_encrypt_layer.py |
| **C#行数** | 59行 |
| **Python行数** | 46行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public class XorEncryptLayer : PacketLayerBase
```

**Python对应**:
```python
class XorEncryptLayer(PacketLayerBase)
```

---

## Utils目录映射（10个文件）

### 19. CRC32C.cs → utils/crc32c.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/CRC32C.cs |
| **Python文件** | litenetlib/utils/crc32c.py |
| **C#行数** | 150行 |
| **Python行数** | 116行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public static class Crc32C
```

**Python对应**:
```python
class Crc32C
```

### 20. FastBitConverter.cs → utils/fast_bit_converter.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/FastBitConverter.cs |
| **Python文件** | litenetlib/utils/fast_bit_converter.py |
| **C#行数** | 175行 |
| **Python行数** | 121行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
internal static class FastBitConverter
```

**Python对应**:
```python
class FastBitConverter
```

### 21. INetSerializable.cs → utils/serializable.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/INetSerializable.cs |
| **Python文件** | litenetlib/utils/serializable.py |
| **C#行数** | 8行 |
| **Python行数** | 41行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public interface INetSerializable
```

**Python对应**:
```python
class INetSerializable
```

### 22. NetDataReader.cs → utils/net_data_reader.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NetDataReader.cs |
| **Python文件** | litenetlib/utils/net_data_reader.py |
| **C#行数** | 614行 |
| **Python行数** | 640行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public class NetDataReader
```

**Python对应**:
```python
class NetDataReader
```

**方法映射（部分）**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public byte GetByte()` | `get_byte() -> int` | 读取字节 |
| `public short GetShort()` | `get_short() -> int` | 读取短整型 |
| `public int GetInt()` | `get_int() -> int` | 读取整型 |
| `public long GetLong()` | `get_long() -> int` | 读取长整型 |
| `public float GetFloat()` | `get_float() -> float` | 读取浮点数 |
| `public double GetDouble()` | `get_double() -> float` | 读取双精度 |
| `public string GetString()` | `get_string(max_length: int = 0) -> str` | 读取字符串 |
| `public bool GetBool()` | `get_bool() -> bool` | 读取布尔值 |
| `public byte[] GetBytesWithLength()` | `get_bytes_with_length() -> bytes` | 读取带长度字节数组 |

### 23. NetDataWriter.cs → utils/net_data_writer.py

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NetDataWriter.cs |
| **Python文件** | litenetlib/utils/net_data_writer.py |
| **C#行数** | 391行 |
| **Python行数** | 383行 |
| **实现状态** | ✅ 完整 |

**C#定义**:
```csharp
public class NetDataWriter
```

**Python对应**:
```python
class NetDataWriter
```

**方法映射（部分）**:

| C#方法 | Python方法 | 说明 |
|--------|-----------|------|
| `public void Put(byte value)` | `put(value: int)` | 写入字节 |
| `public void Put(short value)` | `put_short(value: int)` | 写入短整型 |
| `public void Put(int value)` | `put_int(value: int)` | 写入整型 |
| `public void Put(long value)` | `put_long(value: int)` | 写入长整型 |
| `public void Put(float value)` | `put_float(value: float)` | 写入浮点数 |
| `public void Put(double value)` | `put_double(value: float)` | 写入双精度 |
| `public void Put(string value)` | `put_string(value: str, max_length: int = 0)` | 写入字符串 |
| `public void Put(bool value)` | `put_bool(value: bool)` | 写入布尔值 |
| `public void PutArray<T>(T[] arr)` | `put_array(arr)` | 写入数组 |

### 24. NetSerializer.cs → utils/net_serializer.py ❌

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NetSerializer.cs |
| **Python文件** | litenetlib/utils/net_serializer.py |
| **C#行数** | 770行 |
| **Python行数** | 0行（未创建） |
| **实现状态** | ❌ 完全缺失 |

**C#定义**:
```csharp
public class InvalidTypeException : ArgumentException
public class ParseException : Exception
public class NetSerializer
```

**需要实现的Python类**:

```python
class InvalidTypeException(Exception)
class ParseException(Exception)
class NetSerializer
```

**关键方法**:

| C#方法 | Python方法（待实现） | 说明 |
|--------|---------------------|------|
| `public void Register<T>()` | `register(cls) -> None` | 注册类型 |
| `public T Deserialize<T>(NetDataReader reader)` | `deserialize(reader, cls) -> Any` | 反序列化 |
| `public void Serialize<T>(NetDataWriter writer, T obj)` | `serialize(writer, obj) -> None` | 序列化 |
| `public byte[] Serialize<T>(T obj)` | `serialize_to_bytes(obj) -> bytes` | 序列化到字节数组 |
| `public void RegisterNestedType<T>()` | `register_nested_type(cls) -> None` | 注册嵌套类型（结构体） |
| `public void RegisterNestedType<T>(Func<T> constructor)` | `register_nested_type_with_constructor(cls, constructor) -> None` | 注册嵌套类型（类） |
| `public void RegisterNestedType<T>(Action<NetDataWriter, T> writer, Func<NetDataReader, T> reader)` | `register_custom_type(cls, writer, reader) -> None` | 注册自定义类型 |

**内部类**（需要实现）:
- `FastCall<T>` - 快速调用基类
- `FastCallSpecific<TClass, TProperty>` - 特定类型序列化
- `IntSerializer<T>`, `UIntSerializer<T>`, `StringSerializer<T>` 等类型序列化器
- `ClassInfo<T>` - 存储类型序列化信息

**支持的类型**:
- 基本类型: int, uint, short, ushort, long, ulong, byte, sbyte, float, double, bool, char
- 字符串: string
- 网络类型: IPEndPoint
- 其他类型: Guid
- 数组和列表: T[], List<T>
- 自定义类型: INetSerializable

### 25. NetPacketProcessor.cs → utils/net_packet_processor.py ❌

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NetPacketProcessor.cs |
| **Python文件** | litenetlib/utils/net_packet_processor.py |
| **C#行数** | 288行 |
| **Python行数** | 0行（未创建） |
| **实现状态** | ❌ 完全缺失 |

**C#定义**:
```csharp
public class NetPacketProcessor
```

**需要实现的Python类**:

```python
class NetPacketProcessor
```

**关键方法**:

| C#方法 | Python方法（待实现） | 说明 |
|--------|---------------------|------|
| `public NetPacketProcessor()` | `__init__()` | 构造函数 |
| `public NetPacketProcessor(int maxStringLength)` | `__init__(max_string_length: int)` | 构造函数（带字符串长度限制） |
| `public void RegisterNestedType<T>()` | `register_nested_type(cls) -> None` | 注册嵌套类型 |
| `public void ReadAllPackets(NetDataReader reader)` | `read_all_packets(reader) -> None` | 读取所有包 |
| `public void ReadAllPackets(NetDataReader reader, object userData)` | `read_all_packets_with_user_data(reader, user_data) -> None` | 读取所有包（带用户数据） |
| `public NetPacket ReadPacket(NetDataReader reader)` | `read_packet(reader) -> NetPacket` | 读取单个包 |
| `public NetPacket ReadPacket(NetDataReader reader, object userData)` | `read_packet_with_user_data(reader, user_data) -> NetPacket` | 读取单个包（带用户数据） |
| `public void Write<T>(NetDataWriter writer, T packet)` | `write(writer, packet) -> None` | 写入包 |
| `public void WriteNetSerializable<T>(NetDataWriter writer, ref T packet)` | `write_net_serializable(writer, packet) -> None` | 写入INetSerializable包 |
| `public void Subscribe<T>(Action<T> onReceive, Func<T> packetConstructor)` | `subscribe(callback, constructor) -> None` | 订阅包类型 |
| `public void Subscribe<T, TUserData>(Action<T, TUserData> onReceive, Func<T> packetConstructor)` | `subscribe_with_user_data(callback, constructor) -> None` | 订阅包类型（带用户数据） |
| `public void SubscribeReusable<T>(Action<T> onReceive)` | `subscribe_reusable(callback) -> None` | 订阅可重用包 |
| `public void SubscribeNetSerializable<T, TUserData>(Action<T, TUserData> onReceive)` | `subscribe_net_serializable(callback) -> None` | 订阅INetSerializable包 |
| `public void RemoveSubscription<T>()` | `remove_subscription(cls) -> None` | 移除订阅 |

**特殊功能**:
- 使用FNV-1a 64位哈希进行类型识别
- 静态`HashCache<T>`用于高效哈希计算
- 支持可重用包实例以减少内存分配
- 用户数据支持用于回调

### 26. NtpPacket.cs → utils/ntp_packet.py ❌

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NtpPacket.cs |
| **Python文件** | litenetlib/utils/ntp_packet.py |
| **C#行数** | 423行 |
| **Python行数** | 0行（未创建） |
| **实现状态** | ❌ 完全缺失 |

**C#定义**:
```csharp
public enum NtpLeapIndicator : byte
public enum NtpMode : byte
public sealed class NtpPacket
```

**需要实现的Python类**:

```python
class NtpLeapIndicator(IntEnum)
class NtpMode(IntEnum)
class NtpPacket
```

**NtpLeapIndicator枚举**:

| C#值 | Python值（待实现） | 数值 | 说明 |
|------|---------------------|-----|------|
| `NoWarning = 0` | `NoWarning = 0` | 0 | 无警告 |
| `LastMinuteHas61Seconds = 1` | `LastMinuteHas61Seconds = 1` | 1 | 最后一分钟有61秒 |
| `LastMinuteHas59Seconds = 2` | `LastMinuteHas59Seconds = 2` | 2 | 最后一分钟有59秒 |
| `AlarmCondition = 3` | `AlarmCondition = 3` | 3 | 告警条件 |

**NtpMode枚举**:

| C#值 | Python值（待实现） | 数值 | 说明 |
|------|---------------------|-----|------|
| `Reserved = 0` | `Reserved = 0` | 0 | 保留 |
| `SymmetricActive = 1` | `SymmetricActive = 1` | 1 | 对称主动 |
| `SymmetricPassive = 2` | `SymmetricPassive = 2` | 2 | 对称被动 |
| `Client = 3` | `Client = 3` | 3 | 客户端 |
| `Server = 4` | `Server = 4` | 4 | 服务器 |
| `Broadcast = 5` | `Broadcast = 5` | 5 | 广播 |
| `ControlMessage = 6` | `ControlMessage = 6` | 6 | 控制消息 |

**NtpPacket关键属性**:

| C#属性 | Python属性（待实现） | 类型 | 说明 |
|--------|---------------------|------|------|
| `public NtpLeapIndicator LeapIndicator` | `leap_indicator` | NtpLeapIndicator | 闰秒指示器 |
| `public byte VersionNumber` | `version_number` | int | 版本号（3或4） |
| `public NtpMode Mode` | `mode` | NtpMode | 模式 |
| `public byte Stratum` | `stratum` | int | 层级（1=主服务器, 2+ = 次服务器） |
| `public TimeSpan PollInterval` | `poll_interval` | float | 轮询间隔（秒） |
| `public TimeSpan Precision` | `precision` | float | 精度（秒） |
| `public TimeSpan RootDelay` | `root_delay` | float | 根延迟（秒） |
| `public TimeSpan RootDispersion` | `root_dispersion` | float | 根离散（秒） |
| `public string ReferenceIdentifier` | `reference_identifier` | str | 参考标识符 |
| `public DateTime ReferenceTimestamp` | `reference_timestamp` | datetime | 参考时间戳 |
| `public DateTime OriginTimestamp` | `origin_timestamp` | datetime | 起始时间戳 |
| `public DateTime ReceiveTimestamp` | `receive_timestamp` | datetime | 接收时间戳 |
| `public DateTime TransmitTimestamp` | `transmit_timestamp` | datetime | 发送时间戳 |
| `public DateTime DestinationTimestamp` | `destination_timestamp` | datetime | 目标时间戳 |
| `public TimeSpan RoundTripTime` | `round_trip_time` | float | 往返时间（计算） |
| `public TimeSpan CorrectionOffset` | `correction_offset` | float | 校正偏移（计算） |

**NtpPacket关键方法**:

| C#方法 | Python方法（待实现） | 说明 |
|--------|---------------------|------|
| `public NtpPacket()` | `__init__()` | 创建客户端请求包 |
| `public NtpPacket(byte[] bytes)` | `from_bytes(data: bytes)` | 从字节数组创建 |
| `public static NtpPacket FromServerResponse(byte[] bytes, DateTime destinationTimestamp)` | `from_server_response(data: bytes, dest_timestamp: datetime)` | 从服务器响应创建 |
| `public byte[] ToBytes()` | `to_bytes() -> bytes` | 转换为字节数组 |
| `public void ValidateRequest()` | `validate_request()` | 验证请求包 |
| `public void ValidateReply()` | `validate_reply()` | 验证响应包 |

**RFC4330 SNTP协议完整实现要求**:
- 网络字节序转换（大端，NTP标准）
- NTP时间戳格式：64位，前32位为秒（从1900-01-01起），后32位为分数
- 时间同步计算
- 有效性验证

### 27. NtpRequest.cs → utils/ntp_request.py ❌

| 属性 | 值 |
|------|-----|
| **C#源文件** | Utils/NtpRequest.cs |
| **Python文件** | litenetlib/utils/ntp_request.py |
| **C#行数** | 42行 |
| **Python行数** | 0行（未创建） |
| **实现状态** | ❌ 完全缺失 |

**C#定义**:
```csharp
internal class NtpRequest
```

**需要实现的Python类**:

```python
class NtpRequest
```

**NtpRequest关键属性**:

| C#属性 | Python属性（待实现） | 类型 | 说明 |
|--------|---------------------|------|------|
| `public IPEndPoint EndPoint` | `endpoint` | tuple | NTP服务器端点 (IP, port) |
| `public bool NeedToKill` | `need_to_kill` | bool | 是否需要终止请求 |

**NtpRequest关键方法**:

| C#方法 | Python方法（待实现） | 说明 |
|--------|---------------------|------|
| `public NtpRequest(IPEndPoint endPoint)` | `__init__(endpoint: tuple)` | 构造函数 |
| `public void Send(Socket socket, float time)` | `send(socket, time: float)` | 发送NTP包 |

**NtpRequest常量**:

| C#常量 | Python常量（待实现） | 值 | 说明 |
|--------|---------------------|-----|------|
| `private const int ResendTimer = 1000` | `RESEND_TIMER = 1000` | 1000ms | 重发定时器 |
| `private const int KillTimer = 10000` | `KILL_TIMER = 10000` | 10000ms | 终止定时器（10秒） |
| `private const int DefaultPort = 123` | `DEFAULT_PORT = 123` | 123 | 默认NTP端口 |

**功能要求**:
- 基于定时器的重发逻辑（每秒重发一次）
- 自动请求过期（10秒后终止）
- 简单的UDP包发送
- 与NtpPacket配合使用

---

## 实现优先级路线图

### 🔴 高优先级（核心功能，阻塞其他功能）

1. **utils/net_serializer.py** (770行C#)
   - 序列化系统核心
   - 被NetPacketProcessor依赖
   - 提供对象自动序列化

2. **utils/net_packet_processor.py** (288行C#)
   - 包处理和分发核心
   - 类型安全的包处理器
   - FNV-1a哈希实现

3. **net_manager.py** (完整实现)
   - 当前只有存根
   - 需要~1,964行C#翻译
   - 连接管理、事件分发核心

4. **net_peer.py** (完整实现)
   - 当前只有存根
   - 需要~1,531行C#翻译
   - Peer状态机、通道管理

### 🟡 中优先级（重要功能，增强可用性）

5. **channels/reliable_channel.py** (完整实现)
   - 当前只有存根
   - 需要334行C#翻译
   - 可靠传输核心

6. **channels/sequenced_channel.py** (完整实现)
   - 当前只有存根
   - 需要114行C#翻译
   - 顺序传输

7. **utils/ntp_packet.py** (423行C#)
   - 时间同步支持
   - RFC4330 SNTP协议

8. **utils/ntp_request.py** (42行C#)
   - NTP请求管理
   - 与NtpPacket配合

9. **nat_punch_module.py** (完整实现)
   - 当前只有存根
   - 需要264行C#翻译
   - NAT穿透功能

### 🟢 低优先级（辅助功能，不影响基本使用）

10. **源代码注释增强**
    - 所有文件的详细C#对应注释
    - 文档字符串完善

---

## 实现注意事项

### 二进制兼容性

所有实现必须保持与C#的精确二进制兼容性：

#### 字节序
- **大部分数据**: 小端字节序（`<` in struct, C#默认）
- **NTP包**: 网络字节序/大端（`>` in struct, NTP标准）
- **网络传输**: 大端（IP端点等）

#### 数据类型映射

| C#类型 | Python类型 | 字节数 | struct格式 |
|--------|-----------|--------|-----------|
| `byte` | `int` | 1 | `B` |
| `sbyte` | `int` | 1 | `b` |
| `short` / `Int16` | `int` | 2 | `<h` |
| `ushort` / `UInt16` | `int` | 2 | `<H` |
| `int` / `Int32` | `int` | 4 | `<i` |
| `uint` / `UInt32` | `int` | 4 | `<I` |
| `long` / `Int64` | `int` | 8 | `<q` |
| `ulong` / `UInt64` | `int` | 8 | `<Q` |
| `float` / `Single` | `float` | 4 | `<f` |
| `double` | `float` | 8 | `<d` |
| `bool` | `bool` | 1 | `?` |
| `char` | `str` | 2 | `<H` |
| `string` | `str` | 变长 | UTF-8 |
| `byte[]` | `bytes` | 变长 | - |
| `DateTime` | `datetime` | 8 | 64位时间戳 |

#### 特殊数据结构

- **IPEndPoint**: `(str, int)` 元组
- **Guid**: `uuid.UUID` 或16字节
- **NTP时间戳**: 64位（前32位秒，后32位分数）

#### 字符串编码
- **编码**: UTF-8
- **长度前缀**: ushort (2字节)

#### CRC32C
- **算法**: 必须与C#实现完全一致
- **查找表**: 与C#相同的生成多项式

### 性能考虑

1. **对象池**: NetPacketPool减少GC压力
   - 使用`threading.Lock`确保线程安全
   - 支持批量回收

2. **反射**: NetSerializer使用反射
   - Python的`getattr`/`setattr`替代C#委托
   - 考虑使用`__slots__`优化内存

3. **哈希**: NetPacketProcessor的FNV-1a
   ```python
   def fnv1a_64(data: bytes) -> int:
       hash_val = 14695981039346656037  # offset basis
       for b in data:
           hash_val ^= b
           hash_val *= 1099511628211  # FNV prime
           hash_val &= 0xFFFFFFFFFFFFFFFF  # 保持64位
       return hash_val
   ```

4. **线程安全**:
   - 使用`threading.Lock`
   - 尽量减少锁持有时间

### Python与C#的差异处理

#### 1. 反射与委托

**C#**:
```csharp
Func<TClass, TProperty> getter = (Func<TClass, TProperty>)Delegate.CreateDelegate(...);
```

**Python**:
```python
# 使用getattr/setattr
value = getattr(obj, property_name)
setattr(obj, property_name, value)
```

#### 2. 泛型

**C#**:
```csharp
public void Register<T>()
```

**Python**:
```python
def register(self, cls: type) -> None:
    ...
```

#### 3. 结构体与类

**C#**:
```csharp
where T : struct, INetSerializable  // 值类型
where T : class, INetSerializable  // 引用类型
```

**Python**:
```python
# Python没有这种区分
# 需要在文档中说明或使用isinstance检查
```

#### 4. 枚举底层类型

**C#**:
```csharp
enum DeliveryMethod : byte  // 指定底层类型
```

**Python**:
```python
class DeliveryMethod(IntEnum):
    Unreliable = 4  # 自动适配大小
```

#### 5. 可空类型

**C#**:
```csharp
DateTime? destinationTimestamp  // 可空
```

**Python**:
```python
destination_timestamp: Optional[datetime] = None
```

---

## 测试策略

### 单元测试

每个新文件都需要单元测试：

```python
# tests/test_net_serializer.py
def test_serialize_basic_types():
    """测试基本类型序列化"""

def test_serialize_arrays():
    """测试数组序列化"""

def test_serialize_custom_types():
    """测试自定义类型序列化"""

# tests/test_net_packet_processor.py
def test_subscribe_and_process():
    """测试订阅和包处理"""

def test_fnv1a_hash():
    """测试FNV-1a哈希一致性"""

# tests/test_ntp.py
def test_ntp_packet_creation():
    """测试NTP包创建"""

def test_ntp_time_conversion():
    """测试NTP时间转换"""
```

### 集成测试

```python
# tests/test_integration.py
def test_python_csharp_serialization():
    """测试Python序列化的数据能被C#反序列化"""

def test_full_network_cycle():
    """测试完整的网络通信周期"""
```

### 互通测试

```python
# interop_tests/test_protocol_compatibility.py
def test_packet_format():
    """测试包格式一致"""

def test_serialization_compatibility():
    """测试序列化兼容性"""

def test_crc32c_compatibility():
    """测试CRC32C计算一致"""
```

---

## 代码示例：完整的C#对应注释

### 文件头注释

```python
"""
NetPacket.cs 翻译

网络数据包结构，包含包头、属性、序列号、分片信息等。

C#源文件: NetPacket.cs
C#行数: ~153行
实现状态: ✓完整
最后更新: 2025-02-05
说明:
    - 完整实现了C#版本的所有功能
    - 包括分片支持
    - 包头属性解析完全兼容
    - 字节序使用小端（与C#一致）
"""
```

### 类注释

```python
class NetPacket:
    """
    网络数据包

    C#定义: internal sealed class NetPacket
    C#源位置: NetPacket.cs:28-153

    属性:
        raw_data: bytearray - 原始包数据
        size: int - 包大小
        user_data: object - 用户数据（可选）
        next: NetPacket - 对象池链表指针

    方法:
        get_header_size() -> int - 获取包头大小
        verify() -> bool - 验证包完整性
        mark_fragmented() -> None - 标记为分片包

    说明:
        - 使用对象池模式减少内存分配
        - 支持多种包属性类型
        - 支持分片传输
    """
```

### 枚举注释

```python
class PacketProperty(IntEnum):
    """
    数据包属性类型

    C#定义: internal enum PacketProperty : byte
    C#源位置: NetPacket.cs:6-26

    说明:
        包属性编码在包头的第一个字节中，使用5位（0-4位）存储。
        连接号使用2位（5-6位），分片标志使用1位（7位）。
    """
    Unreliable = 0         # C#值: 0 - 不可靠传输
    Channeled = 1          # C#值: 1 - 通道传输（需要ACK）
    Ack = 2                # C#值: 2 - 确认包
    Ping = 3               # C#值: 3 - Ping包
    Pong = 4               # C#值: 4 - Pong包
    # ... 其他值
```

### 方法注释

```python
def verify(self) -> bool:
    """
    验证包完整性

    C#方法: public bool Verify()
    C#源位置: NetPacket.cs:145-167
    线程安全: No
    异常: 无

    返回:
        bool: 包是否有效
            C#对应: bool

    说明:
        检查以下内容：
        1. 包属性值是否在有效范围内（0-17）
        2. 包大小是否至少包含包头
        3. 如果是分片包，是否有完整的分片头

    示例:
        >>> packet = NetPacket(100, PacketProperty.Channeled)
        >>> assert packet.verify() == True
    """
```

### 属性注释

```python
@property
def packet_property(self) -> int:
    """
    获取包属性

    C#属性: public PacketProperty Property { get; set; }
    C#源位置: NetPacket.cs:67-71

    返回:
        int: 包属性类型（PacketProperty枚举值）
            C#对应: PacketProperty

    说明:
        从包头第一个字节的低5位提取包属性。
        使用位操作：raw_data[0] & 0x1F
    """
    return self._raw_data[0] & 0x1F
```

---

## 文献参考

- **C#源代码**: `../LiteNetLib/LiteNetLib/`
- **LiteNetLib GitHub**: https://github.com/RevenantX/LiteNetLib
- **RFC4330**: SNTP协议规范 (https://tools.ietf.org/html/rfc4330)
- **FNV-1a哈希**: http://www.isthe.com/chongo/tech/comp/fnv/

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2025-02-05 | 初始版本，完整的对应关系映射 |

---

## 贡献指南

如果您想参与实现缺失的文件，请：

1. 阅读对应的C#源代码
2. 按照本文档的注释标准编写Python代码
3. 确保二进制兼容性
4. 添加单元测试
5. 更新此文档的状态

---

*本文档由LiteNetLib Python项目自动生成*
*最后更新: 2025-02-05*
