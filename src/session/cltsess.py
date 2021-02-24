import threading
from .session import Session
from ..models.packet import Packet
from ..models.constants import ACK, FIN, FIN_ACK, FIN_ATTEMPTS

class ClientSession(Session):
    """
    Client's side session with server
    """
    def __init__(self, address, client_seq, server_seq, socket_wrapper):
        """
        :param address: server's address
        :param client_seq: client's initial sequence number
        :param server_seq: server's initial sequence number
        :param socket_wrapper: socket wrapper
        """
        super().__init__(address, client_seq, server_seq)
        self.run = False
        self.closing_process = False
        self.__network = socket_wrapper
        self.__network.select()
        t = threading.Thread(target=self.__listen_for_packets, args=())
        t.start()

    def __listen_for_packets(self):
        """
        listen for income packets
        """
        self.run = True
        while self.run:
            self.__network.select()
            if self.__network.is_readable():
                packet, address = self.__network.read_packet()
                if packet.operation == FIN:
                    self.closing_process = True
                    self._send_packet(packet.ack())
                elif packet.operation == ACK and self.closing_process:
                    self.close_session()
                    break
                else:
                    self._Session__income_packet(packet)

    def _send_packet(self, data):
        self.__network.send(self.address, data)

    def close(self):
        """
        closes session
        """
        self.close_session()
        self.run = False

        fin = Packet(oper=FIN, seq=0)
        self.__network.send(self.address, fin)
        self.__network.set_timeout(3)
        attempts = 0
        while attempts < FIN_ATTEMPTS:
            try:
                attempts += 1
                packet, address = self.__network.read_packet()
                if packet.operation == FIN_ACK:
                    self.__network.send(self.address, packet.ack())
                    self.__network.set_timeout(None)
                    print('Connection closed')
                    break
            except Exception as e:
                if attempts >= FIN_ATTEMPTS:
                    raise Exception('Connection close error: timeout error, server did not respond')
