import pyModeS as pms

from asterix import AsterixCat021Message

from globals_app import (
    SAC, SIC, DEBUG, DEV
)

def process_df5_to_asterix(msg):
    msg_int = int(msg, 16)

    icao = pms.icao(msg).upper()

    fs_val = (msg_int >> 48) & 0b111
    id_code = pms.common.idcode(msg)

    asterix_packet = AsterixCat021Message(
        icao=icao, sac=SAC, sic=SIC, 
        squawk=id_code, flight_status_code=fs_val
    )
    encoded_packet = asterix_packet.encode()
    
    if DEV:
        print(f"{asterix_packet} - {encoded_packet.hex().upper()}")

    return encoded_packet

    
