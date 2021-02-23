# RUDP
Reliable User Datagram Protocol (UDP). The protocol implements more complex functions than the primitive basic UDP (but still not as heavy as TCP)

## Features
* Verifies reception of packets.
* Retransmission of lost packets.
* In order packets reception.
* Safe session establishment and closing.
* Multi-client server sockets
* Costumized settings (timeouts, packet retransmissionm and packets size)

Using TCP concepts such as sequnece numbers, packstes acknowledgement and 3-way handshake.

## Examples

```Python
IP = '127.0.0.1'
PORT = 55265

```

Server

```Python
from .src.sockets.server import ReliableServer

server = ReliableServer(IP, PORT)
server.listen()
print ('listening...')
# accept new connections
while True:
  new_session = server.accept()
  print ("new session started")
  msg = session.receive(1024)
  print (msg)
  session.send('message received')
```

```Python
from src.sockets.client import ReliableSocket

sock = ReliableSocket(IP, PORT)
sock.connect()
print ("session started")
msg = 'new message from client'
sock.send(msg)
response = sock.receive(1024)
print (response)
```

Server output
```
listening...
new session started
new message from client
```

Client output
```
session started
message received
```
## API
**`ReliableServer(ip, port)`**
* **`listen()`**
* **`accept()`**

  Accept a session with a client (similar to the TCP socket, just connectionless). Returns a conenction with a client as *ClientConnection* object, usable to send and receive data on the connection.
  
* **`shutdown()`**

**ClientConnection** - returns from server's *accept* method
* **`send(data)`**
* **`receive(buffer)`**
* **`close()`**

**`ReliableSocket(ip, port)`**
* **`connect()`**
* **`send(data)`**
* **`receive(buffer)`**
* **`close()`**

