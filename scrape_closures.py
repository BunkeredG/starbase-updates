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
    pruned = re.search(r'access.(.+?)Public', text_orig) # Search for road and beach closures (from "access." to "Public")
    return text_orig, pruned.group(1)

# Runs 3 sample tests to ensure correct data (sometimes Starbase's website removes the closure for a few seconds)
samples = []
for i in range(3):
    samples.append(get_page())
    print(samples[i][1])
    if i < 2:
        time.sleep(.15)

# Prefer any test that has a closure
text_orig, text = samples[0]
for orig, t in samples:
    if "Primary" in re.search(r'BEACH Access Status(.+?)Road Updates', t).group(1):
        text_orig, text = orig, t
        break

now = datetime.now(timezone.utc).strftime('%-m%-d%y') # Gets the current time (March 14 2027 is "31427")
mayor_prune = re.search(r'Order(.+?)Previous', text_orig) # Search for mayor's orders and removes previous orders
mayor_text = mayor_prune.group(1)
mayorL = []
if "Primary" not in mayor_text:
    mayorL.append("None") # "None" if there are no active orders
else:
    mayorInter = mayor_text.split("Primary Closure Period")[1:] # Takes text after the string "Primary Closure Period"

    # Ensures that the order has not been revoked
    if "Revocation" not in mayorInter[0]:
        # Gets only the active date, ignoring alternates
        mayor_re = re.search(r'(.*)Alternate', mayorInter[0])
        re_text = mayor_re.group(1)

        # Gets only the alternate date
        alt_mayor_re = re.search(r'Alternate Dates(.*)', mayorInter[0])
        alt_re_text = alt_mayor_re.group(1)

        # Gets only the date, "10/24/26 from ..." -> "10/24/26"
        date_re = re.search(r'(.*) f', re_text)
        date_str = date_re.group(1)
        # Makes date comparable by removing everything except integers
        date_check = re.sub(r'[^0-9]', '', date_str)
        ls_date_check = date_str.split("/")

        # Exact same thing for the alternate date
        alt_date_re = re.search(r'(.*) f', alt_re_text)
        alt_date_str = alt_date_re.group(1)
        alt_date_check = re.sub(r'[^0-9]', '', alt_date_str)
        alt_ls_date_check = alt_date_str.split("/")

        # Checks the current date vs the order date as an int (102426 > 102326) to determine whether the order is outdated or not
        # Since 103126 > 11326 (despite 11/3/26 being after 10/31/26), months are compared on their own as well.
        # Since 123126 > 1127 and 12 > 1, years are compared on their own as well.
        # Note the strict inequality as if the months & years are the same then the straight date comparison will be accurate.
        current_month = int(datetime.now(timezone.utc).strftime('%-m'))
        current_year = int(datetime.now(timezone.utc).strftime("%y"))
        if int(date_check) >= int(now) or int(ls_date_check[0]) > current_month or int(ls_date_check[2]) > current_year:
            mayorL.append(re_text)
        elif int(alt_date_check) >= int(now) or int(alt_ls_date_check[0]) > current_month or int(ls_date_check[2]) > current_year:
            mayorL.append(alt_re_text)

    # If the list of active mayor's orders remains empty after this, append "None"
    if mayorL == []:
        mayorL.append("None")

# Prunes text for only beach closures
beach_match = re.search(r'BEACH Access Status(.+?)Road Updates', text)
beach_text = beach_match.group(1)
beachL = []
if "Primary" not in beach_text:
    beachL.append("No beach closures")
else:
    beachInter = beach_text.split("Primary: ")[1:] # Splits to obtain only the exact beach closures
    for closure in beachInter:
        # Ensure the list only has the primary dates not the backups (as that would make the date string look weird)
        if "Backup:" in closure:
            beach_re = re.search(r'(.*?)Backup:', closure)
            beachL.append(beach_re.group(1))
        else:
            beachL.append(closure)

# Prunes text for only road closures
road_match = re.search(r'Road Updates(.*)', text)
road_text = road_match.group(1)
roadL = []
if "Description" not in road_text:
    roadL.append("No road closures")
else:
    roadInter = road_text.split("Description: ")[1:] # Splits to obtain only the exact road closures
    for closure in roadInter:
        closureL = closure.split("Date: ") # One side is description (Production to Massey's), other is date (October 4th ...)
        closureL[0] = "➜".join(closureL[0].split("to")) # "Production to Masseys" to "Production ➜ Masseys"

        # corrects punctuation
        closureL[0] = closureL[0].split(" ") # ["Production", "➜", "Masseys"]
        for i, item in enumerate(closureL[0]):
            if item == "Masseys":
                closureL[0][i] = "Massey's"
        closureL[0] = " ".join(closureL[0])

        # adds ordinals
        closureL[1] = closureL[1].split(" ") # ["October", "4", "10:00", "AM", ...]
        for i, item in enumerate(closureL[1]):
            if item.isnumeric(): # "4" passes, "not" doesn't, "10:00" doesn't
                if 10 <= int(item) % 100 <= 20: # if item ends in 10-20 add "th"
                    suffix = "th"
                else:
                    # gets item's ending digit, if it matches 1, 2, or 3, add appropriate ordinal, otherwise, add "th"
                    suffix = {1: "st", 2: "nd", 3: "rd"}.get(int(item) % 10, "th")
                closureL[1][i] = f"{item}{suffix} at" # combine number and ordinal, add "at" for easier reading
        closureL[1] = " ".join(closureL[1]) # re-join the list back into a string

        roadL.append(closureL)

closures = []
closures.append(beachL)
closures.append(roadL)
closures.append(mayorL)
print(closures)
with open('closures.json', 'w') as f:
    json.dump(closures, f, indent=2)