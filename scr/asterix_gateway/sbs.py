import datetime
import time
from asterix import AsterixCat021Message

from globals_app import (
    SAC, SIC, DEBUG, DEV,
    LAT_RANGE_PAIRS, LON_RANGE_PAIRS, POSITION_LIMIT
)

aircraft_status_cache = {}
CACHE_EXPIRY_SECONDS = 5 * 60 # 5 minutes
# -------------------------

def process_sbs_to_asterix(line: str):
    if not line or not line.startswith('MSG'):
        return None

    parts = line.strip().split(',')
    if len(parts) < 22:
        return None

    try:
        msg_type = int(parts[1])
        icao24 = parts[4].upper() if parts[4] else None
        callsign = parts[10].strip() or None if msg_type == 1 else None
        altitude = int(parts[11]) if parts[11] else None
        ground_speed = float(parts[12]) if parts[12] else None
        track = float(parts[13]) if parts[13] else None
        latitude = float(parts[14]) if parts[14] else None
        longitude = float(parts[15]) if parts[15] else None
        vertical_rate = int(parts[16]) if parts[16] else None
        squawk = parts[17] if msg_type == 6 and parts[17] else None
        flight_status_code = None
        if msg_type in (5, 6, 7):
            alert = int(parts[18]) if parts[18] else 0
            emergency = int(parts[19]) if parts[19] else 0
            spi = int(parts[20]) if parts[20] else 0
            flight_status_code = (alert << 2) | (emergency << 1) | spi
        velocity = None
        if ground_speed is not None and track is not None and vertical_rate is not None:
            velocity = (ground_speed, track, vertical_rate, 'GS')

        emitter_category = None
        if len(parts) > 8 and parts[8]:
            emitter_category = _map_aircraft_type_to_category(parts[8])

        if icao24 in aircraft_status_cache:
            if time.time() - aircraft_status_cache[icao24]['timestamp'] > CACHE_EXPIRY_SECONDS:
                del aircraft_status_cache[icao24]
            else:
                aircraft_status_cache[icao24]['timestamp'] = time.time()
                return aircraft_status_cache[icao24]['in_zone']

        if latitude is not None and longitude is not None:
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                print(f"Invalid position: {latitude}, {longitude}")
                return
            
            if POSITION_LIMIT:
                verdict = False
                for (min_lat, max_lat), (min_lon, max_lon) in zip(LAT_RANGE_PAIRS, LON_RANGE_PAIRS):
                    if min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon:
                        verdict = True
                        break
                aircraft_status_cache[icao24] = {'in_zone': verdict, 'timestamp': time.time()}
                if not verdict:
                    return

        msg = AsterixCat021Message(
            icao=icao24,
            sac=SAC,
            sic=SIC,
            lat=latitude,
            lon=longitude,
            altitude_ft=altitude,
            velocity=velocity,
            callsign=callsign,
            emitter_category=emitter_category,
            squawk=squawk,
            flight_status_code=flight_status_code
        )

        packet = msg.encode()

        if DEBUG:
            print(f"{msg} - {packet.hex().upper()}")

        return packet
    except (ValueError, IndexError):
        return None


def _map_aircraft_type_to_category(aircraft_type: str) -> int:
    if aircraft_type.startswith('A'):  # Airbus
        return 4  # Large
    elif aircraft_type.startswith('B'):  # Boeing
        return 4  # Large
    elif aircraft_type.startswith('C'):  # Cessna
        return 1  # Light
    return None


def _generate_timestamp(date_str: str, time_str: str) -> datetime.datetime | None:
    if not date_str or not time_str:
        return None
    try:
        time_str = time_str.split('.')[0]
        full_datetime_str = f"{date_str} {time_str}"
        return datetime.datetime.strptime(full_datetime_str, "%Y/%m/%d %H:%M:%S")
    except ValueError:
        return None


def filter_by_aircraft_state(sbs_string: str) -> bool:
    try:
        parts = sbs_string.split(',')
        if parts[0] != 'MSG' or len(parts) < 5:
            return False

        icao = parts[4]
        msg_type = parts[1]
        
        if icao in aircraft_status_cache:
            if time.time() - aircraft_status_cache[icao]['timestamp'] > CACHE_EXPIRY_SECONDS:
                del aircraft_status_cache[icao]
            else:
                aircraft_status_cache[icao]['timestamp'] = time.time()
                return aircraft_status_cache[icao]['in_zone']

        if msg_type == '3' and len(parts) > 15 and parts[14] and parts[15]:
            lat = float(parts[14])
            lon = float(parts[15])

            verdict = False
            for (min_lat, max_lat), (min_lon, max_lon) in zip(LAT_RANGE_PAIRS, LON_RANGE_PAIRS):
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    verdict = True
                    break

            aircraft_status_cache[icao] = {'in_zone': verdict, 'timestamp': time.time()}
            return verdict
        
        return False

    except (ValueError, IndexError):
        return False