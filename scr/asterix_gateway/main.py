# -*- coding: utf-8 -*-

from gateway.gateway import Gateway
from gateway.listener import BeastListener
from gateway.sender import UdpSbsSender

from globals_app import (
    DUMP_HOST, DUMP_PORT,
    ASTERIX_HOST, ASTERIX_PORT,
)

if __name__ == "__main__":
    listener = BeastListener(source_host=DUMP_HOST, source_port=DUMP_PORT)
    sender = UdpSbsSender(target_host=ASTERIX_HOST, target_port=ASTERIX_PORT)

    gateway = Gateway(listener=listener, sender=sender)
    try:
        print("Press Ctrl+C for exit")
        gateway.start()
    except KeyboardInterrupt:
        print("\nInterrupt...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        gateway.stop()
