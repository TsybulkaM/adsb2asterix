import time
from aircraft_data.aircraft_data import AircraftData
from globals_app import (
    LAT_RANGE_PAIRS, LON_RANGE_PAIRS, CACHE_TIMEOUT
)

aircraft_status_cache = {}


def distribute_positions(aircraft_data: AircraftData) -> bool:
    if aircraft_data.icao in aircraft_status_cache:
        if time.time() - aircraft_status_cache[aircraft_data.icao]['timestamp'] > CACHE_TIMEOUT:
            del aircraft_status_cache[aircraft_data.icao]
        else:
            aircraft_status_cache[aircraft_data.icao]['timestamp'] = time.time()
            return aircraft_status_cache[aircraft_data.icao]['in_zone']

    if aircraft_data.lat is None or aircraft_data.lon is None:
        for (min_lat, max_lat), (min_lon, max_lon) in zip(LAT_RANGE_PAIRS, LON_RANGE_PAIRS):
            if min_lat <= aircraft_data.lat <= max_lat and min_lon <= aircraft_data.lon <= max_lon:
                aircraft_status_cache[aircraft_data.icao] = {'in_zone': True, 'timestamp': time.time()}
                return True
        
        aircraft_status_cache[aircraft_data.icao] = {'in_zone': False, 'timestamp': time.time()}
        return False