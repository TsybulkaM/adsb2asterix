import datetime
from .aircraft_data import AircraftData, VelocityData, IAircraftMessage


class SbsMessage(IAircraftMessage):
    def _is_in_zone(self, lat: float, lon: float) -> bool:
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            print(f"Warning: Invalid position received: {lat}, {lon}")
            return False
            
        if not self.position_limit:
            return True

        for (min_lat, max_lat), (min_lon, max_lon) in self.lat_lon_pairs:
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return True
        return False

    def decode(self, sbs_string: str) -> AircraftData | None:
        if not sbs_string or not sbs_string.startswith('MSG'):
            return None

        parts = sbs_string.strip().split(',')
        if len(parts) < 22:
            return None

        try:
            icao24 = parts[4].upper()
            if not icao24:
                return None

            msg_type = int(parts[1])
            latitude = float(parts[14]) if parts[14] else None
            longitude = float(parts[15]) if parts[15] else None
            callsign = parts[10].strip() or None if msg_type == 1 and parts[10] else None
            altitude = int(parts[11]) if parts[11] else None
            ground_speed = int(float(parts[12])) if parts[12] else None
            track = float(parts[13]) if parts[13] else None
            vertical_rate = int(parts[16]) if parts[16] else None
            squawk = parts[17] if msg_type == 6 and parts[17] else None

            flight_status_code = None
            if msg_type in (5, 6, 7) and len(parts) > 20:
                alert = int(parts[18]) if parts[18] else 0
                spi = int(parts[20]) if parts[20] else 0
                flight_status_code = (alert << 1) | spi

            velocity = None
            if ground_speed and track and vertical_rate:
                velocity = VelocityData(
                    speed=ground_speed,
                    track=track,
                    vertical_rate=vertical_rate,
                    speed_type='GS'
                )

            return AircraftData(
                icao=icao24,
                sac=self.sac,
                sic=self.sic,
                lat=latitude,
                lon=longitude,
                altitude_ft=altitude,
                velocity=velocity,
                callsign=callsign,
                squawk=squawk,
                #flight_status_code=flight_status_code,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )

        except (ValueError, IndexError) as e:
            print(f"Error decoding SBS message: {e}")
            return None

    def encode(self) -> str:
        parts = [''] * 22
        now = datetime.datetime.now(datetime.timezone.utc)

        parts[0] = 'MSG'
        parts[1] = '3'
        parts[4] = self.aircraft_data.icao
        parts[6] = now.strftime('%Y/%m/%d')
        parts[7] = now.strftime('%H:%M:%S.') + f"{now.microsecond // 1000:03d}"

        if self.aircraft_data.altitude_ft is not None:
            parts[11] = str(self.aircraft_data.altitude_ft)
        if self.aircraft_data.lat is not None:
            parts[14] = f"{self.aircraft_data.lat:.5f}"
        if self.aircraft_data.lon is not None:
            parts[15] = f"{self.aircraft_data.lon:.5f}"

        if self.aircraft_data.velocity:
            if self.aircraft_data.velocity.speed is not None:
                parts[12] = str(self.aircraft_data.velocity.speed)
            if self.aircraft_data.velocity.track is not None:
                parts[13] = f"{self.aircraft_data.velocity.track:.2f}"
            if self.aircraft_data.velocity.vertical_rate is not None:
                parts[16] = str(self.aircraft_data.velocity.vertical_rate)

        return ','.join(parts)