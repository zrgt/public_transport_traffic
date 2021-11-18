import datetime
from collections import OrderedDict, defaultdict
import json

from dataclasses import dataclass
from typing import List

import utils
from marker_namen import MARK_FILES

JAM_SPEED = 8

@dataclass
class Position:
    lon: int
    lat: int
    time: datetime.time
    speed: float = 0.0
    secs_frm_lst_pos = 0
    meters_frm_lst_pos = 0
    in_jam = False


class Auto:
    def __init__(self, id):
        self.id = id
        self.positions: OrderedDict[datetime.date, Position] = OrderedDict()

    def append_position(self, lon, lat, time: str):
        time = datetime.datetime.strptime(time, "%d.%m.%Y %H:%M:%S")
        pos = Position(lon, lat, time)
        self.positions[time] = pos
        if len(self.positions) > 2:
            prev_pos = list(self.positions.values())[-2]
            prev_prev_pos = list(self.positions.values())[-3]

            pos.secs_frm_lst_pos = (time - prev_pos.time).total_seconds()
            pos.meters_frm_lst_pos = utils.distance(prev_pos.lat, prev_pos.lon, lat, lon)
            pos.speed = round(utils.speed(prev_pos.lat, prev_pos.lon, lat, lon, prev_pos.time, time), 1)

            if pos.speed < JAM_SPEED and prev_pos.speed < JAM_SPEED and pos.secs_frm_lst_pos > 50:
                pos.in_jam = True
                prev_pos.in_jam = True
            if pos.speed < JAM_SPEED and prev_pos.speed < JAM_SPEED and prev_prev_pos.speed < JAM_SPEED:
                pos.in_jam = True
                prev_pos.in_jam = True
                prev_prev_pos.in_jam = True
            else:
                pos.in_jam = False

    def position(self, time: str):
        time = datetime.datetime.strptime(time, "%d.%m.%Y %H:%M:%S")
        return self.positions[time]


def generate_auto_positions(folder:str, files:List[str]):
    autos = defaultdict()

    for n, filename in enumerate(files):
        print(n, filename)
        with open(f"{folder}/{filename}", "r") as file:
            a = json.load(file)
            autos_dict = a["anims"]
        for i in autos_dict:
            try:
                auto: Auto = autos[i["id"]]
            except KeyError:
                autos[i["id"]] = Auto(i["id"])
                auto: Auto = autos[i["id"]]
            auto.append_position(i["lon"], i["lat"], i["lasttime"])
    return autos


def generate_file(folder:str, files:List[str]):
    autos = generate_auto_positions(folder, files)
    final_dict = defaultdict()

    for n, filename in enumerate(files):
        print(n, filename)
        with open(f"{folder}/{filename}", "r") as file:
            full_dict = json.load(file)
            autos_dict = full_dict["anims"]
        for auto in autos_dict:
            position: Position = autos[auto["id"]].position(time=auto["lasttime"])
            auto["speed"] = position.speed
            auto["in_jam"] = position.in_jam
            auto["secs_frm_lst_pos"] = position.secs_frm_lst_pos
            auto["meters_frm_lst_pos"] = position.meters_frm_lst_pos
        final_dict[n] = autos_dict
    with open("all_pos.json", "w") as file:
        json.dump(final_dict, file, ensure_ascii=False)


generate_file(folder="markers_parser/markers_uu", files=MARK_FILES)
