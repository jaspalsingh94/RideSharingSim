
import json
from simul_shared import simulation_test
from generate_customers import generate_customer_list
from statistics import mean
import time

# customers = generate_customer_list(size=500)

# result = simulation_test(
#     list(customers),
#     customer_limit=1,
#     wait_limit=900,
#     VEHICLE_NUM_PER_ZONE=1,
#     printB=False,
# )
# if result:
#     print(result)

# result = simulation_test(
#     list(customers),
#     customer_limit=1,
#     wait_limit=900,
#     VEHICLE_NUM_PER_ZONE=4,
#     printB=False,
# )
# if result:
#     print(result)

# result = simulation_test(
#     list(customers),
#     customer_limit=5,
#     wait_limit=900,
#     VEHICLE_NUM_PER_ZONE=1,
#     printB=False,
# )
# if result:
#     print(result)

# result = simulation_test(
#     list(customers),
#     customer_limit=5,
#     wait_limit=900,
#     VEHICLE_NUM_PER_ZONE=4,
#     printB=False,
# )
# if result:
#     print(result)


def run_simulations(count: int, wait_limit: int = 600, vehicle_num_per_zone=10):
    shared_rejected_customer = []
    no_shared_rejected_customer = []
    shared_meters = []
    no_shared_meters = []
    customer_count = []
    time_shared = []
    time_no_shared = []
    print(f"Starting Simulations ......")
    for i in range(count):
        customers = generate_customer_list(total_time=10800, size=1500)
        customer_count.append(len(customers))
        time_start = time.time()
        result_share = simulation_test(
            customers,
            customer_limit=6,
            wait_limit=wait_limit,
            VEHICLE_NUM_PER_ZONE=vehicle_num_per_zone,
            printB=False,
        )
        time_1 = time.time() - time_start
        time_start = time.time()
        result_no_share = simulation_test(
            customers,
            customer_limit=1,
            wait_limit=wait_limit,
            VEHICLE_NUM_PER_ZONE=vehicle_num_per_zone,
            printB=False,
        )
        time_2 = time.time() - time_start
        shared_rejected_customer.append(result_share["rejected_customer_cnt"])
        no_shared_rejected_customer.append(result_no_share["rejected_customer_cnt"])
        shared_meters.append(result_share["meters"])
        no_shared_meters.append(result_no_share["meters"])
        time_shared.append(time_1)
        time_no_shared.append(time_2)
        if i % 20 == 0:
            print(f"Done with {i + 1} simulations ...")
    return (
        shared_rejected_customer,
        no_shared_rejected_customer,
        shared_meters,
        no_shared_meters,
        customer_count,
        time_shared,
        time_no_shared
    )

def run_and_process_simulations():
    count = 500
    taxi_trips = {}
    taxi_trips[5] = run_simulations(count, wait_limit=600, vehicle_num_per_zone=5)
    taxi_trips[10] = run_simulations(count, wait_limit=600, vehicle_num_per_zone=10)

    print("-----------------------------------------")
    print(f"Total Number of simulations per scenario: {count}")
    print("-----------------------------------------")
    for tt in taxi_trips:
        trip = taxi_trips[tt]
        mean_shared_rejected = mean(trip[0])
        mean_no_shared_rejected = mean(trip[1])
        mean_shared_meters = mean(trip[2])
        mean_no_shared_meters = mean(trip[3])
        mean_customers = mean(trip[4])
        time_shared = mean(trip[5])
        time_no_shared = mean(trip[6])
        print("-----------------------------------------")
        print(f"Taxis: {tt}")
        print(f"Shared rejected customers: {mean_shared_rejected}")
        print(f"No shared rejected customers: {mean_no_shared_rejected}")
        print(f"Shared meters: {mean_shared_meters}")
        print(f"No shared meters: {mean_no_shared_meters}")
        print(f"Customer count: {mean_customers}")
        print(f"Average Meters per customer Shared: {mean_shared_meters / (mean_customers - mean_shared_rejected)}")
        print(f"Average Meters per customer No Shared: {mean_no_shared_meters / (mean_customers - mean_no_shared_rejected)}")
        print(f"Mean compute time shared: {time_shared}")
        print(f"Mean compute time no shared: {time_no_shared}")
        print("------------------------------------------")

    simulated_trip = "data/simulated_trips.json"
    with open(simulated_trip, 'w') as out_json:
        json.dump(taxi_trips, out_json)

total_start = time.time()
run_and_process_simulations()

total_end = time.time() - total_start
print(f"Total program time: {total_end}")
