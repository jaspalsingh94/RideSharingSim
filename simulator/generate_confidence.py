import json
import scipy.stats as st
import numpy as np


"""
        shared_rejected_customer,
        no_shared_rejected_customer,
        shared_meters,
        no_shared_meters,
        customer_count,
        time_shared,
        time_no_shared
"""

def generate_95_confidence(data: list):
    """
    """
    return st.t.interval(alpha=0.95, df=len(data)-1,
              loc=np.mean(data),
              scale=st.sem(data))

def generate_confidence_intervals():
    json_in = {}
    with open("data/simulated_trips.json", 'r') as open_json:
        json_in = json.load(open_json)
        for trip in json_in:
            shared_rejected_ci = generate_95_confidence(json_in[trip][0])
            no_shared_rejected_ci = generate_95_confidence(json_in[trip][1])
            customers = generate_95_confidence(json_in[trip][4])
            shared_time_ci = generate_95_confidence(json_in[trip][5])
            no_shared_time_ci = generate_95_confidence(json_in[trip][6])

            print(f"Shared rejected: {shared_rejected_ci}, +- {(shared_rejected_ci[1] - shared_rejected_ci[0]) / 2}")
            print(f"No shared rejected: {no_shared_rejected_ci}, +- {(no_shared_rejected_ci[1] - no_shared_rejected_ci[0]) / 2}")
            print(f"shared_time: {shared_time_ci} +- {(shared_time_ci[1] - shared_time_ci[0]) / 2}")
            print(f"No shared time: {no_shared_time_ci} +- {(no_shared_time_ci[1] - no_shared_time_ci[0]) / 2}")
            print(f"Customers: {customers}, +- {(customers[1] - customers[0]) / 2}")
            print("-----------------------------------------------------\n")

def generate_ci_meters():
    json_in = {}
    with open("data/simulated_trips.json", 'r') as open_json:
        json_in = json.load(open_json)
        for trip in json_in:
            shared_meter_data = []
            no_shared_meter_data = []
            for shared_meter, no_shared_meter, rejected_custmer, customer in zip(json_in[trip][2], json_in[trip][3], json_in[trip][0],json_in[trip][4]):
                shared_meter_data.append(shared_meter / (customer-rejected_custmer))
            for shared_meter, no_shared_meter, rejected_custmer, customer in zip(json_in[trip][2], json_in[trip][3], json_in[trip][1],json_in[trip][4]):
                no_shared_meter_data.append(no_shared_meter / (customer-rejected_custmer))

            shared_meter_data_ci = generate_95_confidence(shared_meter_data)
            no_shared_meter_data_ci = generate_95_confidence(no_shared_meter_data)

            print(f"shared_meter_data: {shared_meter_data_ci}, +- {(shared_meter_data_ci[1] - shared_meter_data_ci[0]) / 2}")
            print(f"no_shared_meter_data: {no_shared_meter_data_ci}, +- {(no_shared_meter_data_ci[1] - no_shared_meter_data_ci[0]) / 2}")

#generate_confidence_intervals()
generate_ci_meters()