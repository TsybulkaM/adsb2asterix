import socket
from aircraft_data import AircraftData
from asterix import AsterixCat021Message
from sbs import SbsMessage
from abc import ABC, abstractmethod

from globals_app import DEBUG


class Sender(ABC):
    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def close(self):
        pass


class UdpAsterixSender(Sender):
    def __init__(self, target_host, target_port):
        self.target_address = (target_host, target_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Target: {self.target_address}")

    def send(self, data: AircraftData):
        try:
            encoded_message = AsterixCat021Message(data).encode()
            self.udp_socket.sendto(encoded_message, self.target_address)
            if DEBUG:
                print(f"Asterix message : {encoded_message.hex().upper()}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def close(self):
        self.udp_socket.close()


class UdpSbsSender(Sender):
    def __init__(self, target_host, target_port):
        self.target_address = (target_host, target_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Target: {self.target_address}")

    def send(self, data: AircraftData):
        try:
            encoded_message = SbsMessage(data).encode()
            self.udp_socket.sendto(encoded_message.encode('utf-8'), self.target_address)
            if DEBUG:
                print(f"SBS message : {encoded_message}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def close(self):
        self.udp_socket.close()
