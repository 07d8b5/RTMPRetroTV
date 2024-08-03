import os
import time


def update_playlist(file_to_play, playlist_file):
    with open(playlist_file, "r") as file:
        lines = file.readlines()
    if len(lines) > 1:
        lines[1] = f"file '{file_to_play}'\n"

    with open(playlist_file, "w") as file:
        file.writelines(lines)


def tail_f(filename):
    with open(filename, "r") as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def watch_playlist(log_file, playlist_file, upnext_file, fallback_file):
    for line in tail_f(log_file):
        if "auto-inserting h264_mp4toannexb bitstream filter" in line.lower():
            print(f"New log entry detected: {line.strip()}")
            if os.path.getsize(upnext_file) > 0:
                with open(upnext_file, "r") as file:
                    next_file = file.readline().strip()
                print(f"Updating playlist with {next_file} from upnext.txt")
                update_playlist(next_file, playlist_file)

                with open(upnext_file, "r") as file:
                    lines = file.readlines()
                with open(upnext_file, "w") as file:
                    file.writelines(lines[1:])
            else:
                print("upnext.txt is empty. Using fallback.mp4")
                update_playlist(fallback_file, playlist_file)
