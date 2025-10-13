# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol
from position_distributor import distribute_positions
from aircraft_data.aircraft_data import IAircraftMessage
from aircraft_data.asterix import AsterixCat021Message
from aircraft_data.sbs import SbsMessage

from globals_app import (
    DEBUG,
    DUMP_HOST, DUMP_PORT,
    UDP_HOST, UDP_PORT,
    POSITION_LIMIT,
)

class TCPClientRelayProtocol(protocol.Protocol):
    incomming_message: IAircraftMessage
    outcoming_message: IAircraftMessage

    def dataReceived(self, data: bytes):
        text_data = data.decode('utf-8', errors='ignore')
        lines = text_data.splitlines()
        
        for line in lines:
            if DEBUG:
                print(f"Received data: {line}")

            aircraft_data = self.incomming_message.decode(line)

            if DEBUG:
                print(f"Decoded Aircraft Data: {aircraft_data}")

            if POSITION_LIMIT and not distribute_positions(aircraft_data):
                continue

            processed_data = self.outcoming_message.update(aircraft_data).encode() if aircraft_data else None
            if processed_data:
                if DEBUG:
                    print(f"Encoded data: {processed_data.hex().upper()}")
                self.factory.udp_transport.write(processed_data, (UDP_HOST, UDP_PORT))

class TCPClientRelayFactory(protocol.ClientFactory):
    protocol = TCPClientRelayProtocol

    def __init__(self, incomming_message: IAircraftMessage, outcoming_message: IAircraftMessage):
        self.udp_transport = None
        self.incomming_message = incomming_message
        self.outcoming_message = outcoming_message

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        p.incomming_message = self.incomming_message
        p.outcoming_message = self.outcoming_message
        return p


if __name__ == '__main__':
    incomming_message = SbsMessage()  
    outcoming_message = AsterixCat021Message()

    tcp_client_factory = TCPClientRelayFactory(incomming_message=incomming_message, outcoming_message=outcoming_message)

    udp_transport = reactor.listenUDP(0, protocol.DatagramProtocol())
    tcp_client_factory.udp_transport = udp_transport
    
    reactor.connectTCP(DUMP_HOST, DUMP_PORT, tcp_client_factory)
    reactor.run()