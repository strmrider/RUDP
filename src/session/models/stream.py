import threading, io

_STREAM_LEN_LIMIT = 50000000

class ByteStream:
    def __init__(self):
        self.buffer = io.BytesIO()
        self.buffer_lock = threading.Lock()
        self.available_space = _STREAM_LEN_LIMIT
        self.stream_pointer = 0

    def append(self, new_bytes):
        with self.buffer_lock:
            self.buffer.seek(len(self.buffer.getbuffer()))
            self.buffer.write(new_bytes)

    def fetch(self, length):
        data = b''
        with self.buffer_lock:
            buffer_len = len(self.buffer.getbuffer())
            self.buffer.seek(self.stream_pointer)
            if buffer_len >= self.stream_pointer + length:
                data = self.buffer.read(length)
                self.stream_pointer += length
            elif self.stream_pointer + length > buffer_len:
                data = self.buffer.read()
                self.stream_pointer = buffer_len


            return data
