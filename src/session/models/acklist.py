import time, threading
from ...models.event import EventEmitter
from ...models.constants import RESEND_ATTEMPTS, ACK_TIMEOUT

class AckList:
    """
    Stores packets awaiting for acknowledgment
    """
    def __init__(self):
        self.packets = {}
        self.lost_packets = 0
        self.resend_emitter = EventEmitter()
        self.locker = threading.Lock()
        self.active = True

    def new_packet(self, packet):
        """
        adds new sent packet to ack list
        :param packet: new sent packet
        :return:
        """
        with self.locker:
            self.packets[packet.ack_number] = packet
        t = threading.Thread(target=self.run_timeout, args=(packet.ack_number, RESEND_ATTEMPTS, ACK_TIMEOUT,))
        t.start()

    def resend_packet(self, ack_number):
        """
        Resend a packet
        :param ack_number: packet's ack number
        """
        with self.locker:
            self.resend_emitter.emit(pkt=self.packets[ack_number])

    def drop_packet(self, ack_number):
        """
        Drops a packet if ack hasn't been received within timeout
        :param ack_number: packet's ack number
        """
        with self.locker:
            del self.packets[ack_number]
        self.lost_packets += 1

    def confirm_ack(self, ack_number):
        """
        Confirms packet delivery
        :param ack_number: packet's ack number
        :return:
        """
        with self.locker:
            if ack_number in self.packets:
                del self.packets[ack_number]

    def run_timeout(self, ack_number, total_attempts, timeout):
        """
        Runs packet's ack timeout
        :param ack_number: packet's ack number
        :param total_attempts: max resending attempts to
        :param timeout: max time to wait
        :return:
        """
        seconds = 0
        attempts = 0
        while self.active:
            with self.locker:
                if ack_number not in self.packets:
                    break
            if seconds < timeout:
                time.sleep(1)
                seconds += 1
            elif attempts < total_attempts:
                self.resend_packet(ack_number)
                seconds = 0
                attempts += 1
            else:
                self.drop_packet(ack_number)
                break

    def close(self):
        self.active = False

    def get_lost_packets(self):
        return self.lost_packets