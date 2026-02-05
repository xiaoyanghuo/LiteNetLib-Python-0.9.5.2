# 精确实施计划 - 基于详细的C#对比

**基于**: 逐文件C# vs Python详细对比
**日期**: 2025-02-05
**状态**: Round 1 - 重新分析

---

## 执行摘要

通过逐文件详细对比，发现实际缺失情况：

| 类别 | C#文件 | 缺失行数 | 当前Python | 状态 |
|------|--------|---------|-----------|------|
| **核心管理器** | LiteNetManager.cs | ~1,651 | 不存在 | ❌ 100%缺失 |
| **核心Peer** | LiteNetPeer.cs | ~1,500 | 不存在 | ❌ 100%缺失 |
| **事件系统** | NetEvent.cs | ~150 | 不存在 | ❌ 100%缺失 |
| **内部包** | InternalPackets.cs | ~200 | 部分常量 | ⚠️ 90%缺失 |
| **可靠通道** | ReliableChannel.cs | ~290 | 45行 | ⚠️ 87%缺失 |
| **序列通道** | SequencedChannel.cs | ~70 | 43行 | ⚠️ 61%缺失 |
| **基础通道** | BaseChannel.cs | ~15 | 51行 | ⚠️ 33%缺失 |
| **NAT穿透** | NatPunchModule.cs | ~180 | 50行 | ⚠️ 90%缺失 |
| **NetManager** | NetManager.cs | ~150 | 162行 | ⚠️ 50%缺失（缺少基类功能）|
| **NetPeer** | NetPeer.cs | ~200 | 109行 | ⚠️ 82%缺失（缺少基类功能）|

**总计缺失**: 约 **4,406行** 核心功能代码

---

## 详细实施计划

### 阶段 1: 基础架构（必须首先实现）

#### 1.1 创建NetEvent系统 ⚠️ **CRITICAL PATH**
**文件**: `litenetlib/net_event.py`
**C#源**: `NetEvent.cs` (~150行)
**优先级**: 🔴 HIGHEST - 事件系统是所有其他组件的基础

**必须实现的类和结构**:
```python
class NetEventType(IntEnum):
    Connect = 0
    Disconnect = 1
    Receive = 2
    ReceiveUnconnected = 3
    Broadcast = 4
    Error = 5
    ConnectionLatencyUpdated = 6
    ConnectionRequest = 7
    MessageDelivered = 8
    PeerAddressChanged = 9

class NetEvent:
    # 字段（全部来自C#源）:
    - Type: NetEventType
    - Peer: LiteNetPeer
    - DataReader: NetDataReader
    - ConnectionRequest: ConnectionRequest
    - RemoteEndPoint: tuple
    - DisconnectReason: int
    - ErrorCode: SocketError
    - ChannelNumber: byte
    - DeliveryMethod: DeliveryMethod
    - Latency: int
    - UserData: object

    # 方法:
    + Recycle()
```

**为什么必须首先实现**: NetManager和NetPeer的所有方法都依赖NetEvent

---

#### 1.2 创建LiteNetPeer基类 ⚠️ **CRITICAL PATH**
**文件**: `litenetlib/lite_net_peer.py`
**C#源**: `LiteNetPeer.cs` (~1,500行)
**优先级**: 🔴 HIGHEST - 所有Peer功能的基类

**必须实现的枚举**:
```python
class ConnectionState(IntEnum):
    Outgoing = 0
    Connected = 1
    Shutdown = 2
    Disconnected = 3

class ConnectRequestResult(IntEnum):
    Ok = 0
    PeerNotFound = 1
    ConnectionClose = 2
    P2PLose = 3

class DisconnectResult(IntEnum):
    Ok = 0
    PeerNotFound = 1
    ConnectionClose = 2
    Reconnect = 3
    RejectNewConnection = 4
    MaxConnectionReached = 5
    UnknownPeer = 6

class ShutdownResult(IntEnum):
    Ok = 0
    PeerNotFound = 1
    ConnectionClose = 2
    Reconnect = 3
    UnknownPeer = 4
    Success
```

**必须实现的方法**（从C#源逐个列出）:

```python
class LiteNetPeer:
    # 构造函数 (3个重载):
    + __init__(manager: LiteNetManager, remoteEndPoint: tuple, id: int)
    + __init__(manager: LiteNetManager, remoteEndPoint: tuple, id: int, connectNum: byte, connectData: bytes)
    + __init__(manager: LiteNetManager, request: ConnectionRequest, id: int)

    # 连接管理 (9个方法):
    + Connect() -> ConnectRequestResult
    + Reject(force: bool) -> DisconnectResult
    + Disconnect(reason: byte, data: bytes = None) -> ShutdownResult
    + Shutdown(reason: byte, data: bytes = None) -> ShutdownResult

    # 发送方法 (5个重载):
    + Send(data: bytes, channelNumber: byte, deliveryMethod: DeliveryMethod)
    + Send(writer: NetDataWriter, channelNumber: byte, deliveryMethod: DeliveryMethod)
    + SendWithDeliveryEvent(...)  # 4个重载

    # 包处理 (6个方法):
    + ProcessPacket(packet: NetPacket)
    + ProcessChanneled(packet: NetPacket)  # 抽象方法
    + AddToReliableChannelSendQueue(channel: BaseChannel)
    + CreateChannel(idx: byte) -> BaseChannel  # 抽象方法

    # 通道管理 (3个方法):
    + UpdateChannels()  # 抽象方法
    + GetPacketsCountInReliableQueue(channelNumber: byte, ordered: bool) -> int

    # 工具方法 (12个方法):
    + CreateEvent() -> NetEvent
    + RecycleEvent(evt: NetEvent)
    + SendUserData(packet: NetPacket)
    + RecycleAndDeliver(packet: NetPacket)
    + InvalidatePacket()
    + ResetMtu()
    + MergeNextPacket()
    + GetMtu() -> int
    + SetMtu(mtu: int)
    + GetRoundTripTime() -> int
    + GetRemoteEndPoint() -> tuple
    + FinishEndPointChange(newEndPoint: tuple)

    # 属性 (20个属性):
    + NetManager -> LiteNetManager
    + Id -> int
    + ConnectionState -> ConnectionState
    + IsRunning -> bool
    + Mtu -> int
    + Ping -> int
    + Rtt -> int
    + ResendDelay -> float
    + Current_MTU -> int
    + RemoteEndPoint -> tuple
    + Address -> str
    + Port -> int
    + Statistics -> NetStatistics
    + ConnectTime -> datetime
    + BytesReceived -> long
    + BytesSent -> long
    + PacketsReceived -> int
    + PacketsSent -> int
    + LossPercent -> float
    + IsDuplicateRequired -> bool
```

**为什么必须首先实现**: NetManager依赖它，所有通道功能由它管理

---

#### 1.3 创建LiteNetManager基类 ⚠️ **CRITICAL PATH**
**文件**: `litenetlib/lite_net_manager.py`
**C#源**: `LiteNetManager.cs` (1,651行)
**优先级**: 🔴 HIGHEST - NetManager继承自它

**必须实现的内部类**:
```python
class IPv6Mode(IntEnum):
    Disabled = 0
    SeparateSocket = 1
    DualMode = 2

class NetEvent:
    # 事件池管理
    + GetEvent() -> NetEvent
    + RecycleEvent(evt: NetEvent)

class PacketPool:
    # 包池管理
    + GetPacket(size: int) -> NetPacket
    + Recycle(packet: NetPacket)
```

**必须实现的方法**（从C#源）:

```python
class LiteNetManager:
    # 启动/停止 (4个方法):
    + Start(port: int) -> bool
    + Start(address: str, port: int) -> bool
    + Stop(disconnectPeers: bool)
    + Stop()

    # 连接管理 (8个方法):
    + Connect(host: str, port: int, key: str) -> LiteNetPeer
    + Connect(host: str, port: int, key: str, data: bytes) -> LiteNetPeer
    + Connect(target: tuple, key: str) -> LiteNetPeer
    + Connect(target: tuple, key: str, data: bytes) -> LiteNetPeer
    + DisconnectAll()
    + DisconnectAll(force: bool)
    + DisconnectPeer(peer: LiteNetPeer, data: bytes = None)
    + GetPeerById(id: int) -> LiteNetPeer

    # 发送 (4个方法):
    + SendToAll(data: bytes, options: DeliveryMethod)
    + SendToAll(writer: NetDataWriter, options: DeliveryMethod)
    + SendUnconnectedMessage(data: bytes, address: tuple)
    + SendBroadcast(address: str, port: int, data: bytes)

    # 查询 (6个属性):
    + ConnectedPeersCount -> int
    + MaxConnections -> int
    + IsRunning -> bool
    + LocalPort -> int
    + IPv6Enabled -> IPv6Mode
    + Listener -> INetEventListener

    # 抽象方法（子类实现）:
    + CreateOutgoingPeer(remoteEndPoint: tuple, id: int, connectNum: byte, connectData: bytes) -> LiteNetPeer
    + CreateIncomingPeer(request: ConnectionRequest, id: int) -> LiteNetPeer
    + CreateRejectPeer(remoteEndPoint: tuple, id: int) -> LiteNetPeer
    + ProcessEvent(evt: NetEvent)
    + CustomMessageHandle(packet: NetPacket, remoteEndPoint: tuple) -> bool
```

**为什么必须首先实现**: NetManager继承它，所有网络管理功能的基础

---

### 阶段 2: 通道系统

#### 2.1 完善BaseChannel (33% → 100%)
**缺失**: ~15行
**必须添加**:
```python
class BaseChannel:
    + AddToPeerChannelSendQueue()
    + SendAndCheckQueue() -> bool
    - _isAddedToPeerChannelSendQueue: int
```

---

#### 2.2 完整实现ReliableChannel (13% → 100%)
**缺失**: ~290行
**必须添加**:

```python
class PendingPacket:
    """内部结构 - 可靠包的重发状态"""
    - _packet: NetPacket
    - _timeStamp: long
    - _isSent: bool

    + Init(packet: NetPacket)
    + TrySend(currentTime: long, peer: LiteNetPeer) -> bool
    + Clear(peer: LiteNetPeer) -> bool

class ReliableChannel(BaseChannel):
    # 字段 (13个):
    - _outgoingAcks: NetPacket
    - _pendingPackets: PendingPacket[]
    - _receivedPackets: NetPacket[]
    - _earlyReceived: bool[]
    - _localSequence: int
    - _remoteSequence: int
    - _localWindowStart: int
    - _remoteWindowStart: int
    - _mustSendAcks: bool
    - _deliveryMethod: DeliveryMethod
    - _ordered: bool
    - _windowSize: int
    - _id: byte

    # 方法 (4个):
    + SendNextPackets() -> bool
    + ProcessPacket(packet: NetPacket) -> bool
    - ProcessAck(packet: NetPacket)
```

---

#### 2.3 完整实现SequencedChannel (38% → 100%)
**缺失**: ~70行
**必须添加**:

```python
class SequencedChannel(BaseChannel):
    # 字段 (8个):
    - _localSequence: int
    - _remoteSequence: ushort
    - _reliable: bool
    - _lastPacket: NetPacket
    - _ackPacket: NetPacket
    - _mustSendAck: bool
    - _id: byte
    - _lastPacketSendTime: long

    # 方法 (2个):
    + SendNextPackets() -> bool
    + ProcessPacket(packet: NetPacket) -> bool
```

---

### 阶段 3: NetManager和NetPeer增强

#### 3.1 增强NetManager (50% → 100%)
**基于**: 现有net_manager.py (162行) + 继承LiteNetManager
**必须添加**: ~150行

```python
class NetManager(LiteNetManager):
    # 字段 (3个):
    - _netEventListener: INetEventListener
    - _channelsCount: byte
    - _ntpRequests: Dict[tuple, NtpRequest]

    # 属性 (1个):
    + ChannelsCount -> byte

    # NTP方法 (3个):
    + CreateNtpRequest(endPoint: tuple)
    + CreateNtpRequest(address: str, port: int)
    + CreateNtpRequest(address: str)

    # 重写方法 (6个):
    + CreateOutgoingPeer(...) -> LiteNetPeer
    + CreateIncomingPeer(...) -> LiteNetPeer
    + CreateRejectPeer(...) -> LiteNetPeer
    + ProcessEvent(evt: NetEvent)
    + CustomMessageHandle(packet: NetPacket, remoteEndPoint: tuple) -> bool
    + ProcessNtpRequests(elapsedMilliseconds: float)
```

---

#### 3.2 增强NetPeer (8% → 100%)
**基于**: 现有net_peer.py (109行) + 继承LiteNetPeer
**必须添加**: ~200行

```python
class NetPeer(LiteNetPeer):
    # 字段 (2个):
    - _channelSendQueue: Queue[BaseChannel]
    - _channels: BaseChannel[]

    # 属性 (1个):
    + ChannelsCount -> int  # override

    # Send方法 (7个重载):
    + Send(data: bytes, channelNumber: byte, deliveryMethod: DeliveryMethod)
    + Send(writer: NetDataWriter, channelNumber: byte, deliveryMethod: DeliveryMethod)
    + SendWithDeliveryEvent(...)  # 4个重载

    # 其他方法 (5个):
    + CreatePacketFromPool(deliveryMethod: DeliveryMethod, channelNumber: byte) -> PooledPacket
    + GetPacketsCountInReliableQueue(channelNumber: byte, ordered: bool) -> int
    + UpdateChannels()
    + ProcessChanneled(packet: NetPacket)
    + AddToReliableChannelSendQueue(channel: BaseChannel)
    + CreateChannel(idx: byte) -> BaseChannel
```

---

### 阶段 4: 辅助功能

#### 4.1 InternalPackets (90%缺失)
**文件**: `litenetlib/internal_packets.py`
**C#源**: `InternalPackets.cs` (~200行)
**必须添加**:
```python
class ConnectRequestPacket:
    # 连接请求包结构
    + Structure

class ConnectAcceptPacket:
    # 连接接受包结构
    + Structure

class DisconnectPacket:
    # 断开连接包结构
    + Structure

# 其他内部包类型...
```

---

#### 4.2 NatPunchModule增强 (10% → 100%)
**必须添加**: ~180行
完整的NAT穿透协议实现

---

#### 4.3 NetUtils增强 (33% → 100%)
**必须添加**: ~100行
- 地址解析方法
- Socket工具方法
- 网络辅助方法

---

## 实施顺序（严格依赖关系）

### Round 2: 基础架构
1. **Day 1**: NetEvent系统 (150行) - 🔴 CRITICAL
2. **Day 2-3**: LiteNetPeer基类 (1,500行) - 🔴 CRITICAL
3. **Day 4-5**: LiteNetManager基类 (1,651行) - 🔴 CRITICAL

### Round 3: 通道系统
4. **Day 6**: BaseChannel增强 (15行)
5. **Day 7-8**: ReliableChannel完整实现 (290行)
6. **Day 9**: SequencedChannel完整实现 (70行)

### Round 4: 增强和集成
7. **Day 10**: NetManager增强 (150行)
8. **Day 11-12**: NetPeer增强 (200行)
9. **Day 13**: InternalPackets (200行)
10. **Day 14**: NatPunchModule增强 (180行)
11. **Day 15**: NetUtils和其他增强 (100行)

---

## 测试验证点

每个组件完成后立即验证：

### 阶段1测试:
- [ ] NetEvent创建和回收
- [ ] LiteNetPeer基本功能
- [ ] LiteNetManager启动/停止

### 阶段2测试:
- [ ] ReliableChannel ACK处理
- [ ] SequencedChannel顺序保证
- [ ] 通道集成测试

### 阶段3测试:
- [ ] NetManager完整生命周期
- [ ] NetPeer发送/接收
- [ ] 端到端连接测试

---

## 成功标准

### Round 2 完成标准:
- ✅ NetEvent系统完全可用
- ✅ LiteNetPeer所有方法实现
- ✅ LiteNetManager所有方法实现
- ✅ 所有单元测试通过

### Round 3 完成标准:
- ✅ ReliableChannel可靠交付
- ✅ SequencedChannel顺序保证
- ✅ 通道集成测试通过

### Round 4 完成标准:
- ✅ NetManager完整功能
- ✅ NetPeer完整功能
- ✅ 端到端集成测试通过
- ✅ 与C#版本协议兼容

---

**总计**: 约 **4,406行** 需要实现
**预计时间**: 15个工作日
**下一里程碑**: Round 2 - 完成NetEvent + LiteNetPeer + LiteNetManager

**当前状态**: 准备开始Round 2 - 基础架构实施
