import math


def distance(lat1, lon1, lat2, lon2): # generally used geo measurement function
    if lat1 > 10**6:
        lat1 = lat1/10**6
    if lon1 > 10 ** 6:
        lon1 = lon1/10**6
    if lat2 > 10 ** 6:
        lat2 = lat2/10**6
    if lon2 > 10 ** 6:
        lon2 = lon2/10**6

    R = 6378.137 # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000 # meters

# pos_to_meters(51829772, 107584201, 49982046, 107564452) vertical
# pos_to_meters(51829772, 107584201, 52284568, 104283160)

# 52.284568, 104.283160

def speed(lat1, lon1, lat2, lon2, time1, time2):
    distance = distance(lat1, lon1, lat2, lon2)
    tdelta = time2 - time1

    speed_mps = distance/tdelta.total_seconds()
    speed_kmh = (speed_mps*60*60)/1000
    return speed_kmh


def geographic_to_web_mercator(x_lon, y_lat):
    return lon_to_x_mercator(x_lon), lat_to_y_mercator(y_lat)


def lon_to_x_mercator(lon):
    num = lon * 0.017453292519943295 / 10**6
    x_mercator = 6378137.0 * num
    return x_mercator


def lat_to_y_mercator(lat):
    a = lat * 0.017453292519943295 / 10**6
    y_mercator = 3189068.5 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    return y_mercator


def speed_color(kmh):
    if kmh < 8:
        return "red"
    elif kmh < 18:
        return "yellow"
    else:
        return "green"