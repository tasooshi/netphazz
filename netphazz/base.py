import socket
import concurrent.futures

from . import exceptions
from . import transports


class Probe:

    transport = None
    template = None
    buffer = 32

    def __init__(self, address, port, timeout, count, threads, **kwargs):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.count = count
        self.threads = threads
        self.kwargs = kwargs

    def connect(self, sock):
        raise NotImplementedError

    def disconnect(self, sock=None):
        pass

    def mutate(self, value):
        return value

    def samples(self):
        raise NotImplementedError

    def job(self, sample):
        sock = self.transport.create(self.address)
        sock.settimeout(self.timeout)
        try:
            self.connect(sock)
            self.transport.send(sock, sample)
            self.transport.read(sock, self.buffer)
        except (OSError, exceptions.ConnectionFailed):
            pass
        finally:
            self.disconnect(sock)

    def test(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            for sample in self.samples():
                executor.submit(self.job, sample)


class UdpProbe(Probe):

    transport = transports.UDP

    def connect(self, sock):
        sock.connect((self.address, self.port))


class TcpProbe(Probe):

    transport = transports.TCP

    def connect(self, sock):
        port_state = sock.connect_ex((self.address, self.port))
        if port_state == 101:
            raise exceptions.ConnectionFailed
        elif port_state != 0:
            raise exceptions.ConnectionFailed

    def disconnect(self, sock=None):
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
