using System;
using System.Text;
using System.Threading;
using LiteNetLib;
using LiteNetLib.Utils;

namespace CSharpServer
{
    class Program
    {
        static EventBasedNetListener listener = new EventBasedNetListener();
        static NetManager server = null;
        static NetPeer clientPeer = null;

        static void Main(string[] args)
        {
            Console.WriteLine("=== LiteNetLib C# Server v0.9.5.2 ===");
            Console.WriteLine("等待 Python 客户端连接...\n");

            listener.ConnectionRequestEvent += request =>
            {
                Console.WriteLine($"[C#] 收到连接请求: {request.RemoteEndPoint}");
                request.AcceptIfKey("test_connection");
            };

            listener.PeerConnectedEvent += peer =>
            {
                Console.WriteLine($"[C#] 客户端已连接: {peer.EndPoint}");
                clientPeer = peer;

                // 发送测试消息
                Thread.Sleep(500);
                SendTestMessages(peer);
            };

            listener.PeerDisconnectedEvent += (peer, disconnectInfo) =>
            {
                Console.WriteLine($"[C#] 客户端断开: {disconnectInfo.Reason}");
                clientPeer = null;
            };

            listener.NetworkReceiveEvent += (peer, reader, channelNumber, deliveryMethod) =>
            {
                try
                {
                    byte messageType = reader.GetByte();
                    switch (messageType)
                    {
                        case 1: // String message
                            string msg = reader.GetString();
                            Console.WriteLine($"[C#] 收到字符串: {msg}");
                            break;

                        case 2: // Integer array
                            int count = reader.GetInt();
                            int[] numbers = new int[count];
                            for (int i = 0; i < count; i++)
                            {
                                numbers[i] = reader.GetInt();
                            }
                            Console.WriteLine($"[C#] 收到整数数组 ({count} 个): [{string.Join(", ", numbers)}]");
                            break;

                        case 3: // Large data
                            int size = reader.GetInt();
                            byte[] data = reader.GetBytesWithLength();
                            Console.WriteLine($"[C#] 收到大块数据: {data.Length} 字节");
                            break;

                        case 4: // Test result
                            bool passed = reader.GetBool();
                            string testName = reader.GetString();
                            Console.WriteLine($"[C#] 测试结果: {(passed ? "✅ 通过" : "❌ 失败")} - {testName}");
                            break;

                        default:
                            Console.WriteLine($"[C#] 未知消息类型: {messageType}");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[C#] 处理消息错误: {ex.Message}");
                }
            };

            listener.NetworkReceiveUnconnectedEvent += (point, reader, messageType) =>
            {
                Console.WriteLine($"[C#] 收到非连接消息");
            };

            listener.NetworkLatencyUpdateEvent += (peer, latency) =>
            {
                // Console.WriteLine($"[C#] 延迟更新: {latency}ms");
            };

            server = new NetManager(listener, 0, "test_key")
            {
                AutoRecycle = true,
                UpdateTime = 15,
                DisconnectTimeout = 5000,
                UseSafeMtu = true
            };

            if (!server.Start(9050))
            {
                Console.WriteLine("[C#] 服务器启动失败！");
                return;
            }

            Console.WriteLine("[C#] 服务器已启动，监听端口 9050");
            Console.WriteLine("[C#] 按 ENTER 退出...\n");

            while (true)
            {
                server.BroadcastPoll();
                Thread.Sleep(15);

                if (Console.KeyAvailable && Console.ReadKey(true).Key == ConsoleKey.Enter)
                    break;
            }

            server.Stop();
            Console.WriteLine("[C#] 服务器已停止");
        }

        static void SendTestMessages(NetPeer peer)
        {
            Console.WriteLine("\n[C#] === 开始发送测试消息 ===\n");

            // 1. Unreliable 消息
            var writer = new NetDataWriter();
            writer.Put((byte)10); // Message type: Test start
            peer.Send(writer, DeliveryMethod.Unreliable);
            Console.WriteLine("[C#] 发送: Unreliable 消息");

            // 2. 字符串消息 (ReliableOrdered)
            writer.Reset();
            writer.Put((byte)1);
            writer.Put("Hello from C# Server!");
            peer.Send(writer, DeliveryMethod.ReliableOrdered);
            Console.WriteLine("[C#] 发送: ReliableOrdered 字符串");

            // 3. 整数数组 (ReliableUnordered)
            writer.Reset();
            writer.Put((byte)2);
            writer.Put(5);
            writer.Put(100);
            writer.Put(200);
            writer.Put(300);
            writer.Put(400);
            writer.Put(500);
            peer.Send(writer, DeliveryMethod.ReliableUnordered);
            Console.WriteLine("[C#] 发送: ReliableUnordered 整数数组");

            // 4. 大块数据 (测试分片)
            writer.Reset();
            writer.Put((byte)3);
            var largeData = new byte[20000];
            for (int i = 0; i < largeData.Length; i++)
                largeData[i] = (byte)(i % 256);
            writer.Put(largeData.Length);
            writer.PutBytesWithLength(largeData);
            peer.Send(writer, DeliveryMethod.ReliableOrdered);
            Console.WriteLine("[C#] 发送: 20000 字节大数据（测试分片）");

            // 5. Sequenced 消息
            for (int i = 1; i <= 3; i++)
            {
                writer.Reset();
                writer.Put((byte)1);
                writer.Put($"Sequenced message {i} from C#");
                peer.Send(writer, DeliveryMethod.Sequenced);
            }
            Console.WriteLine("[C#] 发送: 3 个 Sequenced 消息");

            // 6. ReliableSequenced 消息
            for (int i = 1; i <= 3; i++)
            {
                writer.Reset();
                writer.Put((byte)1);
                writer.Put($"ReliableSequenced message {i} from C#");
                peer.Send(writer, DeliveryMethod.ReliableSequenced);
            }
            Console.WriteLine("[C#] 发送: 3 个 ReliableSequenced 消息");

            Console.WriteLine("\n[C#] === 测试消息发送完成 ===\n");
        }
    }
}
