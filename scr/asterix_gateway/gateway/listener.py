from abc import ABC, abstractmethod
from pyModeS.extra.tcpclient import TcpClient

from mode_s.common import process_mode_s

import threading

from globals_app import DEBUG


class Listener(TcpClient, ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class BeastListener(Listener):
    def __init__(self, source_host, source_port, output_queue=None):
        print(f"Source: {source_host}:{source_port}")
        super().__init__(host=source_host, port=source_port, datatype='beast')
        self._running = False
        self.output_queue = output_queue
        self.thread = None
    
    def start(self):
        if self._running:
            print("Listener is already running.")
            return

        if self.output_queue is None:
            raise ValueError("Output queue is not set.")
            
        self._running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if not self._running:
            return
            
        self._running = False
        super().close()
        if self.thread:
            self.thread.join(timeout=2)

    def handle_messages(self, messages):
        if not self._running:
            return
        
        for msg, timestamp in messages:
            if DEBUG:
                print(f"Received BEAST message: {msg}")
            
            aircraft_data = process_mode_s(msg, timestamp) 
            if aircraft_data:
                self.output_queue.put(aircraft_data)

        return None

    def close(self):
        if self.udp_socket:
            self.udp_socket.close()


class SbsListener(Listener):
    def __init__(self, source_host, source_port, output_queue=None):
        print(f"Source: {source_host}:{source_port}")
        super().__init__(host=source_host, port=source_port)
        self._running = False
        self.output_queue = output_queue
        self.thread = None
    
    def start(self):
        if self._running:
            print("Listener is already running.")
            return

        if self.output_queue is None:
            raise ValueError("Output queue is not set.")
            
        self._running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if not self._running:
            return
            
        self._running = False
        super().close()
        if self.thread:
            self.thread.join(timeout=2)

    def handle_messages(self, messages):
        if not self._running:
            return
        
        for msg, timestamp in messages:
            if DEBUG:
                print(f"Received SBS message: {msg}")
            
            aircraft_data = process_mode_s(msg, timestamp) 
            if aircraft_data:
                self.output_queue.put(aircraft_data)

        return None

    def close(self):
        if self.udp_socket:
            self.udp_socket.close()