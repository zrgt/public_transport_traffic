import datetime
from collections import OrderedDict, defaultdict
import json

from dataclasses import dataclass

import utils


class Auto:
    def __init__(self, id):
        self.id = id
        self.positions: OrderedDict[datetime.date, Position] = OrderedDict()

    def append_position(self, lon, lat, time: str):
        time = datetime.datetime.strptime(time, "%d.%m.%Y %H:%M:%S")
        self.positions[time] = Position(lon, lat, time)
        if len(self.positions) > 1:
            prev_pos_val = list(self.positions.values())[-2]
            speed = utils.speed(prev_pos_val.lon, prev_pos_val.lat, lon, lat, prev_pos_val.time, time)
            self.positions[time].speed = speed
            old_speed = self.positions[prev_pos_val.time].speed
            self.positions[prev_pos_val.time].speed = (speed+old_speed)/2

    def speed(self, time: str):
        time = datetime.datetime.strptime(time, "%d.%m.%Y %H:%M:%S")
        return self.positions[time].speed


@dataclass
class Position:
    lon: int
    lat: int
    time: datetime.time
    speed: float = 0.0

def generate_auto_positions(n=120):
    autos = defaultdict()

    for i in range(n):
        print(i)
        with open(f"tram_positions/tram_pos_{i}.json", "r") as file:
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


def generate_file():
    autos = generate_auto_positions(80)
    final_dict = defaultdict()

    for i in range(80):
        print(i)
        with open(f"tram_positions/tram_pos_{i}.json", "r") as file:
            full_dict = json.load(file)
            autos_dict = full_dict["anims"]
        for auto in autos_dict:
            auto["speed"]=autos[auto["id"]].speed(time=auto["lasttime"])
        final_dict[i] = autos_dict
    with open("all_pos.json", "w") as file:
        json.dump(final_dict, file, ensure_ascii=False)

generate_file()