import requests
import re
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# WORD## : leave unchanged
# WORD##-## : leave unchanged
# WORD-## : leave unchanged
# WORD-## / .. : WORD-##
# WORD ## : WORD-##

# Scrapes FAA Operations Advisory
url = "https://www.fly.faa.gov/adv/adv_spt"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text_orig = soup.get_text()

print(text_orig)

# Prune response to only include upcoming launches
purged = re.search(r'REENTRY:(.*)FLIGHT CHECK', text_orig, re.DOTALL)
if purged:
    launch_text = purged.group(1)

    # Formats dates into a JS friendly layout
    def formatDate(month, day, hour, min):
        return f"2026-{month}-{day}T{hour}:{min}:00Z"

    # Splits by newline (by launch)
    textL = launch_text.split("\n")
    carousel_data = []
    for i, line in enumerate(textL):
        # Gets only SpaceX launches (include Transporter and exclude Reentry advisories)
        if ("SPACEX" in line or "TRANSPORTER" in line) and "REENTRY" not in line:
            print(line)
            # Specifically cut out SPACEX if it's there
            if "SPACEX" in line:
                match = re.search(r'SPACEX ([^,]+),', line)
                mission = match.group(1)

                # Special format case for Starship flights
                if "STARSHIP" in mission:
                    flight_num = re.sub(r'[^0-9]', '', mission)
                    mission = f"Flight {flight_num}"
                else:
                    # WORD ##
                    if ' ' in mission:
                        word, number = mission.split(' ', 1)
                        # Only capitalize (not uppercase) words that aren't NASA or NROL
                        if word not in ["NASA", "NROL"] and "/" not in number:
                            # If the "number" is not truly a number, then capitalize
                            if number.isalpha():
                                mission = f"{word.capitalize()} {number.capitalize()}"
                            else:
                                mission = f"{word.capitalize()} {number}"
                        # WORD ## / .., remove characters past the /
                        elif " /" in number:
                            prune = re.search(r'([^,]+) /', number)
                            number = prune.group(1)
                            mission = f"{word}-{number}"
                        # WORD ##/..., remove characters past the /
                        elif "/" in number:
                            prune = re.search(r'([^,]+)/', number)
                            number = prune.group(1)
                            mission = f"{word}-{number}"

                        # Full caps
                        else:
                            # Special case add dash to NROL
                            if word == "NROL":
                                mission = f"{word}-{number.capitalize()}"
                            # Full caps word with number following
                            else:
                                mission = f"{word} {number.capitalize()}"

                    # WORD-##
                    elif '-' in mission:
                        # WORD-##/... -> WORD-##
                        if "/" in mission:
                            prune = re.search(r'([^,]+)/', mission)
                            mission = prune.group(1)
                        # WORD-## / ... -> WORD-##
                        elif " /" in mission:
                            prune = re.search(r'([^,]+) /', mission)
                            mission = prune.group(1)

            # Formatting for Transporter missions
            elif "TRANSPORTER" in line:
                match = re.search(r'([^,]+),', line)
                mission = match.group(1)
                word, number = mission.split('-')
                mission = f"{word.capitalize()}-{number}"

            text_split = textL[i+1].split("\t")
            date_split = text_split[1].split("/")
            window_open = text_split[2][0:4]
            window_close = text_split[2][6:10]

            current_time = datetime.now(timezone.utc).strftime('%m%d%H%M')
            close_time = date_split[0] + date_split[1] + str(window_close[0:4])
            
            if close_time > current_time:
                open_z = formatDate(date_split[0], date_split[1], window_open[0:2], window_open[2:4])
                close_z = formatDate(date_split[0], date_split[1], window_close[0:2], window_close[2:4])

                print(mission, open_z, close_z, sep='\n')
                carousel_data.append([open_z, close_z, mission])
                print("\n")

    print(carousel_data)
    with open('launches.json', 'w') as f:
        json.dump(carousel_data, f, indent=2)