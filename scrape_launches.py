import requests
import re
import json
from bs4 import BeautifulSoup

# WORD##
# WORD##-##
# WORD-##

url = "https://www.fly.faa.gov/adv/adv_spt"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text_orig = soup.get_text()

def formatDate(month, day, hour, min):
    return f"2026-{month}-{day}T{hour}:{min}:00Z"

textL = text_orig.split("\n")
carousel_data = []
for i, line in enumerate(textL):
    if "SPACEX" in line and "REENTRY" not in line:
        print(line)
        match = re.search(r'SPACEX ([^,]+),', line)
        mission = match.group(1)

        if "STARSHIP" in mission:
            flight_num = re.sub(r'[^0-9]', '', mission)
            mission = f"Flight {flight_num}"
        else:
            if ' ' in mission:
                word, number = mission.split(' ', 1)
                if number.isalpha():
                    mission = f"{word.capitalize()} {number.capitalize()}"
                else:
                    mission = f"{word.capitalize()} {number}"

        text_split = textL[i+1].split("\t")
        date_split = text_split[1].split("/")
        window_open = text_split[2][0:4]
        window_close = text_split[2][6:10]


        open_z = formatDate(date_split[0], date_split[1], window_open[0:2], window_open[2:4])
        close_z = formatDate(date_split[0], date_split[1], window_close[0:2], window_close[2:4])

        print(mission, open_z, close_z, sep='\n')
        carousel_data.append([open_z, close_z, mission])
        print("\n")

print(carousel_data)
with open('launches.json', 'w') as f:
    json.dump(carousel_data, f, indent=2)