import random
import string
import struct

from scapy.layers import dns

from . import base


class RandomBytesMixin:

    def samples(self):
        min_length = self.kwargs['min_length']
        max_length = self.kwargs['max_length']
        for _ in range(self.count):
            yield random.randbytes(
                random.randint(min_length, max_length)
            )


class PrependStringMixin:

    separator = ''

    def mutate(self, value):
        min_length = self.kwargs['min_length']
        max_length = self.kwargs['max_length']
        return ''.join(
            random.choices(string.ascii_letters, k=random.randint(min_length, max_length))
        ) + self.separator + value


class UdpRandom(RandomBytesMixin, base.UdpProbe):

    pass


class TcpRandom(RandomBytesMixin, base.TcpProbe):

    pass


class DnsUdpPayload(base.UdpProbe):

    def samples(self):
        query = self.kwargs['payload']
        for _ in range(self.count):
            payload = self.mutate(query)
            yield dns.DNS(rd=1, qd=dns.DNSQR(qname=payload)).build()


class DnsTcpPayload(base.TcpProbe):

    def samples(self):
        query = self.kwargs['payload']
        for _ in range(self.count):
            payload = self.mutate(query)
            payload = dns.DNS(rd=1, qd=dns.DNSQR(qname=payload)).build()
            yield struct.pack('>h', len(payload)) + payload


class DnsUdpSubdomain(PrependStringMixin, DnsUdpPayload):

    separator = '.'


class DnsTcpSubdomain(PrependStringMixin, DnsTcpPayload):

    separator = '.'
