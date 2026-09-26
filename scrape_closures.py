import requests
import re
import json
from bs4 import BeautifulSoup

# WORD##
# WORD##-##
# WORD-##

url = "https://www.starbase.texas.gov/beach-road-access"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text_orig = soup.get_text()
pruned = re.search(r'access.(.+?)Public', text_orig)
text = pruned.group(1)
# text = "BEACH Access StatusBoca Chica Beach closures.Primary: Aug. 27 6:30 AM to Aug. 27 9:00 PMPrimary: Aug. 28 6:30 AM to Aug. 28 9:00 PMRoad UpdatesRoad DelayNo road delays.Description: Production to PadDate: September 20 10:00 PM to September 21 2:00 AMDescription: Port to MasseysDate: September 20 11:59 PM to September 21 4:00 AM"
print(text)

beach_match = re.search(r'BEACH Access Status(.+?)Road Updates', text)
beach_text = beach_match.group(1)
beachL = []
if "Primary" not in beach_text:
    beachL.append("No beach closures")
else:
    beachInter = beach_text.split("Primary: ")[1:]
    for closure in beachInter:
        if "Backup:" in closure:
            beach_re = re.search(r'(.*?)Backup:', closure)
            beachL.append(beach_re.group(1))
        else:
            beachL.append(closure)

road_match = re.search(r'Road Updates(.*)', text)
road_text = road_match.group(1)
roadL = []
if "Description" not in road_text:
    roadL.append("No road closures")
else:
    roadInter = road_text.split("Description: ")[1:]
    for closure in roadInter:
        roadL.append(closure.split("Date: "))

closures = []
closures.append(beachL)
closures.append(roadL)
print(closures)
with open('closures.json', 'w') as f:
    json.dump(closures, f, indent=2)