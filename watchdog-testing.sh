#!/bin/bash

log_file="logfile.log"
playlist_file="playlist.txt"
upnext_file="upnext.txt"
fallback_file="fallback.mp4"

# Function to update the playlist with a given file
update_playlist() {
    local file_to_play="$1"
    sed -i "2s|file .*|file '$file_to_play'|" "$playlist_file"
}

# Initialize playlist with fallback.mp4
update_playlist "$fallback_file"

# Run the make command in the background and redirect stderr to the log file
make -f Makefile.dev stream_to_server 2>> "$log_file" &

# Monitor the log file for changes
tail -F "$log_file" | while read -r line; do
    if echo "$line" | grep -qi "auto-inserting h264_mp4toannexb bitstream filter"; then
        echo "New log entry detected: $line"
        
        # Check if upnext.txt has content
        if [[ -s "$upnext_file" ]]; then
            # Get the first file from upnext.txt
            next_file=$(head -n 1 "$upnext_file")
            echo "Updating playlist with $next_file from upnext.txt"
            update_playlist "$next_file"
            
            # Remove the first line from upnext.txt after updating
            sed -i '1d' "$upnext_file"
        else
            # If upnext.txt is empty, use fallback.mp4
            echo "upnext.txt is empty. Using fallback.mp4"
            update_playlist "$fallback_file"
        fi
    fi
done

