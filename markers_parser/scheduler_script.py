import datetime

import pytz
import schedule
import time

from markers_parser.positions_parser import get_vehicle_markers, UU


def get_vehicle_markers_for_uu():
    now = datetime.datetime.now(pytz.timezone("Asia/Irkutsk"))
    get_vehicle_markers(f"markers_uu/markers_{now.hour}_{now.minute}_{now.second}.json",
                        city=UU["city"],
                        base_url=UU["url"],
                        routes=UU["tram_route_ids"])
    print(f"Got markers: {now.hour}:{now.minute}")


def parse(start_hour=6, end_hour=22, delta_sec=30):
    # irkutsk time
    now = datetime.datetime.now(pytz.timezone("Asia/Irkutsk"))
    if now.hour >= start_hour:
        schedule.every(delta_sec).seconds.do(get_vehicle_markers_for_uu)
        # Loop so that the scheduling task
        # keeps on running all time.
        while True:
            # Checks whether a scheduled task
            # is pending to run or not
            schedule.run_pending()
            time.sleep(1)
            now = datetime.datetime.now(pytz.timezone("Asia/Irkutsk"))
            if now.hour >= end_hour:
                break

parse(12, 13)
