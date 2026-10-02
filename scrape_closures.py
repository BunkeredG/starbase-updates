import requests
import re
import json
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# WORD##
# WORD##-##
# WORD-##

# text_orig = "Beach and Road AccessGovernment GovernmentCommission MeetingsC-4 AnnexationCity Commission And StaffCommission UpdatesOrdinancesElectionsContact UsEDCEDCApplicationsPermits & Inspections Permits & InspectionsApplication ChecklistsPermit PortalBeach & Road AccessCommunity & ExploreGovernmentCommission MeetingsC-4 AnnexationCity Commission And StaffCommission UpdatesOrdinancesElectionsContact UsEDCApplicationsPermits & InspectionsApplication ChecklistsPermit PortalBeach & Road AccessCommunity & ExploreBeach And Road AccessText “BEACH” TO 1-866-513-3475 to receive updates about beach access.BEACH Access StatusBoca Chica Beach is open.Road UpdatesNo Road Delay.Public Notice of Mayor's OrderPursuant to Mayor's Order No. 2026-22, issued by Mayor Bobby Peden and attested by City Clerk Keila Tuttle, under authority granted by Texas Space Commission Order No. 2025-02, Ordinance No. 2026-2, and the City's Emergency Management Plan,the City of Starbase is temporarily closing Boca Chica Beach, Texas State Highway 4 (from FM 1419/0klahoma Ave. to the beach entrance), and associated FAA hazard areas/Clear Zone to protect public health and safety during SpaceX spaceflight activities.‍Primary Closure Period9/24/26 from 6:00 AM to 6:00 PMAlternate Dates9/25/26 from 6:00 AM to 6:00 PMPrevious OrdersAugust 30, 2026Link to Executed OrderAugust 29, 2026Link to Executed OrderAugust 28, 2026Link to Executed OrderJuly 26, 2026Link to Executed OrderJuly 25, 2026Link to Executed OrderJuly 24, 2026Link to Executed OrderJuly 23, 2026Link to Executed OrderJuly 19, 2026Link to Executed OrderJuly 18, 2026Link to Executed OrderJuly 11, 2026Link to Executed OrderMay 23, 2026Link to Executed OrderMay 22, 2026Link to Executed OrderMay 19, 2026Link to Executed OrderMay 14, 2026Link to Executed OrderMay 9, 2026Link to Executed OrderMay 9, 2026Link to Executed OrderApril 17, 2026Link to Executed OrderApril 16, 2026Link to Executed OrderMarch 19, 2026Link to Executed OrderMarch 13, 2026Link to Executed OrderMarch 11, 2026Link to Executed OrderOTHER BEACHES TO VISITDuring closures, the public may visit alternative beaches on South Padre Island at Cameron County Beach Access No. 3, No.4, No. 4 (West), or No. 5 (West).Surf ReportWeather Conditions Beach Access PlanPublic NoticesCommunity & ExploreOpen Records Request"
# text = "BEACH Access StatusBoca Chica Beach closures.Primary: Aug. 27 6:30 AM to Aug. 27 9:00 PMPrimary: Aug. 28 6:30 AM to Aug. 28 9:00 PMRoad UpdatesRoad DelayNo road delays.Description: Production to PadDate: September 20 10:00 PM to September 21 2:00 AMDescription: Port to MasseysDate: September 20 11:59 PM to September 21 4:00 AM"

url = "https://www.starbase.texas.gov/beach-road-access"

def get_page():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text_orig = soup.get_text()
    pruned = re.search(r'access.(.+?)Public', text_orig)
    return text_orig, pruned.group(1)

samples = []
for i in range(3):
    samples.append(get_page())
    print(samples[i][1])
    if i < 2:
        time.sleep(0.2)

text_orig, text = samples[0]
for orig, t in samples:
    if "Primary" in re.search(r'BEACH Access Status(.+?)Road Updates', t).group(1):
        text_orig, text = orig, t
        break

now = datetime.now(timezone.utc).strftime('%-m%-d%y')
mayor_prune = re.search(r'Order(.+?)Previous', text_orig)
mayor_text = mayor_prune.group(1)
mayorL = []
if "Primary" not in mayor_text:
    mayorL.append("None")
else:
    mayorInter = mayor_text.split("Primary Closure Period")[1:]
    for order in mayorInter:
        mayor_re = re.search(r'(.*)Alternate', order)
        re_text = mayor_re.group(1)

        date_re = re.search(r'(.*) f', re_text)
        date_str = date_re.group(1)
        date_check = re.sub(r'[^0-9]', '', date_str)
        alt_date_check = date_str.split("/")

        if int(date_check) >= int(now) and int(alt_date_check[0]) >= int(datetime.now(timezone.utc).strftime('%-m')):
            mayorL.append(re_text)

    if mayorL == []:
        mayorL.append("None")

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
        closureL = closure.split("Date: ")
        closureL[0] = "->".join(closureL[0].split("to")) # production -> masseys

        # october 2nd
        closureL[1] = closureL[1].split(" ")
        for i, item in enumerate(closureL[1]):
            if item.isnumeric():
                if 10 <= int(item) % 100 <= 20:
                    suffix = "th"
                else:
                    suffix = {1: "st", 2: "nd", 3: "rd"}.get(int(item) % 10, "th")
                closureL[1][i] = f"{item}{suffix} at"
        closureL[1] = " ".join(closureL[1])

        roadL.append(closureL)

closures = []
closures.append(beachL)
closures.append(roadL)
closures.append(mayorL)
print(closures)
with open('closures.json', 'w') as f:
    json.dump(closures, f, indent=2)