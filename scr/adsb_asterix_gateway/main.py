# -*- coding: utf-8 -*-

from adsb import AdsbAsterixGateway
from globals_app import (
    DUMP_HOST, DUMP_PORT,
    ASTERIX_HOST, ASTERIX_PORT,
)


if __name__ == "__main__":
    client = None
    try:
        client = AdsbAsterixGateway(
            DUMP_HOST, DUMP_PORT, 
            ASTERIX_HOST, ASTERIX_PORT
        )
        print("Press Ctrl+C for exit")
        client.run()
    except KeyboardInterrupt:
        print("\nInterrupt...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.close()
