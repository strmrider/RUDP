import socket
from .sock import Socket
from ..models.packet import Packet, generate_id
from ..session.cltsess import ClientSession
from ..models.constants import SYN, SYN_ACK, SYN_TIMEOUT, SYN_ATTEMPTS

class ReliableSocket:
    """
    Client side reliable UDP socket
    """
    def __init__(self, ip, port):
        """
        :param ip: Host's IP address
        :param port: Host's port number
        """
        self.socket = Socket()
        self.address = (ip, port)
        self.syn_attempts = SYN_ATTEMPTS
        self.syn_timeout = SYN_TIMEOUT
        self.session = None

    def connect(self):
        """
        Connect to server
        """
        if self.session:
            raise Exception('Connection Error: session is already established')

        # client's initial sequence number
        initial_seq_number = generate_id()
        syn_packet = Packet(seq=initial_seq_number, oper=SYN)
        self.socket.send(self.address, bytes(syn_packet))
        self.socket.set_timeout(self.syn_timeout)
        attempts = 0
        while attempts < self.syn_attempts:
            try:
                attempts += 1
                packet, address = self.socket.read_packet()
                if packet.operation == SYN_ACK:
                    self.socket.send(self.address, bytes(packet.ack()))
                    self.socket.set_timeout(None)
                    self.session = ClientSession(self.address, initial_seq_number, packet.seq_number, self.socket)
                    print ('Connection established')
                    break
            except socket.timeout as e:
                if attempts >= self.syn_attempts:
                    raise Exception('Connection failure: timeout error')

    def close(self):
        """
        Closes session
        """
        if not self.session:
            raise Exception('Close connection failure: no session is established')
        self.session.close()
        self.session = None

    def receive(self, buffer):
        """
        Returns data from server
        :param buffer: Data's length
        """
        if not self.session:
            raise Exception("Data transfer failure: connection is closed or not established")
        return self.session.receive(buffer)

    def send(self, data):
        """
        Sends data to server
        :param data: (str or bytes) data to send
        """
        if not self.session:
            raise Exception("Data transfer failure: connection is closed or not established")
        self.session.send(data)

