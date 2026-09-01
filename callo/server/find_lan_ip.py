#!/usr/bin/env python3
"""Prints this computer's local network address, for connecting to Callo
from your phone while on the same Wi-Fi. No network traffic is actually
sent -- this just asks the OS which local address it would use."""
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
finally:
    s.close()
