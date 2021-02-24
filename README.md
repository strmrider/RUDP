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
Client
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

  Creates a server binded to given ip address and port.
  
* **`listen()`**

  listen to income clients.
  
* **`accept()`**

  Accept a session with a client (similar to the TCP socket, just connectionless). Returns a conenction with a client as *ClientConnection* object, usable to send and receive data on the connection.
  
* **`shutdown()`**

  Shuts down the server. Active sessions should be closed in advanced to avoid socket exception.
  
**ClientConnection** - returns from server's *accept* method
* **`send(data)`**

  Sends data to clients.
  
* **`receive(buffer)`**

  Receives data from clients.
  
* **`close()`**

  Close connection.

**`ReliableSocket(ip, port)`**

  Creates a client sokcet. Receives target server ip address and port number.
  
* **`connect()`**

  Connect to the server.

* **`send(data)`**

  Sends data to server.

* **`receive(buffer)`**

  Receives data from Server.
  
* **`close()`**

  Close session with server.

