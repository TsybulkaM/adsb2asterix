from pyModeS.decoder import adsb
from pyModeS.decoder import bds
import time

from aircraft_data import AircraftData, VelocityData

from globals_app import (
    LAT_REF, LON_REF, 
    POSITION_LIMIT, LAT_RANGE_PAIRS, LON_RANGE_PAIRS,
    CACHE_TIMEOUT
)

aircraft_status_cache = {}
position_cache = {}

def process_adsb(msg, timestamp) -> AircraftData | None:
    try:
        icao = adsb.icao(msg)
        tc = adsb.typecode(msg)

        lat = None
        lon = None
        altitude = None
        velocity = None
        callsign = None
        emitter_category = None
        speed = None
        track = None
        vr = None
        speed_type = None
        position = None

        if tc == 19:
            velocity_tuple = adsb.velocity(msg)
            if velocity_tuple:
                speed, track, vr, speed_type = velocity_tuple
                velocity = VelocityData(
                    speed=int(speed),
                    track=track,
                    vertical_rate=vr,
                    speed_type=speed_type
                )
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
            if time.time() - aircraft_status_cache[icao]['timestamp'] > CACHE_TIMEOUT:
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

        aircraft_data = AircraftData(
            icao=icao,
            lat=lat, lon=lon, 
            altitude_ft=altitude, 
            velocity=velocity, 
            callsign=callsign, 
            emitter_category=emitter_category
        )

        return aircraft_data
    except Exception as e:
        print(f"Error processing message {msg}: {e}")