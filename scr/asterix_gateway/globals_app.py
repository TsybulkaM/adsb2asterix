import envsh

is_loaded = envsh.load()
if not is_loaded:
    raise RuntimeError("Failed to load .sh environment file")

# ======== Connection Settings ========
GATEWAY_TYPE = envsh.read_env('GATEWAY_TYPE', str)  # 'BEAST' or 'SBS'

DUMP_HOST = envsh.read_env('DUMP_HOST', str)
DUMP_PORT = envsh.read_env('DUMP_PORT', int)
UDP_HOST = envsh.read_env('UDP_HOST', str)
UDP_PORT = envsh.read_env('UDP_PORT', int)

# ======== Calibration Settings ========
LAT_REF = envsh.read_env('LAT_REF', float)
LON_REF = envsh.read_env('LON_REF', float)

POSITION_LIMIT = envsh.read_env('POSITION_LIMIT', int)  # 0 - off, 1 - on
LAT_RANGE_PAIRS = envsh.read_env('LAT_RANGE_PAIRS', list[float])
LAT_RANGE_PAIRS = list(zip(LAT_RANGE_PAIRS[::2], LAT_RANGE_PAIRS[1::2]))
LON_RANGE_PAIRS = envsh.read_env('LON_RANGE_PAIRS', list[float])
LON_RANGE_PAIRS = list(zip(LON_RANGE_PAIRS[::2], LON_RANGE_PAIRS[1::2]))

SAC = envsh.read_env('SAC', int)
SIC = envsh.read_env('SIC', int)
SERVICE_ID = envsh.read_env('SERVICE_ID', int)
CACHE_TIMEOUT = envsh.read_env('CACHE_TIMEOUT', int)

# ========= Optional Settings ========
DEBUG = envsh.read_env('DEBUG', int)
DEV = envsh.read_env('DEV', int)