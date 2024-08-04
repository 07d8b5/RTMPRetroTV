import yaml
import os
import random
import time
from datetime import datetime, timedelta

# Function to load and parse the YAML file
def load_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

# Function to verify that files exist
def verify_files(source_directory, episodes):
    missing_files = []
    for episode in episodes:
        file_path = os.path.join(source_directory, episode)
        if not os.path.isfile(file_path):
            missing_files.append(episode)
    return missing_files

# Initialize counters for sequential selection
counters = {}

# Function to get the next episode
def get_next_episode(show_name, show_details, selection_method):
    episodes = show_details['episodes']
    if selection_method == "shuffle":
        return random.choice(episodes)
    elif selection_method == "sequential":
        # Initialize counter if not present
        if show_name not in counters:
            counters[show_name] = 0
        # Get the next episode
        episode = episodes[counters[show_name]]
        # Update the counter, cycling back to the start if necessary
        counters[show_name] = (counters[show_name] + 1) % len(episodes)
        return episode

# Function to calculate the time to wait until the next scheduled slot
def calculate_wait_time(current_day, current_time, target_day, target_time):
    # Calculate the current and target datetime
    current_datetime = datetime.combine(datetime.now(), current_time)
    target_datetime = datetime.combine(datetime.now(), target_time)

    # If the target day is not today, adjust the target datetime
    days_until_target = (target_day - current_day) % 7
    if days_until_target > 0 or current_time > target_time:
        target_datetime += timedelta(days=days_until_target)

    # Calculate the wait time in seconds
    wait_time = (target_datetime - current_datetime).total_seconds()
    if wait_time < 0:
        # If the time has passed for today, adjust to next week
        target_datetime += timedelta(days=7)
        wait_time = (target_datetime - current_datetime).total_seconds()

    return wait_time

# Main function to start the scheduler
def start_scheduler(scheduler_file, upnext_file_path):
    # Load data from YAML file
    data = load_yaml(scheduler_file)

    # Check if data was loaded successfully
    if data:
        # Verify paths and files
        all_files_exist = True
        if 'paths' in data:
            print("\nPaths:")
            for show_name, show_details in data['paths'].items():
                print(f"  {show_name}:")
                print(f"    Source Directory: {show_details['source_directory']}")
                if 'episodes' in show_details:
                    print("    Episodes:")
                    # Verify files in the specified source directory
                    missing_files = verify_files(show_details['source_directory'], show_details['episodes'])
                    if missing_files:
                        all_files_exist = False
                    for episode in show_details['episodes']:
                        status = "Exists" if episode not in missing_files else "Missing"
                        print(f"      - {episode} ({status})")
        else:
            print("\nPaths not found in YAML.")

        # If all files exist, proceed to scheduling
        if all_files_exist and 'schedule' in data['tv_station']:
            print("\nWaiting for scheduled times to append to upnext_file...")
            while True:
                current_datetime = datetime.now()
                current_day = current_datetime.weekday()  # Monday is 0 and Sunday is 6
                current_time = current_datetime.time()

                show_scheduled = False

                for schedule in data['tv_station']['schedule']:
                    target_day = schedule['day']
                    for time_slot in schedule['time_slots']:
                        target_time = datetime.strptime(time_slot['time'], '%H:%M').time()

                        # Calculate the wait time
                        wait_time = calculate_wait_time(current_day, current_time, target_day, target_time)

                        # If we are within a second of the scheduled time, write to upnext_file
                        if 0 <= wait_time <= 1:
                            program = time_slot['program']
                            selection_method = time_slot['selection_method']

                            # Retrieve the show details
                            show_details = data['paths'].get(program)
                            if show_details:
                                # Get the next episode based on the selection method
                                next_episode = get_next_episode(program, show_details, selection_method)
                                # Construct the full path to the episode
                                episode_path = os.path.join(show_details['source_directory'], next_episode)

                                # Log the information and append to the upnext_file
                                print(f"  Day {target_day}, Time {target_time}: {episode_path}")
                                with open(upnext_file_path, 'a') as upnext_file:
                                    upnext_file.write(f"{episode_path}\n")

                                show_scheduled = True

                                # Sleep for 1 second to avoid duplicate writing
                                time.sleep(1)

                # Check if upnext_file is empty and no show is scheduled
                if not show_scheduled:
                    with open(upnext_file_path, 'r+') as upnext_file:
                        content = upnext_file.read().strip()
                        if not content:  # If the file is empty
                            # Select a random commercial
                            commercial_details = data['paths'].get('commercials')
                            if commercial_details:
                                commercial = random.choice(commercial_details['episodes'])
                                commercial_path = os.path.join(commercial_details['source_directory'], commercial)
                                # Log the information and append to the upnext_file
                                print(f"No scheduled show, adding commercial: {commercial_path}")
                                upnext_file.write(f"{commercial_path}\n")

                # Sleep for 1 second before checking again
                time.sleep(1)
        else:
            print("\nSome files are missing. Not proceeding with scheduling.")
    else:
        print("Failed to load YAML data.")

