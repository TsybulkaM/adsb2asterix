import struct


class AsterixCat021Message:
    _flight_status_map = {
        0: "Normal, Airborne",
        1: "Normal, On-ground",
        2: "ALERT, Airborne",
        3: "ALERT, On-ground",
        4: "ALERT, Special Position Identification (SPI)",
        5: "Normal, Special Position Identification (SPI)",
    }

    FIELD_MAP = {
        'data_source_id':         {'num': 1,  'handler': '_encode_source_id'},
        'target_report_desc':     {'num': 3,  'handler': '_encode_trd'},
        'position':               {'num': 6,  'handler': '_encode_position'},
        'target_address':         {'num': 11, 'handler': '_encode_icao'},
        'altitude':               {'num': 16, 'handler': '_encode_altitude'},
        'squawk':                 {'num': 19, 'handler': '_encode_squawk'},
        'flight_status_code':     {'num': 23, 'handler': '_encode_flight_status_code'},
        'baro_vert_rate':         {'num': 24, 'handler': '_encode_vertical_rate'},
        'ground_vector':          {'num': 26, 'handler': '_encode_ground_vector'},
        'callsign':               {'num': 29, 'handler': '_encode_callsign'},
        'emitter_category':       {'num': 30, 'handler': '_encode_emitter_category'},
    }

    def __init__(self, icao, sac, sic, lat=None, lon=None, altitude_ft=None, velocity=None, 
                callsign=None, emitter_category=None, squawk=None, flight_status_code=None
        ):
        self.icao = icao
        self.sac = sac
        self.sic = sic
        self.lat = lat
        self.lon = lon
        self.altitude_ft = altitude_ft
        self.velocity = velocity
        self.callsign_str = callsign
        self.emitter_category = emitter_category
        self.squawk = squawk
        #self.flight_status_code = flight_status_code
        self.flight_status_code = None

    def __str__(self):
        return (f"AsterixCat021Message(icao={self.icao}, sac={self.sac}, sic={self.sic}, "
                f"lat={self.lat}, lon={self.lon}, altitude_ft={self.altitude_ft}, "
                f"velocity={self.velocity}, callsign={self.callsign_str}, "
                f"emitter_category={self.emitter_category}, squawk={self.squawk}, "
                f"flight_status_code={self.flight_status_code} [{self._flight_status_map.get(self.flight_status_code, "Unknown")}])"
                )

    def encode(self):
        present_items = set()
        
        present_items.add(1)

        if self.flight_status_code is not None:
            present_items.add(2)

        present_items.add(11)

        if self.lat is not None and self.lon is not None: 
            present_items.add(6)

        if self.altitude_ft is not None:
            present_items.add(16)

        if self.squawk is not None:
            present_items.add(19)

        if self.flight_status_code is not None:
            present_items.add(23)

        if self.callsign_str is not None: 
            present_items.add(29)

        if self.velocity is not None:
            present_items.add(26)

            vert_rate = self.velocity[2]
            if vert_rate != 0:
                present_items.add(24)

        if self.emitter_category is not None:
            present_items.add(30)

        # --- FSPEC ---
        max_item_num = max(present_items)
        num_fspec_bytes = (max_item_num - 1) // 7 + 1
        fspec_bytes = [0] * num_fspec_bytes
        for item_num in present_items:
            byte_index = (item_num - 1) // 7
            bit_index = 7 - ((item_num - 1) % 7)
            fspec_bytes[byte_index] |= (1 << bit_index)
        for i in range(num_fspec_bytes - 1):
            fspec_bytes[i] |= 1
        fspec = bytes(fspec_bytes)

        data_payload = bytearray()
        for item_num in sorted(list(present_items)):
            for field_name, spec in self.FIELD_MAP.items():
                if spec['num'] == item_num:
                    handler = getattr(self, spec['handler'])
                    data_payload += handler()
                    break

        packet_length = 3 + len(fspec) + len(data_payload)
        packet = bytearray([21])
        packet += packet_length.to_bytes(2, 'big')
        packet += fspec
        packet += data_payload
        
        return bytes(packet)

    # --- Methods-encoders ---
    def _encode_source_id(self): return struct.pack('>BB', self.sac, self.sic)
    def _encode_icao(self): return int(self.icao, 16).to_bytes(3, 'big')
    def _encode_position(self):
        lsb = 180.0 / (2**23)
        lat_enc = int(self.lat / lsb).to_bytes(3, 'big', signed=True)
        lon_enc = int(self.lon / lsb).to_bytes(3, 'big', signed=True)
        return lat_enc + lon_enc
    def _encode_altitude(self):
        return int(self.altitude_ft / 6.25).to_bytes(2, 'big', signed=True)

    def _encode_callsign(self):
        char_map = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ## ###############0123456789######"
        encoded = 0
        callsign = self.callsign_str.upper().strip().replace('_', ' ').ljust(8, ' ')[:8]
        for char in callsign:
            encoded <<= 6
            encoded |= char_map.index(char)
        return encoded.to_bytes(6, 'big')

    def _encode_ground_vector(self):
        speed_kts = self.velocity[0]
        track_deg = self.velocity[1]

        try:
            speed_resolution = 2**-14 # NM/s
            track_resolution = 360.0 / (2**16) # degrees
            speed_in_nms = speed_kts * (0.514444 / 1852)
            scaled_speed = int(speed_in_nms / speed_resolution)
            scaled_track = int(track_deg / track_resolution)

            scaled_speed = max(0, min(scaled_speed, 65535))
            scaled_track = max(0, min(scaled_track, 65535))
            return struct.pack('>HH', scaled_speed, scaled_track)
        except Exception as e:
            print(f"Error encoding ground vector: {e}, values: speed_kts={speed_kts}, track_deg={track_deg}")
            return b'\x00\x00\x00\x00'

    def _encode_vertical_rate(self):
        vert_rate_fpm = self.velocity[2]
        
        resolution = 6.25
        scaled_vert_rate = int(vert_rate_fpm / resolution)
        
        return struct.pack('>h', scaled_vert_rate)

    def _encode_emitter_category(self):
        return struct.pack('>B', self.emitter_category)
    
    def _encode_squawk(self):
        return int(self.squawk).to_bytes(2, 'big')

    def _encode_flight_status_code(self):
        target_status = 0

        if self.flight_status_code in [2, 3, 4]:
            ps_mask = (1 << 4)
            target_status |= ps_mask

        return target_status.to_bytes(1, 'big')

    def _encode_trd(self):
        target_report_descriptor = 0

        if self.flight_status_code in [1, 3]:
            vs_mask = (1 << 2)
            target_report_descriptor |= vs_mask

        if self.flight_status_code in [4, 5]:
            spi_mask = (1 << 3)
            target_report_descriptor |= spi_mask
            
        return target_report_descriptor.to_bytes(1, 'big')