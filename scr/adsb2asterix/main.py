#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from adsb import ADSBRetransmitter
from globals_app import (
    DUMP_HOST, DUMP_PORT,
    ASTERIX_HOST, ASTERIX_PORT,
)


if __name__ == "__main__":
    try:
        client = ADSBRetransmitter(
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
        client.close()
