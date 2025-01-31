# Clyde Alert - Notification of new city council meetings

MIT license copywrite 2025, Bo Davidson. See included LICENSE.

## Installation:
1. [Install Python](https://www.python.org/downloads/) if you don't have it.

2. Git clone this repo: `git clone https://github.com/talzahr/clyde-alert.git` **OR** simply download the *meetings.py* and *requirements.txt* file from here.

3. `pip install -r requirements.txt` will install the *pygame* (mp3 audio) and *requests* depenencies.

## Run:
`python meetings.py`

On first run, it will detect anything that matches "*council meeting*" and save it to new_meetings.txt file, as well as a timestamp
in last_checked.txt file. Any subsequent runs will ignore a duplicate and play the notification sound and keep the console window
open. You need to provide your own audio file. Mine is not included do to licensing. 

# Best Use:**
Create an entry in the Windows Scheduler or a .service file on Linux (Systemd). Point to the *meetings.py* and run daily or more.
The console window will remain open when a new Council Meeting entry is found. 

Enjoy. 

