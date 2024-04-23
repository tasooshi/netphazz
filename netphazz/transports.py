import ipaddress
import socket


class Transport:

    @staticmethod
    def ip_family(address):
        if isinstance(ipaddress.ip_address(address), ipaddress.IPv4Address):
            return socket.AF_INET
        elif isinstance(ipaddress.ip_address(address), ipaddress.IPv6Address):
            return socket.AF_INET6
        else:
            raise Exception(f'Invalid address: `{address}`')


class TCP(Transport):

    @staticmethod
    def create(address):
        return socket.socket(Transport.ip_family(address), socket.SOCK_STREAM)

    @staticmethod
    def send(sock, data):
        sock.send(data)

    @staticmethod
    def read(sock, buffer):
        return sock.recv(buffer)


class UDP(Transport):

    @staticmethod
    def create(address):
        return socket.socket(Transport.ip_family(address), socket.SOCK_DGRAM)

    @staticmethod
    def send(sock, data):
        ip, port = sock.getpeername()
        sock.sendto(data, (ip, port))

    @staticmethod
    def read(sock, buffer):
        data, _ = sock.recvfrom(buffer)
        return data
