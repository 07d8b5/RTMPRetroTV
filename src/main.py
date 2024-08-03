import subprocess

from watchdog import watch_playlist

if __name__ == "__main__":
    subprocess.Popen(["make", "stream_to_server"])
    log_file = "log_file.log"
    playlist_file = "playlist.txt"
    upnext_file = "upnext.txt"
    fallback_file = "fallback.mp4"

    watch_playlist(log_file, playlist_file, upnext_file, fallback_file)
