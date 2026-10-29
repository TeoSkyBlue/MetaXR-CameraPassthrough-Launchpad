
//Writing code top level like this is not allowed in Unity. Will need to alter later.
using System.Net.Sockets;

TcpClient client = new TcpClient();
await client.ConnectAsync("", 5000);

NetworkStream stream = client.GetStream();

