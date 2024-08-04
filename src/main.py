import subprocess
from multiprocessing import Process
from watchdog import watch_playlist
from scheduler import start_scheduler

def run_watch_playlist(log_file, playlist_file, upnext_file, fallback_file):
    # Function to start the watch_playlist in a subprocess
    watch_playlist(log_file, playlist_file, upnext_file, fallback_file)

def run_start_scheduler(scheduler_file, upnext_file):
    # Function to start the scheduler in a subprocess
    start_scheduler(scheduler_file, upnext_file)

if __name__ == "__main__":

    subprocess.Popen(["make", "stream_to_server"])

    log_file = "log_file.log"
    playlist_file = "playlist.txt"
    upnext_file = "upnext.txt"
    fallback_file = "video/fallback.mp4"
    scheduler_file = "config/schedule.yaml"

    # Create the processes
    watch_process = Process(target=run_watch_playlist, args=(log_file, playlist_file, upnext_file, fallback_file))
    scheduler_process = Process(target=run_start_scheduler, args=(scheduler_file, upnext_file))

    # Start the processes
    watch_process.start()
    scheduler_process.start()

    # Wait for the processes to finish (optional)
    watch_process.join()
    scheduler_process.join()
