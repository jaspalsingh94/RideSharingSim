"""
Computes the centroids of the taxi zones for midtown only and midtown_downtown.
"""

import os
import json
from pathlib import Path
from shapely.geometry import MultiPolygon, Polygon

CURRENT_FILE_PATH = Path(__file__).parent.absolute()


def open_json_file(file_path: Path) -> dict:
    """
    Opens a json file and returns the dictionary
    """
    with open(file_path, 'r') as in_file:
        return json.load(in_file)


def main():
    """
    Main. Hard-coding paths for files.
    """
    midtown_file = CURRENT_FILE_PATH / ".." / "data" / "nyc_taxi_zone_midtown.geojson"
    midtown_downtown_file = (
        CURRENT_FILE_PATH / ".." / "data" / "nyc_taxi_zone_midtown_downtown.geojson"
    )
    midtown_feat = open_json_file(midtown_downtown_file)

    centroids = {}
    zone_ids = []
    print(list(midtown_feat))
    for mid_feat in midtown_feat["features"]:
        geom = mid_feat["geometry"]
        prop = mid_feat["properties"]
        obj_id = prop["objectid"]
        location_id = prop["location_id"]

        if obj_id != location_id:
            raise Exception(f"Object id does not match location id {obj_id} != {location_id}")
        centroid = Polygon(geom["coordinates"][0][0]).centroid
        centroids[location_id] = [centroid.x, centroid.y]
        zone_ids.append(location_id)
    print(f"Cenroids: {centroids}")
    print(f"Zone ids: {zone_ids}")
    with open("data/centroids_midtown_downtown.csv", 'w') as out_file:
        out_file.write("Long,Lat,ID\n")
        for centroid in centroids:
            out_file.write(f"{centroids[centroid][0]},{centroids[centroid][1]},{centroid}\n")



    # print(list(midtown_feat["features"][0]))
    # print(type(midtown_feat["features"][0]))
    # print(midtown_feat["features"][0]["geometry"]["coordinates"][0][0])

    # multi = Polygon(midtown_feat["features"][0]["geometry"]["coordinates"][0][0])
    # # print(list(multi.exterior.coords))
    # print(multi.area)
    # # for feat in midtown_feat["features"]:
    #     # print(len(feat))



main()