#!/bin/bash

log_file="logfile.log"

make -f Makefile.dev stream_to_server 2>> "$log_file" &

sleep 0.5
# Initial file swap
sed -i '2s|file .*|file '\''Isis_c.mp4'\''|' playlist.txt

tail -F "$log_file" | while read -r line; do
    if echo "$line" | grep -i "auto-inserting h264_mp4toannexb bitstream filter"; then
        echo "New log entry detected: $line"
		sed -i '2s|file .*|file '\''IloveTokyo.mp4'\''|' playlist.txt
    fi
done
