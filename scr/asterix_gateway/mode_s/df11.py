import pyModeS as pms

from globals_app import DEBUG


def process_df11(msg_hex):
    icao = pms.icao(msg_hex).upper()

    if DEBUG:
        print(f"DF11 Message: {msg_hex}")
        print(f"  ICAO: {icao}")

    return None
