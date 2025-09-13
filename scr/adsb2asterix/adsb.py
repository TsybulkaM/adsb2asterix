import socket
import time
import pyModeS as pms
from pyModeS.extra.tcpclient import TcpClient
from pyModeS.decoder import adsb

from asterix import AsterixCat021Message
from globals_app import (
    SAC, SIC,
    LAT_REF, LON_REF, LAT_LON_RANGE,
    CACHE_TIMEOUT
)

class ADSBRetransmitter(TcpClient):
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


    def process_adsb_message(self, msg, timestamp):
        if len(msg) != 28:
            return
        
        try:
            if adsb.df(msg) != 17 or pms.crc(msg) != 0:
                return
            
            icao = adsb.icao(msg)
            tc = adsb.typecode(msg)
            
            lat, lon = None, None
            velocity = None
            altitude = None
            callsign = None
            emitter_category = None

            if tc == 19:
                velocity = adsb.velocity(msg)
                print(f"Velocity: {velocity}")
            elif 9 <= tc <= 18:
                oe = adsb.oe_flag(msg)
                
                if icao not in self.position_cache:
                    self.position_cache[icao] = [None, None, None, None]
                
                if oe == 0:
                    self.position_cache[icao][0] = msg
                    self.position_cache[icao][1] = timestamp
                else:
                    self.position_cache[icao][2] = msg
                    self.position_cache[icao][3] = timestamp
                
                msg_even, t_even, msg_odd, t_odd = self.position_cache[icao]
                if (msg_even and msg_odd and t_even and t_odd and 
                    abs(t_even - t_odd) < CACHE_TIMEOUT):
                    position = adsb.airborne_position(msg_even, msg_odd, t_even, t_odd)
                    if position:
                        lat, lon = position
                
                if lat is None or lon is None:
                    position = adsb.position_with_ref(msg, LAT_REF, LON_REF)
                    if position:
                        lat, lon = position

                altitude = adsb.altitude(msg)
            
            elif 5 <= tc <= 8:
                position = adsb.surface_position_with_ref(msg, LAT_REF, LON_REF)
                if position:
                    lat, lon = position
            
            elif 1 <= tc <= 4:
                callsign = adsb.callsign(msg)
            
            if lat is not None and lon is not None:
                if not ((LAT_REF - LAT_LON_RANGE <= lat <= LAT_REF + LAT_LON_RANGE and
                    LON_REF - LAT_LON_RANGE <= lon <= LON_REF + LAT_LON_RANGE)):
                    print(f"Position out of range: {lat}, {lon}")
                    return

            asterix_packet = AsterixCat021Message(
                icao=icao, sac=SAC, sic=SIC, 
                lat=lat, lon=lon, 
                altitude_ft=altitude, velocity=velocity, 
                callsign=callsign, emitter_category=emitter_category
            )
            encoded_packet = asterix_packet.encode()
            if self.udp_socket and encoded_packet:
                self.udp_socket.sendto(encoded_packet, (self.tx_host, self.tx_port))

            print(f"{asterix_packet} - {encoded_packet.hex().upper()}")

        except Exception as e:
            print(f"Error processing message {msg}: {e}")


    def handle_messages(self, messages):
        self._cleanup_cache()
        
        for msg, timestamp in messages:
            if isinstance(msg, str) and len(msg) == 28:
                self.process_adsb_message(msg, timestamp)


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
        super().close()
