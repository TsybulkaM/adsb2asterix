import pyModeS as pms
import time
from globals_app import DEV

def process_mode_s_to_asterix(msg, timestamp=time.time()):
    df = pms.df(msg)
    match df:
        case 5:
            from .df5 import process_df5_to_asterix
            return process_df5_to_asterix(msg)
        case 11:
            #from .df11 import process_df11
            #process_df11(msg)
            return None
        case 17:
            from .adsb import process_adsb_to_asterix
            return process_adsb_to_asterix(msg, timestamp)
        case _:
            if DEV:
                print(f"Unsupported DF: {df} - {msg}")
            return None