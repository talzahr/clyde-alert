import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import zoneinfo
from pathlib import Path
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Suppress the annoying advertisement by setting an env var
import pygame
del os
import time

rss_url = "https://www.clyde-tx.gov/calendar/rss"
last_checked_file = "last_checked.txt"
new_meetings_file = "new_meetings.txt"
sound_file = "telephone-ring-01a.mp3"  # Using your audio file
num_loops = 10 # Number of times the audio file will loop

def get_last_checked_date():
    try:
        with open(last_checked_file, "r") as f:
            last_checked_str = f.read().strip()
            last_checked_naive = datetime.fromisoformat(last_checked_str)
            local_tz = zoneinfo.ZoneInfo('US/Central')
            return last_checked_naive.replace(tzinfo=local_tz)
    except FileNotFoundError:
        local_tz = zoneinfo.ZoneInfo('US/Central')
        now_aware = datetime.now(local_tz)
        return now_aware - timedelta(weeks=1)

def save_last_checked_date(date_obj):
    with open(last_checked_file, "w") as f:
        f.write(date_obj.isoformat())

def play_alert_sound():
    try:
        sound_path = Path(__file__).parent / sound_file
        if not sound_path.exists():
            print(f"Sound file not found: {sound_path}")
            return

        print(f"End audio loop early with ctrl-c.")
        pygame.mixer.init()
        for _ in range(num_loops):
            pygame.mixer.music.load(str(sound_path))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    except Exception as e:
        print(f"Error playing sound: {e}")
    except KeyboardInterrupt:
        return

def check_for_new_meetings():
    try:
        existing_entries = set()
        try:
            with open(new_meetings_file, "r") as f:
                existing_entries = {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            pass

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        last_checked = get_last_checked_date()
        new_meetings = []
        max_pub_date = None

        for item in items:
            title = item.find("title").text
            link = item.find("link").text

            if "council meeting" not in title.lower():
                continue

            pub_date_str = item.find("pubDate").text
            pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            pub_date = pub_date.astimezone(last_checked.tzinfo)

            if pub_date > last_checked:
                meeting_info = f"{title} - {pub_date.strftime('%a, %d %b %Y, %H:%M')} - {link}"
                
                if meeting_info in existing_entries or meeting_info in new_meetings:
                    continue

                new_meetings.append(meeting_info)
                existing_entries.add(meeting_info)
                print(f"NEW MEETING: {meeting_info}")

                if max_pub_date is None or pub_date > max_pub_date:
                    max_pub_date = pub_date

        if new_meetings:
            with open(new_meetings_file, "a") as outfile:
                outfile.write("\n".join(new_meetings) + "\n")
            
            if max_pub_date is not None:
                save_last_checked_date(max_pub_date)
            
            play_alert_sound()
            input("New meetings found! Press Enter to close this window...")
        else:
            print("No new meetings found")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    check_for_new_meetings()