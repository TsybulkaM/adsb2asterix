import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scr', 'adsb_asterix_gateway'))

from asterix import AsterixCat021Message

def test_asterix021_packaging():
    ICAO = '48C133'
    SAC = 48
    SIC = 1
    LAT = 52.2
    LON = 16.9
    ALTITUDE = 35000
    CALLSIGN = 'SPSMZ___'

    VELOCITY_TUPLE = (84, 121.42956561483851, -64, 'GS')

    msg = AsterixCat021Message(
        icao=ICAO, 
        sac=SAC, 
        sic=SIC, 
        lat=LAT, 
        lon=LON, 
        altitude_ft=ALTITUDE, 
        velocity=VELOCITY_TUPLE,
        callsign=CALLSIGN,
        emitter_category=4
    )

    packet = msg.encode()
    print(packet.hex().upper())
    assert packet is not None