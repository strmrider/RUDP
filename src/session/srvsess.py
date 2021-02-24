import time
from .session import Session
from ..models.packet import Packet
from ..models.constants import ACK, FIN, FIN_ACK, FIN_ATTEMPTS, FIN_TIMEOUT
from ..sockets.sock import Socket

class ClientConnection(Session):
    """
    Handling session with a client on server's side
    """
    def __init__(self, address, server_seq, client_seq, new_pkt_emitter):
        super().__init__(address, server_seq, client_seq)
        self.income_pkt_emitter = new_pkt_emitter
        self.income_pkt_emitter.subscribe(self.__new_packet_emitter)
        self.send_socket = Socket()

        self.closing_process = False
        self.session_closed = False

    def __new_packet_emitter(self, **args):
        """
        Handles new income packets
        """
        if args['address'] == self.address[1]:
            packet = args['pkt']
            if packet.operation == FIN:
                self.__send_packet(bytes(packet.ack()))
                self.closing_process = True
            elif self.closing_process:
                if packet.operation == ACK:
                    self.close_session()
                    self.session_closed = True
                    # print('Connection closed')
                elif packet.operation == FIN_ACK:
                    self.__send_packet(bytes(packet.ack()))
                    self.session_closed = True
                    # print('Connection closed')

            else:
                self._Session__income_packet(packet)

    def receive(self, buffer):
        if self.session_closed:
            raise Exception("Data transfer failure: connection is closed")
        return Session.receive(self, buffer)

    def send(self, packet):
        if self.session_closed:
            raise Exception("Data transfer failure: connection is closed")
        Session.send(self, packet)

    def __send_packet(self, data):
        self.send_socket.send(self.address, data)

    def close(self):
        """
        Closes session
        """
        self.close_session()
        self.closing_process = True
        fin = Packet(seq=0, oper=FIN)
        self.__send_packet(fin)
        attempts = 0
        time.sleep(FIN_TIMEOUT)
        while attempts < FIN_ATTEMPTS:
            if self.session_closed:
                break
            else:
                time.sleep(FIN_TIMEOUT)
                self.__send_packet(fin)
                attempts += 1

        if not self.session_closed:
            raise Exception('Connection close error: timeout error, server did not respond')
