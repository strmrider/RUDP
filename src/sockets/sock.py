import socket, select
from ..models.constants import PACKET_HEADER_SIZE
from ..models.packet import Packet

class Socket:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__is_selecting = False
        self.__readable = self.__writeable = self.__exceptional = None

    def bind(self, ip, port):
        self.socket.bind((ip, port))

    def select(self):
        inputs = [self.socket]
        self.__is_selecting = True
        self.__readable, self.__writeable, self.__exceptional = select.select(inputs, [self.socket], inputs, 0)

    def quit_select(self):
        self.__is_selecting = False

    def is_readable(self):
        return self.socket in self.__readable

    def is_writeable(self):
        return self.socket in self.__writeable

    def is_exceptional(self):
        return self.socket in self.__exceptional

    def is_selecting(self):
        return self.__is_selecting

    def read_packet(self):
        packet_bytes, address = self.socket.recvfrom(1500)
        packet = Packet(header=packet_bytes[:PACKET_HEADER_SIZE])
        if packet.payload_size > 0:
            packet.payload = packet_bytes[PACKET_HEADER_SIZE:]
        return packet, address

    def send(self, address, packet):
        self.socket.sendto(bytes(packet), address)

    def set_timeout(self, timeout):
        self.socket.settimeout(timeout)

    def close(self):
        self.socket.close()