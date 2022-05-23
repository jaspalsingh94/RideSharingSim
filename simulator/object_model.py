import json
from generate_random import generate_pickup_zone, generate_dropoff_zone
from shapely.geometry import Point

ZONES = {
    "107": {
        "avg_dist": 436.0,
        "lon_lat": [-73.98405213268907, 40.73682405761877]
    },
    "234": {
        "avg_dist": 496.0,
        "lon_lat": [-73.99045782354737, 40.740337441756836]
    },
    "90": {
        "avg_dist": 404.0,
        "lon_lat": [-73.99697141558367, 40.74227862901209]
    },
    "164": {
        "avg_dist": 360.0,
        "lon_lat": [-73.98515639467685, 40.748574629356526]
    }
}

DISTANCES = {
    "107": {
        "234": 663.5,
        "90": 1258.9,
        "164": 1317.8
    },
    "234": {
        "107": 663.5,
        "90": 591.7,
        "164": 1014.9
    },
    "90": {
        "107": 1258.9,
        "234": 591.7,
        "164": 1229.4
    },
    "164": {
        "107": 1317.8,
        "234": 1014.9,
        "90": 1229.4
    }
}

class Customer:
    def __init__(self, id: int, arrival_time: float):
        self.name = id
        self.arrival = arrival_time
        self.pickup = generate_pickup_zone()
        self.dropoff = generate_dropoff_zone()

    def __repr__(self):
        return "name:" + str(self.name) + ", arrival: "+ str(self.arrival) + ", pickup:" + str(self.pickup) + " dropoff:" + str(self.dropoff) 
    def __str__(self):
        return "name:" + str(self.name) + ", arrival: "+ str(self.arrival) + ", pickup:" + str(self.pickup) + " dropoff:" + str(self.dropoff) 
      

class Zone:
    def __init__(self, id: int):
        self.id = id
        self.lon_lat = ZONES[id]["lon_lat"]
        self.avg_distance = ZONES[id]["avg_dist"]
        self.other_distance = DISTANCES[id]