import struct, random, hashlib
from .constants import ACK, SYN, FIN, SYN_ACK, FIN_ACK, PACKET_HEADER_SIZE

_INT_MAX = 4294967296
_HEADER_SIZE = PACKET_HEADER_SIZE
_CHECKSUM_LEN = 4
_PACK_FORMAT = "!I I B H"
_UNPACK_FORMAT = "!I I B H"

def generate_id():
    return random.randint(0, _INT_MAX)


def _calculate_checksum(header):
    checksum = hashlib.sha256(header)
    return struct.pack("!I", checksum)

class Packet:
    def __init__(self, **fields):
        if 'header' in fields:
            self.dissect(fields['header'])
        else:
            self.seq_number = fields['seq'] if 'seq' in fields else None
            self.operation = fields['oper'] if 'oper' in fields else None
            self.ack_number = fields['ack'] if 'ack' in fields else generate_id()
            self.payload = fields['payload'] if 'payload' in fields else bytes()
            self.payload_size = len(self.payload) if self.payload else 0
            self.checksum = None
            self.ver_cksm = False

    def dissect(self, header):
        """
        Dissects a packet
        :param header: (bytes) packet header
        :return:
        """
        checksum_pointer = _HEADER_SIZE - _CHECKSUM_LEN
        self.checksum =  header[checksum_pointer:]
        header = header[:checksum_pointer]
        checksum = struct.pack('!4s', hashlib.sha256(header).digest())
        self.ver_cksm = checksum == self.checksum

        header = struct.unpack(_UNPACK_FORMAT, header)
        self.seq_number = header[0]
        self.ack_number = header[1]
        self.operation = header[2]
        self.payload_size = header[3]

    def verify_checksum(self):
        return self.ver_cksm

    def ack(self, seq_number=0):
        """
        Returns an ack packet for the current packet
        :param seq_number: akc sequence number
        :return:
        """
        operation = ACK
        if self.operation == SYN:
            operation = SYN_ACK
        elif self.operation == FIN:
            operation = FIN_ACK
        packet = Packet(seq=seq_number, oper=operation, ack=self.ack_number)

        return packet

    def __bytes__(self):
        """
        Returns pack in bytes
        """
        pack = struct.pack(_PACK_FORMAT, self.seq_number, self.ack_number, self.operation, self.payload_size)
        checksum = struct.pack('! 4s', hashlib.sha256(pack).digest())
        if type(self.payload) == str:
            self.payload = self.payload.encode('utf-8')

        return bytes(pack + checksum + self.payload)

    def __len__(self):
        return _HEADER_SIZE + self.payload_size

    def __repr__(self):
        return 'Sequence number: {}\t' \
               'Operation: {}\t' \
               'Ack number: {}\t' \
               'Payload len: {}\n'.format(str(self.seq_number), str(self.operation),
                                       str(self.ack_number), self.payload_size)
