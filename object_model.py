import json
from generate_random import generate_pickup_zone, generate_dropoff_zone


class Customer:
    def __init__(self, id: int, arrival_time: float):
        self.name = id
        self.arrival = arrival_time
        self.pickup = generate_pickup_zone()
        self.dest = generate_dropoff_zone()