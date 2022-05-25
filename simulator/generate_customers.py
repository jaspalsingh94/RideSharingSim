from object_model import Customer
from generate_random import gen_expon, generate_pickup_zone, generate_dropoff_zone
import scipy.stats as st

# default to 4 hours: 14400
# using 1 hour now
def generate_customer_list(total_time=3600, size=500):
    """
    Generates a list of customers for total time.
    """
    expon_vars = gen_expon(size)
    time_so_far = 0.0
    customers = []
    for i, var in enumerate(expon_vars):
        time_so_far = time_so_far + var
        customers.append(Customer(i, time_so_far))
        if time_so_far > total_time:
            if len(customers) % 2 == 0:
                break
    print(f"Length of customers: {len(customers)}")
    mid_point = int(len(customers) / 2)

    # testing_rand = [generate_pickup_zone() for i in range(mid_point * 2)]
    # probs = [pickup[1] for pickup in testing_rand]
    # print(f"Initial variance: {st.variation(probs)}")
    # for i in range(mid_point):
    #     testing_rand[mid_point + 1] = generate_pickup_zone(1 - testing_rand[i][1])
    # probs = [pickup[1] for pickup in testing_rand]
    # print(f"Final variance: {st.variation(probs)}")

    pick_up_zones = [generate_pickup_zone() for i in range(mid_point)]
    drop_off_zones = [generate_dropoff_zone() for i in range(mid_point)]

    for i in range(mid_point):
        pick_up_zones.append(generate_pickup_zone(1 - pick_up_zones[i][1]))
        drop_off_zones.append(generate_dropoff_zone(1 - drop_off_zones[i][1]))

    probs = [pickup[1] for pickup in pick_up_zones]
    

    for i, _ in enumerate(customers):
        customers[i].pickup = pick_up_zones[i][0]
        customers[i].dropoff = drop_off_zones[i][0]

    print(f"Time so far: {time_so_far}")
    print(f"Lenght of Customers: {len(customers)}")
    return customers
    """
    print(f"Time so far: {time_so_far}")
    print(f"Lenght of Customers: {len(customers)}")
    for i in range(5):
        print(f"Customer name: {customers[i].name}")
        print(f"Customer arrival: {customers[i].arrival}")
        print(f"Customer pickup: {customers[i].pickup}")
        print(f"Customer dropoff: {customers[i].dropoff}\n")
    i = -1
    print(f"Customer name: {customers[i].name}")
    print(f"Customer arrival: {customers[i].arrival}")
    print(f"Customer pickup: {customers[i].pickup}")
    print(f"Customer dropoff: {customers[i].dropoff}\n")
    """
