import queue
import time
from .listener import Listener
from .sender import Sender


from globals_app import (
    DEBUG,
    POSITION_LIMIT, LAT_RANGE_PAIRS, LON_RANGE_PAIRS
)

CACHE_EXPIRY_SECONDS = 5 * 60 # 5 minutes

class Gateway():
    def __init__(self, listener: Listener, sender: Sender):
        self.data_queue = queue.Queue()
        self.listener = listener
        self.sender = sender
        self.listener.output_queue = self.data_queue
        self._running = False
        self.aircraft_status_cache = {}

    def start(self):
        self._running = True
        self.listener.start()

        while self._running:
            try:
                aircraft_data = self.data_queue.get(timeout=1)
                
                if POSITION_LIMIT:
                    if aircraft_data.icao in self.aircraft_status_cache:
                        if time.time() - self.aircraft_status_cache[aircraft_data.icao]['timestamp'] > CACHE_EXPIRY_SECONDS:
                            del self.aircraft_status_cache[aircraft_data.icao]
                        else:
                            self.aircraft_status_cache[aircraft_data.icao]['timestamp'] = time.time()
                            return self.aircraft_status_cache[aircraft_data.icao]['in_zone']

                    if aircraft_data.lat is None or aircraft_data.lon is None:
                        verdict = False
                        for (min_lat, max_lat), (min_lon, max_lon) in zip(LAT_RANGE_PAIRS, LON_RANGE_PAIRS):
                            if min_lat <= aircraft_data.lat <= max_lat and min_lon <= aircraft_data.lon <= max_lon:
                                verdict = True
                                break
                        self.aircraft_status_cache[aircraft_data.icao] = {'in_zone': verdict, 'timestamp': time.time()}
                        if not verdict:
                            continue

                self.sender.send(aircraft_data)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                self.stop()
                break

    def stop(self):
        self._running = False
        self.listener.stop()
        self.sender.close()
