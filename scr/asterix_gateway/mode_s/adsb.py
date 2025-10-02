from pyModeS.decoder import adsb
from pyModeS.decoder import bds
import time

from asterix import AsterixCat021Message

from globals_app import (
    SAC, SIC,
    LAT_REF, LON_REF, 
    POSITION_LIMIT, LAT_RANGE_PAIRS, LON_RANGE_PAIRS,
    CACHE_TIMEOUT, DEBUG
)

aircraft_status_cache = {}
CACHE_EXPIRY_SECONDS = 5 * 60 # 5 minutes

position_cache = {}

def process_adsb_to_asterix(msg, timestamp):
    if DEBUG:
        print(f"Processing message: {msg}")
    try:
        icao = adsb.icao(msg)
        tc = adsb.typecode(msg)
        
        lat, lon = None, None
        velocity = None
        altitude = None
        callsign = None
        emitter_category = None

        if tc == 19:
            velocity = adsb.velocity(msg)
        elif 9 <= tc <= 18:
            oe = adsb.oe_flag(msg)
            
            if icao not in position_cache:
                position_cache[icao] = [None, None, None, None]
            
            if oe == 0:
                position_cache[icao][0] = msg
                position_cache[icao][1] = timestamp
            else:
                position_cache[icao][2] = msg
                position_cache[icao][3] = timestamp
            
            msg_even, t_even, msg_odd, t_odd = position_cache[icao]
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
            callsign = bds.bds08.callsign(msg).strip()
            emitter_category = bds.bds08.category(msg)

        if icao in aircraft_status_cache:
            if time.time() - aircraft_status_cache[icao]['timestamp'] > CACHE_EXPIRY_SECONDS:
                del aircraft_status_cache[icao]
            else:
                aircraft_status_cache[icao]['timestamp'] = time.time()
                return aircraft_status_cache[icao]['in_zone']
            
        if lat is not None and lon is not None and POSITION_LIMIT:
            if POSITION_LIMIT:
                verdict = False
                for (min_lat, max_lat), (min_lon, max_lon) in zip(LAT_RANGE_PAIRS, LON_RANGE_PAIRS):
                    if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                        verdict = True
                        break
                aircraft_status_cache[icao] = {'in_zone': verdict, 'timestamp': time.time()}
                if not verdict:
                    return

        asterix_packet = AsterixCat021Message(
            icao=icao, sac=SAC, sic=SIC, 
            lat=lat, lon=lon, 
            altitude_ft=altitude, velocity=velocity, 
            callsign=callsign, emitter_category=emitter_category
        )
        encoded_packet = asterix_packet.encode()
        
        if DEBUG:
            print(f"{asterix_packet} - {encoded_packet.hex().upper()}")

        return encoded_packet
    except Exception as e:
        print(f"Error processing message {msg}: {e}")