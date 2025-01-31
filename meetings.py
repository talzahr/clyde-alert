import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# URL of the website
url = "https://www.clyde-tx.gov/"

# File to store last checked date
last_checked_file = "last_checked.txt"

def get_last_checked_date():
    """Retrieves the last checked date from file or sets it to a week ago."""
    try:
        with open(last_checked_file, "r") as f:
            last_checked_str = f.read().strip()
            return datetime.fromisoformat(last_checked_str)
    except FileNotFoundError:
        return datetime.now() - timedelta(weeks=1)  # Default to a week ago if no file

def save_last_checked_date(date_obj):
    """Saves the last checked date to a file in ISO format."""
    with open(last_checked_file, "w") as f:
        f.write(date_obj.isoformat())


def check_for_new_meetings():
    """Checks for new council meetings and saves them to a file."""

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, "html.parser")
        meeting_items = soup.find_all("li", class_=lambda x: x and "views-row" in x) # Added views-row class selector to ensure only meeting items are included

        last_checked = get_last_checked_date()
        new_meetings = []

        for item in meeting_items:
            title_element = item.find("span", class_="field-content") # Using find instead of select_one to handle cases when no matching tag is found. select_one will throw an error
            title = title_element.find("a").text if title_element else None  # Ensuring title_element is not None

            if title and re.search(r"council\smeeting", title, re.I):  # Case-insensitive search for "Council Meeting"
                date_str = item.find("time", class_="datetime")["datetime"]
                meeting_date = datetime.fromisoformat(date_str[:-6]) # Removing the timezone offset info

                if meeting_date > last_checked:
                    link = item.find('a', href=True)
                    full_link = url.rstrip('/') + link["href"]  # Ensure no double slashes, handle trailing slash in base url.
                    meeting_info = f"{title} - {item.find('time').text} - {full_link}"
                    new_meetings.append(meeting_info)

        if new_meetings:
            with open("new_meetings.txt", "a") as outfile:
                for meeting in new_meetings:
                    outfile.write(meeting + "\n")

        save_last_checked_date(datetime.now())


    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    check_for_new_meetings()
    print("Checked for new meetings!")