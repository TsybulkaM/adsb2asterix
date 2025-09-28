# -*- coding: utf-8 -*-

from gateway import AdsbAsterixGateway, SBSAsterixGateway
from globals_app import (
    GATEWAY_TYPE,
    DUMP_HOST, DUMP_PORT,
    ASTERIX_HOST, ASTERIX_PORT,
)

if __name__ == "__main__":
    client = None
    try:
        match GATEWAY_TYPE:
            case 'BEAST':
                client = AdsbAsterixGateway(
                    DUMP_HOST, DUMP_PORT, 
                    ASTERIX_HOST, ASTERIX_PORT
                )
            case 'SBS':
                client = SBSAsterixGateway(
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
