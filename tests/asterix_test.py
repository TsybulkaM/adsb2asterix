import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scr', 'asterix_gateway'))

from asterix import AsterixCat021Message

def test_asterix021_packaging():
    ICAO = '48C133'
    SAC = 48
    SIC = 1
    LAT = 52.2
    LON = 16.9
    ALTITUDE = 35000
    CALLSIGN = 'SPSMZ___'
    EMITTER_CATEGORY = 4
    SQUAWK = 1000
    FLIGHT_STATUS_CODE = 1

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
        emitter_category=EMITTER_CATEGORY,
        squawk=SQUAWK,
        flight_status_code=FLIGHT_STATUS_CODE
    )

    packet = msg.encode()
    print(packet.hex().upper())
    assert packet is not None


def test_asterix_packet_decode_with_bash():
    import subprocess
    import os
    
    ICAO = '48C133'
    SAC = 48
    SIC = 1
    LAT = 52.2
    LON = 16.9
    ALTITUDE = 35000
    CALLSIGN = 'SPSMZ___'
    EMITTER_CATEGORY = 4
    SQUAWK = 1000
    FLIGHT_STATUS_CODE = 1

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
        emitter_category=EMITTER_CATEGORY,
        squawk=SQUAWK,
        flight_status_code=FLIGHT_STATUS_CODE
    )

    packet = msg.encode()
    hex_packet = packet.hex().upper()
    print(f"Testing packet: {hex_packet}")
    
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scr', 'utils', 'asterix_tshark_decode.sh')
    
    try:
        result = subprocess.run(
            ['bash', script_path, hex_packet],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(script_path)
        )
        
        assert result.returncode == 0, f"Script failed with return code {result.returncode}. stderr: {result.stderr}"
        
        output = result.stdout + result.stderr
        assert "[Malformed Packet: ASTERIX]" not in output, f"Found malformed packet error in output: {output}"
        assert "Malformed Packet (Exception occurred)" not in output, f"Found malformed packet exception in output: {output}"
        
        assert "ASTERIX" in output, f"No ASTERIX data found in output: {output}"
        
        print("✓ Packet decoded successfully without malformed errors")
        
    except subprocess.TimeoutExpired:
        pytest.fail("Script execution timed out")
    except Exception as e:
        pytest.fail(f"Error running decode script: {e}")
