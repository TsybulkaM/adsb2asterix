import pyModeS as pms
import time
from globals_app import DEV

from aircraft_data import AircraftData

def process_mode_s(msg, timestamp=time.time()) -> AircraftData | None:
    df = pms.df(msg)
    match df:
        case 5:
            from .df5 import process_df5
            return process_df5(msg)
        case 11:
            from .df11 import process_df11
            process_df11(msg)
        case 17:
            from .adsb import process_adsb
            return process_adsb(msg, timestamp)
        case _:
            if DEV:
                print(f"Unsupported DF: {df} - {msg}")
            return None