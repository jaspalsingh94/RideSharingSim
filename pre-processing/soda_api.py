"""
Utilities for running soda api queries to get the data from open nyc data.
"""
import os
from sodapy import Socrata
import json
from pathlib import Path
from datetime import datetime
from matplotlib import pyplot

SODA_TOKEN = "OYDc2QFddRUsFWLu19VnHnTp3"
ZONE_IDS = ["90", "100", "107", "137", "164", "170", "186", "234"]

MIDTOWN_DOWNTOWN_IDS = [
    "4",
    "12",
    "13",
    "45",
    "48",
    "50",
    "68",
    "79",
    "87",
    "88",
    "90",
    "125",
    "100",
    "107",
    "113",
    "114",
    "137",
    "144",
    "148",
    "158",
    "161",
    "162",
    "163",
    "164",
    "170",
    "186",
    "209",
    "211",
    "224",
    "229",
    "230",
    "231",
    "232",
    "233",
    "234",
    "246",
    "249",
    "261",
]

def make_dirs(dir_path: Path):
    """
    Creates a directory if it doesnt exist.
    """
    if not dir_path.exists():
        os.makedirs(dir_path)


class SodaApi:
    def __init__(self):
        self.dataset_id = "rebk-rr49"
        self.soda_client = Socrata("data.cityofnewyork.us", SODA_TOKEN)

    def get_filtered_location(
        self,
        pickup_id: int,
        dropoff_id: int,
        where_clause: str = "date_extract_hh(pickup_datetime) between 6 and 20",
        select_clause: str = "hvfhs_license_num, pickup_datetime, dropoff_datetime",
    ) -> dict:
        """
        Returns the data back with fitlering on pickup and drop of location.
        If where clause is provided then it is used.
        """
        trip_data = self.soda_client.get(
            self.dataset_id,
            limit=50000,
            where=where_clause,
            pulocationid=pickup_id,
            dolocationid=dropoff_id,
            sr_flag=None,
            select=select_clause,
            order="pickup_datetime"
        )
        print(
            f"Got {len(trip_data)} trip data rows for pickup id {pickup_id} and dropoff id {dropoff_id}"
        )
        return trip_data


    def generate_arrival_and_travel_time(self, trip_data: dict, output_folder: Path, dropoff_id: int):
        """
        Generates the distribution for inter-arrival times and the travel times.
        """
        inter_arrival = []
        travel = []
        travel.append(self.compute_travel_time[trip_data[0]])
        for i, trip in enumerate(trip_data[1:]):
            travel.append(self.compute_travel_time(trip))
            inter_arrival.append(self.compute_inter_arrival_time(trip, trip_data[i - 1])
        out_file_travel = output_folder / f"{dropoff_id}_travel.png"
        out_file_arrival = output_folder / f"{dropoff_id}_arrival.png"
        make_dirs(out_file_travel)
        make_dirs(out_file_arrival)
        self.save_histogram_plot(travel, out_file_travel)
        self.save_histogram_plot(inter_arrival, out_file_arrival)


    @staticmethod
    def compute_travel_time(trip: json) -> float:
        """
        Returns the travel time for this trip.
        """
        start = datetime.strptime(trip["pickup_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
        end = datetime.strptime(trip["dropoff_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
        duration = (end - start).total_seconds()
        return duration


    @staticmethod
    def compute_inter_arrival_time(trip, previous_trip) -> float:
        """
        Returns the inter-arrival time between 2 trips.
        """
        first = datetime.strptime(trip["pickup_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
        second = datetime.strptime(previous_trip["pickup_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
        time_diff = (second - first).total_seconds()
        return time_diff

    @staticmethod
    def save_histogram_plot(plt_data: list, output_file: Path):
        """
        Saves the histograms to file.
        """
        


def main():
    """
    Main.
    """
    zone_ids = [234, 107]
    soda_api = SodaApi()
    for pickup in zone_ids:
        for dropoff in zone_ids:
            this_trip = soda_api.get_filtered_location(pickup, dropoff)



            sys.exit()

            

main()
