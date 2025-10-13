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

OUTPUT_PROTOCOL = 'TCP'

class TCPServerOutputProtocol(protocol.Protocol):
    def connectionMade(self):
        print(f"Новый клиент подключился к нашему TCP-серверу: {self.transport.getPeer()}")
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        print(f"Клиент {self.transport.getPeer()} отключился.")
        self.factory.clients.remove(self)

class TCPServerOutputFactory(protocol.Factory):
    protocol = TCPServerOutputProtocol

    def __init__(self):
        self.clients = set()

    def broadcast(self, message: bytes):
        disconnected_clients = set()
        for client in self.clients:
            try:
                client.transport.write(message)
            except Exception as e:
                print(f"Ошибка при отправке клиенту {client.transport.getPeer()}: {e}")
                disconnected_clients.add(client)
        self.clients.difference_update(disconnected_clients)


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
                    print(f"Encoded data: {processed_data.hex().upper() if isinstance(processed_data, bytes) else processed_data}")

                if self.factory.output_type == "UDP":
                    self.factory.udp_transport.write(processed_data, (UDP_HOST, UDP_PORT))
                elif self.factory.output_type == "TCP":
                     if self.factory.server_factory:
                        self.factory.server_factory.broadcast(processed_data)

class TCPClientRelayFactory(protocol.ClientFactory):
    protocol = TCPClientRelayProtocol

    def __init__(self, incomming_message: IAircraftMessage, outcoming_message: IAircraftMessage, output_type: str, server_factory: TCPServerOutputFactory):
        self.output_type = output_type
        self.udp_transport = None
        self.server_factory = server_factory
        self.incomming_message = incomming_message
        self.outcoming_message = outcoming_message

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        p.incomming_message = self.incomming_message
        p.outcoming_message = self.outcoming_message
        return p


if __name__ == '__main__':
    incomming_message = SbsMessage()  
    outcoming_message = SbsMessage()

    server_output_factory = None
    
    if OUTPUT_PROTOCOL == "TCP":
        print("Режим вывода: TCP-сервер")
        server_output_factory = TCPServerOutputFactory()
        reactor.listenTCP(UDP_PORT, server_output_factory, interface=UDP_HOST)
    
    elif OUTPUT_PROTOCOL == "UDP":
        print("Режим вывода: UDP")
        udp_transport = reactor.listenUDP(0, protocol.DatagramProtocol())
    else:
        print(f"Ошибка: Неизвестный OUTPUT_PROTOCOL: {OUTPUT_PROTOCOL}")
        exit(1)

    tcp_client_factory = TCPClientRelayFactory(
        incomming_message=incomming_message,
        outcoming_message=outcoming_message,
        output_type=OUTPUT_PROTOCOL,
        server_factory=server_output_factory
    )

    if OUTPUT_PROTOCOL == "UDP":
        tcp_client_factory.udp_transport = udp_transport

    reactor.connectTCP(DUMP_HOST, DUMP_PORT, tcp_client_factory)
    
    reactor.run()