import heapq, threading, time
from ..models.packet import Packet, generate_id
from .models.acklist import AckList
from ..models.constants import MTU, SEQ_LIMIT, ACK, PAYLOAD, RESEND_ATTEMPTS, ACK_TIMEOUT, PACKET_HEADER_SIZE
from .models.stream import ByteStream

class Session:
    """
    Abstract session class
    """
    def __init__(self, address, server_seq, client_seq):
        self.address = address
        self.id = generate_id()
        self.timestamp = time.time()

        # income packets
        self.__packets = []
        self.stream = ByteStream()
        # income packets seq
        self.packet_counter = client_seq
        # local send packets seq
        self.next_sent_seq = server_seq
        self.lost_packets = 0

        self.awaiting_ack = AckList()
        self.awaiting_ack.resend_emitter.subscribe(self.__emitted_resend)

        self.stream_lock = threading.Lock()
        self.heap_lock = threading.Lock()

        self.run_heap = False
        threading.Thread(target=self.__run_heap, args=()).start()

    def __next_seq(self, seq_type):
        """
        Moves to next sequence number
        :param seq_type: sequence type- local or income
        """
        if seq_type == 0:
            self.packet_counter += 1
            if self.packet_counter == SEQ_LIMIT:
                self.packet_counter = 1
        elif seq_type == 1:
            self.next_sent_seq += 1
            if self.next_sent_seq == SEQ_LIMIT:
                self.next_sent_seq = 1

    def __income_packet(self, packet):
        """
        Handles income packet
        :param packet: income packet
        """
        if packet.operation == ACK:
           self.awaiting_ack.confirm_ack(packet.ack_number)
        elif packet.operation == PAYLOAD:
            if packet.verify_checksum():
                if packet.seq_number >= self.packet_counter:
                    ack = packet.ack()
                    self._send_packet(bytes(ack))
                    heap_element = (packet.seq_number, packet)
                    with self.heap_lock:
                        heapq.heappush(self.__packets, heap_element)

    def __run_heap(self):
        """
        Runs income packets heap
        """
        self.run_heap = True
        attempts = 0
        while self.run_heap:
            seq_number = self.__pop_packet_seq()
            if not seq_number:
                continue
            if seq_number == self.packet_counter:
                with self.heap_lock:
                    seq_number, packet = heapq.heappop(self.__packets)
                    self.stream.append(packet.payload)
                    self.__next_seq(0)
            else:
                if attempts < RESEND_ATTEMPTS:
                    time.sleep(ACK_TIMEOUT)
                    continue
                else:
                    self.lost_packets += 1
                    attempts = 0
                    self.__next_seq(0)
                    self.packet_counter += 1

    def __pop_packet_seq(self):
        """
        Gets top packet from heap
        """
        with self.heap_lock:
            if len(self.__packets) > 0:
                seq = self.__packets[0][0]
                return seq
            else:
                return None

    def receive(self, length):
        return self.stream.fetch(length)

    def send(self, data):
        """
        Sends data to target
        :param data: data to send
        """
        size = len(data)
        if size <= 0:
            raise Exception('Send data error: data length is 0')
        pointer = 0
        while pointer <= size:
            payload = data[pointer:pointer + (MTU-PACKET_HEADER_SIZE)]
            pointer += MTU-PACKET_HEADER_SIZE
            packet = Packet(seq=self.next_sent_seq, oper=PAYLOAD, ack=generate_id(), payload=payload)
            self._send_packet(packet)
            self.awaiting_ack.new_packet(packet)
            self.__next_seq(1)

    def __emitted_resend(self, **args):
        """
        Resend packets. Subscribed method awaiting ack list
        """
        packet = args['pkt']
        self._send_packet(bytes(packet))

    def _send_packet(self, packet): pass

    # abstract
    def close(self): pass

    def close_session(self):
        """
        closes local session
        """
        self.awaiting_ack.close()
        self.run_heap = False
        self.stream = bytes()