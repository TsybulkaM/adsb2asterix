import envsh

is_loaded = envsh.load()
if not is_loaded:
    raise RuntimeError("Failed to load .sh environment file")

# ======== Connection Settings ========
DUMP_HOST = envsh.read_env('DUMP_HOST', str)
DUMP_PORT = envsh.read_env('DUMP_PORT', int)
ASTERIX_HOST = envsh.read_env('ASTERIX_HOST', str)
ASTERIX_PORT = envsh.read_env('ASTERIX_PORT', int)

# ======== Calibration Settings ========
LAT_REF = envsh.read_env('LAT_REF', float)
LON_REF = envsh.read_env('LON_REF', float)
LAT_LON_RANGE = envsh.read_env('LAT_LON_RANGE', float)
SAC = envsh.read_env('SAC', int)
SIC = envsh.read_env('SIC', int)
SERVICE_ID = envsh.read_env('SERVICE_ID', int)
CACHE_TIMEOUT = envsh.read_env('CACHE_TIMEOUT', int)

# ========= Optional Settings ========
DEBUG = envsh.read_env('DEBUG', int)
DEV = envsh.read_env('DEV', int)