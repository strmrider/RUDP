import queue, threading
from ..models.packet import generate_id
from .sock import Socket
from ..models.event import EventEmitter
from ..session.srvsess import ClientConnection
from ..models.constants import PAYLOAD, FIN, FIN_ACK, SYN, ACK

class ReliableServer:
    """
    Reliable UDP server
    """
    def __init__(self, ip, port):
        """
        :param ip: Host's IP address
        :param port: Host's port number
        """
        self.socket = Socket()
        self.socket.bind(ip, port)
        self.awaiting_connections = {}
        self.available_sessions = queue.Queue()
        self.income_packet_emitter = EventEmitter()
        self.acceptors = 0

        self.run = False

    def listen(self):
        """
        Starts a thread for listening
        """
        if not self.run:
            t = threading.Thread(target=self.__listen, args=())
            t.start()

    def __listen(self):
        """
        Listen to income clients
        """
        self.run = True
        while self.run:
            self.socket.select()
            if self.socket.is_readable():
                packet, address = self.socket.read_packet()
                if packet.operation == PAYLOAD or packet.operation == FIN or packet.operation == FIN_ACK:
                    self.income_packet_emitter.emit(address=address[1], pkt=packet)
                elif packet.operation == SYN:
                    self.__handle_syn(address, packet)
                elif packet.operation == ACK:
                    self.__handle_ack(address, packet)

    def __handle_syn(self, address, packet):
        """
        Handles SYN request
        :param address: Client's address
        :param packet: SYN packet
        """
        if self.acceptors <= 0:
            return

        # Session's initial sequence number
        initial_seq_number = generate_id()
        new_session = ClientConnection(address, initial_seq_number, packet.seq_number, self.income_packet_emitter)
        self.awaiting_connections[address[1]] = new_session
        syn_ack = packet.ack(initial_seq_number)
        self.socket.send(address, syn_ack)

    def __handle_ack(self, address, packet):
        """
        Handles ACK request
        :param address: Client's address
        :param packet: ACK packet
        """
        if address[1] in self.awaiting_connections:
            session = self.awaiting_connections[address[1]]
            del self.awaiting_connections[address[1]]
            self.available_sessions.put(session)
        else:
            self.income_packet_emitter.emit(address=address[1], pkt=packet)

    def __send(self, address, packet):
        self.socket.send(address, packet)

    def accept(self):
        """
        Accepts new clients
        :return: new session with client
        """
        self.acceptors += 1
        session = self.available_sessions.get()
        self.available_sessions.task_done()
        self.acceptors -= 1

        return session

    def shutdown(self):
        """
        Shuts down the server
        """
        self.run = False
        self.socket.close()

