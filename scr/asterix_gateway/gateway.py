import socket
import time

from pyModeS.extra.tcpclient import TcpClient

from mode_s.common import process_mode_s_to_asterix

from globals_app import (
    LAT_REF, LON_REF, LAT_LON_RANGE,
    CACHE_TIMEOUT, DEBUG
)

class AsterixGateway(TcpClient):
    def __init__(self, rx_host, rx_port, tx_host, tx_port):
        super().__init__(host=rx_host, port=rx_port, datatype='beast')
        self.position_cache = {}
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tx_host = tx_host
        self.tx_port = tx_port

        print("=" * 40)
        print(f"Source: {rx_host}:{rx_port}")
        print(f"Target: {tx_host}:{tx_port}")
        print(f"Region: {LAT_REF:.4f}, {LON_REF:.4f} (±{LAT_LON_RANGE}°)")
        print("=" * 40)


    def handle_messages(self, messages):
        self._cleanup_cache()
        
        for msg, timestamp in messages:
            if DEBUG:
                print(f"Received ADS-B message: {msg} at {timestamp}")
            if isinstance(msg, str):
                encoded_packet = process_mode_s_to_asterix(msg, timestamp)
                if self.udp_socket and encoded_packet:
                    self.udp_socket.sendto(encoded_packet, (self.tx_host, self.tx_port))


    def _cleanup_cache(self):
        current_time = time.time()
        expired = []
        
        for icao, (msg_even, t_even, msg_odd, t_odd) in self.position_cache.items():
            if ((t_even and current_time - t_even > CACHE_TIMEOUT) or
                (t_odd and current_time - t_odd > CACHE_TIMEOUT)):
                expired.append(icao)
        
        for icao in expired:
            del self.position_cache[icao]

    def close(self):
        if self.udp_socket:
            self.udp_socket.close()
