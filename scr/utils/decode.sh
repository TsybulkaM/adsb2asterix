#!/bin/bash

# Dependencies:
# sudo apt install wireshark tshark

# Script to decode a hex string into an ASTERIX packet and display it with tshark
# HEX string format example: 15002185114129803001251EB80C048D48C13315E0FFF6017E56594994B4B4C09D
hex_string="$1"
formatted_hex=$(echo "$hex_string" | sed 's/../& /g')

echo "0000 $formatted_hex" > hex.txt

text2pcap -u 40001,40001 hex.txt asterix.pcap
tshark -r asterix.pcap -d udp.port==40001,asterix -V