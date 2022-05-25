from simul_shared import simulation_test
from generate_customers import generate_customer_list

customers = generate_customer_list(size=100)

result = simulation_test(list(customers), customer_limit=1, wait_limit=900, VEHICLE_NUM_PER_ZONE=1, printB=False)
if result: print(result)

result = simulation_test(list(customers), customer_limit=1, wait_limit=900, VEHICLE_NUM_PER_ZONE=4, printB=False)
if result: print(result)

result = simulation_test(list(customers), customer_limit=5, wait_limit=900, VEHICLE_NUM_PER_ZONE=1, printB=False)
if result: print(result)

result = simulation_test(list(customers), customer_limit=5, wait_limit=900, VEHICLE_NUM_PER_ZONE=4, printB=False)
if result: print(result)