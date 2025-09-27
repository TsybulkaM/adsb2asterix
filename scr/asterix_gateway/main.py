# -*- coding: utf-8 -*-

from gateway import AsterixGateway
from globals_app import (
    DUMP_HOST, DUMP_PORT,
    ASTERIX_HOST, ASTERIX_PORT,
)


if __name__ == "__main__":
    client = None
    try:
        client = AsterixGateway(
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
