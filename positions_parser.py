import time
import pytz

import requests
import datetime
import json

from requests.exceptions import ChunkedEncodingError

UU_URL = "http://bus03.ru/php/getVehiclesMarkers.php"
UU_ROUTE_IDS = "1-1,334-0,335-0,3-0,4-0,35-0,34-0,8-1,327-0,326-0,115-0,116-0,41-0,42-0,87-0,86-0,338-0,339-0,10-1,9-1,11-1,12-1,337-0,336-0,323-0,140-0,139-0,31-0,30-0,55-0,56-0,344-0,343-0,341-0,342-0,328-0,59-0,58-0,60-0,61-0,333-0,332-0,25-0,24-0,62-0,63-0,331-0,330-0,66-0,67-0,321-0,320-0,340-0,70-0,73-0,315-0,314-0,279-0,278-0,71-0,72-0,284-0,6-0,5-0,77-0,76-0,78-0,79-0,83-0,82-0,324-0,325-0,85-0,84-0,90-0,91-0,317-0,316-0,27-0,26-0,93-0,92-0,94-0,95-0,100-0,329-0,322-0,101-0,102-0,103-0,106-0,145-0,108-0,107-0,110-0,109-0,111-0,112-0,142-0,141-0,28-0,29-0,312-0,313-0,281-0,280-0,283-0,282-0,32-0,33-0,114-0,113-0"
UU_TRAM_ROUTE_IDS = "1-1,8-1,10-1,9-1,11-1,12-1"

IRK_URL = "http://irkbus.ru/php/getVehiclesMarkers.php"
IRK_ROUTE_IDS = "1-1,2-1,19-0,20-0,4-1,3-1,283-0,282-0,344-0,343-0,233-0,232-0,6-0,5-0,5-1,10-1,11-1,9-1,8-1,348-0,347-0,84-0,83-0,2-0,1-0,201-0,202-0,128-0,129-0,394-0,395-0,6-1,7-1,214-0,215-0,12-1,18-0,17-0,4-0,3-0,11-0,12-0,24-0,23-0,10-0,9-0,63-0,62-0,308-0,309-0,60-0,61-0,13-0,14-0,297-0,296-0,16-0,15-0,243-0,242-0,25-0,26-0,64-0,65-0,311-0,310-0,346-0,68-0,69-0,27-0,28-0,73-0,72-0,52-0,53-0,278-0,279-0,332-0,36-0,37-0,360-0,361-0,234-0,235-0,398-0,399-0,228-0,229-0,127-0,126-0,298-0,299-0,301-0,300-0,78-0,77-0,125-0,124-0,79-0,80-0,81-0,82-0,302-0,303-0,401-0,400-0,30-0,31-0,222-0,223-0,207-0,206-0,224-0,225-0,208-0,209-0,351-0,350-0,352-0,353-0,240-0,241-0,286-0,287-0,227-0,226-0,210-0,211-0,409-0,410-0,216-0,217-0,218-0,219-0,337-0,338-0,42-0,43-0,397-0,396-0,335-0,336-0,408-0,355-0,354-0,236-0,237-0,220-0,221-0,326-0,327-0,49-0,48-0,313-0,312-0,314-0,293-0,292-0,304-0,305-0,345-0,47-0,46-0,291-0,290-0,33-0,32-0,212-0,213-0,316-0,315-0,342-0,341-0,203-0,22-0,21-0,38-0,230-0,231-0,340-0,339-0,324-0,323-0,280-0,281-0,123-0,239-0,238-0,321-0,390-0,391-0,392-0,393-0,358-0,359-0,362-0,363-0,365-0,364-0,369-0,368-0,367-0,366-0,388-0,389-0,370-0,371-0,373-0,372-0,374-0,375-0,376-0,377-0,402-0,403-0,378-0,379-0,381-0,380-0,407-0,406-0,383-0,382-0,384-0,385-0,387-0,386-0,404-0,405-0,349-0,357-0,356-0,67-0,66-0,334-0,333-0"
IRK_TRAM_ROUTE_IDS = "1-1,2-1,4-1,3-1,5-1,10-1,11-1,9-1,8-1,6-1,7-1,12-1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Cookie": "PHPSESSID=1akttfiht1cp72uci06etsf4k0",
}


def get_vehicle_markers(output_file, routes, city, base_url):
    params = {
        'rids': routes,
        'lat0': 0,
        'lng0': 0,
        'lat1': 90,
        'lng1': 180,
        'curk': 2055019,
        'city': city,
        # 'info': "0123",
        # 'time': extended
    }

    data = {"datetime": datetime.datetime.now(pytz.timezone("Asia/Irkutsk")).strftime("%H:%M:%S %d-%M-%Y")}
    for i in range(10):
        try:
            response = requests.get(base_url, params=params, headers=HEADERS)
            break
        except ChunkedEncodingError:
            time.sleep(5)
            continue

    data.update(response.json())
    #data['response'].get("profiles")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def parse_markers_for_uu():
    for hour in range(9, 12):
        for i in range(180):
            print(hour, i)
            get_vehicle_markers(f"tram_positions/all_pos_{hour}_{i}.json", city="ulanude",
                                base_url=UU_URL, routes=UU_ROUTE_IDS)
            time.sleep(20)


def parse_markers_for_irk():
    for hour in range(9, 12):
        for i in range(180):
            print(hour, i)
            get_vehicle_markers(f"tram_positions_irk/all_pos_{hour}_{i}.json", city="irkutsk",
                                base_url=IRK_URL, routes=IRK_TRAM_ROUTE_IDS)
            time.sleep(20)

parse_markers_for_uu()
