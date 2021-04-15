import json
import matplotlib.pyplot as plt

with open("positions.json", "r") as file:
    a=json.load(file)
    trams = a["anims"]

for tram in trams:
    lons = tuple(tram["lon"] for tram in trams)
    lats = tuple(tram["lat"] for tram in trams)
# plotting points as a scatter plot
plt.scatter(lons, lats, label= "stars", color="green", marker= "*", s=30)


for r_num in (1,2,4,5):
    with open(f"tram_routes/route_{r_num}.json", "r") as file:
        route=json.load(file)
    r_lons = tuple(point["lng"] for point in route)
    r_lats = tuple(point["lat"] for point in route)
    plt.scatter(r_lons, r_lats, label="4", color="red", marker= ".", s=30)

# naming the x axis
plt.xlabel('x - axis')
# naming the y axis
plt.ylabel('y - axis')

# giving a title to my graph
plt.title('Trams')

# function to show the plot
plt.show()

print("Finish")


transport_types = {"М": 0, "Тр": 1}

base = "http://bus03.ru/php/getVehiclesMarkers.php"
route_ids = "?rids=1-1,8-1,10-1,9-1,11-1,12-1"
frame = "&lat0=0&lng0=0&lat1=90&lng1=180"
curk = "&curk=4606611" #?
city = "&city=ulanude"
info = "&info=0123" #? probably types of transport
time = "&_=1618225211619"
