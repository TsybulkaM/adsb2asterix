import pyModeS as pms
from aircraft_data import AircraftData
from globals_app import DEBUG


def process_df11(msg_hex) -> AircraftData | None:
    icao = pms.icao(msg_hex).upper()

    if False:
        print(f"DF11 Message: {msg_hex}")
        print(f"  ICAO: {icao}")

    return None
