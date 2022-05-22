"""
Utilities for running soda api queries to get the data from open nyc data.
"""
import os
import json
from sodapy import Socrata
from pathlib import Path
from datetime import datetime
from matplotlib import pyplot
from sqlalchemy import sql, Table, MetaData
from sqlalchemy import create_engine, func
import scipy.stats as st

SODA_TOKEN = "OYDc2QFddRUsFWLu19VnHnTp3"
# ZONE_IDS = ["90", "100", "107", "137", "164", "170", "186", "234"]
ZONE_IDS = ["107", "234", "90", "164"]

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


class DataGenerator:
    def __init__(self, debug=False):
        self.dataset_id = "rebk-rr49"
        self.soda_client = Socrata("data.cityofnewyork.us", SODA_TOKEN)
        self.pg_url = "postgresql://postgres:hunter2022@database-1.cpwa86v6hjzb.ap-northeast-2.rds.amazonaws.com:5432"
        self.engine = create_engine(self.pg_url, echo=debug, echo_pool=debug, future=True)
        self.metadata = MetaData(bind=self.engine)

    def get_filtered_location(
        self,
        pickup_id: int,
        dropoff_id: int,
        where_clause: str = "date_extract_hh(pickup_datetime) between 6 and 20",
        select_clause: str = "pickup_datetime, dropoff_datetime, pulocationid, dolocationid",
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


    # @staticmethod
    # def compute_inter_arrival_time(trip, previous_trip) -> float:
    #     """
    #     Returns the inter-arrival time between 2 trips.
    #     """
    #     first = datetime.strptime(trip["pickup_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
    #     second = datetime.strptime(previous_trip["pickup_datetime"], "%Y-%m-%dT%H:%M:%S.%f")
    #     time_diff = (second - first).total_seconds()
    #     return time_diff


    def populate_arrival_times(self):
        """
        Populates the inter_arrival_times_day_time table by calculting the values
        from the trip data table.
        """
        trip_data_table = Table("trip_data_day_time", self.metadata, autoload_with=self.engine)
        inter_arrival_table = Table("inter_arrival_times_day_time", self.metadata, autoload_with=self.engine)
        with self.engine.connect() as conn:
            select_statement = sql.select(trip_data_table.c.pulocationid, trip_data_table.c.pickup_datetime).order_by("pickup_datetime")
            select_result = conn.execute(select_statement)
            previous_datetime = select_result.fetchone()

            arrivals = []
            for result in select_result:
                delta = (result[1] - previous_datetime[1]).total_seconds()
                arrivals.append({"zone_id": result[0], "inter_arrival_time": delta})
                previous_datetime = result
            
            conn.execute(inter_arrival_table.insert(), arrivals)
            conn.commit()




    def generate_travel_time_hist(self, zone_ids: list, output_folder: str):
        """
        Generates the travel time histograms for each zone - zone trip.
        """
        out_path = Path(output_folder)
        make_dirs(out_path)

        travel_time_table = Table("travel_times_day_time", self.metadata, autoload_with=self.engine)
        travel_time_dists = {}
        with self.engine.connect() as conn:
            for start_zone in ZONE_IDS:
                if start_zone not in travel_time_dists:
                    travel_time_dists[start_zone] = {}
               
                for end_zone in ZONE_IDS:

                    select_statement = travel_time_table.select().where(sql.and_(travel_time_table.c.pulocationid == start_zone, travel_time_table.c.dolocationid == end_zone)).order_by("travel_time")
                    select_result = conn.execute(select_statement)
                    travel_times = [result["travel_time"] for result in select_result]
                    one_perc = int(len(travel_times) * 0.02)
                    travel_times = travel_times[one_perc:-one_perc]

                    print("\n\n-----------------------------------------------------------------------")
                    print(f"Generating PDF for travel time between Zones {start_zone} - {end_zone}")
                    print(f"Sample Count: {len(travel_times)}")

                    output_file = out_path / f"travel_time_{start_zone}_{end_zone}.png"
                    best_name, best_params = self.get_best_fit(travel_times, output_file)
                    print(f"Best Fit returned: {best_name}")
                    print(f"Dist Params: {best_params}")
                    

                    travel_time_dists[start_zone][end_zone] = {
                        "dist_name": best_name,
                        "dist_params": best_params,
                        "sample_count": len(travel_times)
                    }

        print(f"\n\nTravel Time Distributions: {travel_time_dists}")
        dist_json = out_path / "travel_time_distributions.json"
        with open(dist_json, 'w') as out_json:
            json.dump(travel_time_dists, out_json)

        self.print_dist_zones_info(travel_time_dists)



    def generate_arrival_time_dist(self, zone_ids: list, output_folder: str):
        """
        Generates the probabilities and the distribution for inter-arrival time.
        """
        out_path = Path(output_folder)
        make_dirs(out_path)

        zone_probs = {}
        inter_arrival_table = Table("inter_arrival_times_day_time", self.metadata, autoload_with=self.engine)
        total_count = 0
        with self.engine.connect() as conn:
            for zone_id in zone_ids:
                select_statement = sql.select(func.count(inter_arrival_table.c.id)).where(inter_arrival_table.c.zone_id == zone_id) 
                select_result = conn.execute(select_statement).fetchall()
                zone_probs[zone_id] = {"count": select_result[0][0]}
                total_count = total_count + select_result[0][0]

        for zone_id in zone_probs:
            prob = float(zone_probs[zone_id]["count"]) / float(total_count)
            zone_probs[zone_id]["prob"] = prob

        with self.engine.connect() as conn:
            arrivals = []
            for zone_id in zone_ids:
                select_statement = inter_arrival_table.select().where(inter_arrival_table.c.zone_id == zone_id)
                select_result = conn.execute(select_statement)
                for arrival in select_result:
                    if arrival["inter_arrival_time"] < 3600 and arrival["inter_arrival_time"] > 0.001:
                        arrivals.append(arrival["inter_arrival_time"])
            # arrivals = [arrival["inter_arrival_time"] for arrival in select_result if arrival["inter_arrival_time"] < 3600 and arrival["inter_arrival_time"] > 0.001]
            total_arrival_count = len(arrivals)
            print(f"Total arrival count: {total_arrival_count}")

            output_file = out_path / "inter_arrival_times.png"

            best_name, best_params = self.get_best_fit(arrivals, output_file, dist_names=["expon"])
            print(f"Best fit: {best_name}")

        inter_arrival = {
            "zone_probs": zone_probs, 
            "dist_name": best_name,
            "dist_params": best_params,
            "sample_count": total_arrival_count
        }

        print(f"Inter arrivals: {inter_arrival}")

        output_json = out_path / "inter_arrival.json"
        with open(output_json, "w") as out_json:
            json.dump(inter_arrival, out_json)


    @staticmethod
    def get_best_fit(samples: list, output_file: Path, dist_names = ["gamma", "lognorm"]):
        """
        Returns the best fit PDF for the sample data.
        """
        dist_params = {}
        dist_scores = []
        for dist_name in dist_names:
            this_dist = getattr(st, dist_name)
            param = this_dist.fit(samples)
            dist_params[dist_name] = param

            d_value, p_value = st.kstest(samples, dist_name, args=param)
            dist_scores.append([dist_name, d_value, p_value])
        # print(f"Dist params: {dist_params}")
        # print(f"Dist scores: {dist_scores}")
        best_fit = min(dist_scores, key=lambda item: item[1])[0]
        print(f"Best fit 1: {best_fit}")

        fig, ax = pyplot.subplots()
        n, bins, _ = ax.hist(samples, bins=40, density=True, label="sample data")

        best_dist = getattr(st, best_fit)
        if best_fit == "expon":
            best_fit_pdf = best_dist.pdf(bins, dist_params[best_fit][0], dist_params[best_fit][1])
        else:
            best_fit_pdf = best_dist.pdf(bins, dist_params[best_fit][0], dist_params[best_fit][1], dist_params[best_fit][2])

        
        ax.plot(bins, best_fit_pdf, label=f"{best_fit} PDF")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Frequency (density)")
        ax.set_title("Comparison of the sample Histogram and generated PDF")
        ax.legend()
        pyplot.savefig(output_file)
        print(f"Wrote plots to file: {output_file}")
        # pyplot.show()

        return best_fit, dist_params[best_fit]


    @staticmethod
    def print_dist_zones_info(travel_time_dists: dict):
        """
        Prints some info about the travel time distributions.
        """
        dist_to_zones = {}
        for start_zone in travel_time_dists:
            for end_zone in travel_time_dists[start_zone]:
                dist_name = travel_time_dists[start_zone][end_zone]["dist_name"]
                if dist_name not in dist_to_zones:
                    dist_to_zones[dist_name] = []
                dist_to_zones[dist_name].append([start_zone, end_zone])
        
        for dist_name in dist_to_zones:
            print(f"Zone count for distribution {dist_name}: {len(dist_to_zones[dist_name])}")

        for dist_name in dist_to_zones:
            print(f"\nZones for distribution {dist_name}: {dist_to_zones[dist_name]}")


def main():
    """
    Main.
    """
    output_path = "data/dist_small/"
    data_gen = DataGenerator()
    # data_gen.generate_travel_time_hist(ZONE_IDS, output_path)
    # data_gen.populate_arrival_times()
    data_gen.generate_arrival_time_dist(ZONE_IDS, "data/dist_small")

    # for pickup in ZONE_IDS:
    #     for dropoff in ZONE_IDS:
            # this_trip = soda_api.get_filtered_location(pickup, dropoff)
            # # print(this_trip[0])

            # trip_data_table = Table('trip_data_day_time', soda_api.metadata, autoload_with=soda_api.engine)
            # with soda_api.engine.connect() as conn:
            #     print(f"Writing {len(this_trip)} rows to the database")
            #     conn.execute(trip_data_table.insert(), this_trip)
            #     conn.commit()




            

main()
