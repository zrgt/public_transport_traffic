import datetime
from collections import OrderedDict, defaultdict
import json

from dataclasses import dataclass
from typing import List

import utils
from marker_namen import MARK_FILES, MARK_FILES_LIGHT

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
        self.positions[time] = Position(lon, lat, time)
        if len(self.positions) > 1:
            prev_pos_val = list(self.positions.values())[-2]
            speed = utils.speed(prev_pos_val.lat, prev_pos_val.lon, lat, lon, prev_pos_val.time, time)
            speed = round(speed, 1)
            self.positions[time].speed = speed
            self.positions[time].in_jam = True if (speed < JAM_SPEED and prev_pos_val.speed < JAM_SPEED) else False
            self.positions[time].secs_frm_lst_pos = (time - prev_pos_val.time).total_seconds()
            self.positions[time].meters_frm_lst_pos = utils.distance(prev_pos_val.lat, prev_pos_val.lon, lat, lon)

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
