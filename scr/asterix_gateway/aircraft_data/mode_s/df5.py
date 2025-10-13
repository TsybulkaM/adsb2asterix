import pyModeS as pms

from aircraft_data import AircraftData

def process_df5(msg) -> AircraftData | None:
    msg_int = int(msg, 16)

    icao = pms.icao(msg).upper()

    fs_val = (msg_int >> 48) & 0b111
    id_code = pms.common.idcode(msg)

    aircraft_data = AircraftData(
        icao=icao, 
        squawk=id_code, flight_status_code=fs_val
    )

    return aircraft_data

    
