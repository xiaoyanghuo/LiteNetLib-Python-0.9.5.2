using System;
using System.Text;
using System.Threading;
using LiteNetLib;
using LiteNetLib.Utils;

namespace CSharpClient
{
    class Program
    {
        static EventBasedNetListener listener = new EventBasedNetListener();
        static NetManager client = null;
        static NetPeer serverPeer = null;

        static void Main(string[] args)
        {
            Console.WriteLine("=== LiteNetLib C# Client v0.9.5.2 ===");
            Console.WriteLine("连接到 Python 服务器 (127.0.0.1:9051)...\n");

            listener.NetworkReceiveEvent += (peer, reader, channelNumber, deliveryMethod) =>
            {
                try
                {
                    byte messageType = reader.GetByte();
                    switch (messageType)
                    {
                        case 1: // String message
                            string msg = reader.GetString();
                            Console.WriteLine($"[C#] 收到字符串 ({deliveryMethod}): {msg}");
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

                        case 10: // Test start
                            Console.WriteLine("[C#] 收到测试开始信号");
                            Thread.Sleep(500);
                            SendTestMessages(peer);
                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[C#] 处理消息错误: {ex.Message}");
                }
            };

            listener.PeerConnectedEvent += peer =>
            {
                Console.WriteLine($"[C#] ✅ 已连接到 Python 服务器");
                serverPeer = peer;
            };

            listener.PeerDisconnectedEvent += (peer, disconnectInfo) =>
            {
                Console.WriteLine($"[C#] 断开连接: {disconnectInfo.Reason}");
                serverPeer = null;
            };

            client = new NetManager(listener, 1, "test_key")
            {
                AutoRecycle = true,
                UpdateTime = 15,
                DisconnectTimeout = 5000,
                UseSafeMtu = true
            };

            serverPeer = client.Connect("127.0.0.1", 9051, "test_connection");

            Console.WriteLine("[C#] 正在连接...");
            Console.WriteLine("[C#] 按 ENTER 退出...\n");

            while (true)
            {
                client.Poll();
                Thread.Sleep(15);

                if (Console.KeyAvailable && Console.ReadKey(true).Key == ConsoleKey.Enter)
                    break;

                if (serverPeer == null || serverPeer.ConnectionState == ConnectionState.Disconnected)
                    break;
            }

            client.Stop();
            Console.WriteLine("[C#] 客户端已停止");
        }

        static void SendTestMessages(NetPeer peer)
        {
            Console.WriteLine("\n[C#] === 开始发送测试消息 ===\n");

            // 1. Unreliable 消息
            var writer = new NetDataWriter();
            writer.Put((byte)1);
            writer.Put("Hello from C# Client!");
            peer.Send(writer, DeliveryMethod.Unreliable);
            Console.WriteLine("[C#] 发送: Unreliable 字符串");

            Thread.Sleep(100);

            // 2. ReliableOrdered 消息
            writer.Reset();
            writer.Put((byte)1);
            writer.Put("C# 客户端消息 - 中文测试！");
            peer.Send(writer, DeliveryMethod.ReliableOrdered);
            Console.WriteLine("[C#] 发送: ReliableOrdered UTF-8 字符串");

            Thread.Sleep(100);

            // 3. 整数数组
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

            Thread.Sleep(100);

            // 4. Sequenced 消息
            for (int i = 1; i <= 3; i++)
            {
                writer.Reset();
                writer.Put((byte)1);
                writer.Put($"Sequenced {i} from C#");
                peer.Send(writer, DeliveryMethod.Sequenced);
            }
            Console.WriteLine("[C#] 发送: 3 个 Sequenced 消息");

            Thread.Sleep(100);

            // 5. ReliableSequenced 消息
            for (int i = 1; i <= 3; i++)
            {
                writer.Reset();
                writer.Put((byte)1);
                writer.Put($"ReliableSequenced {i} from C#");
                peer.Send(writer, DeliveryMethod.ReliableSequenced);
            }
            Console.WriteLine("[C#] 发送: 3 个 ReliableSequenced 消息");

            Console.WriteLine("\n[C#] === 测试消息发送完成 ===\n");
        }
    }
}
