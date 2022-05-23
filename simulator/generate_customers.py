from object_model import Customer
from generate_random import gen_expon
import scipy.stats as st

# default to 4 hours: 14400
# using 1 hour now
def generate_customer_list(total_time = 3600, size = 500 ):
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
            break
    return customers
    '''
    print(f"Time so far: {time_so_far}")
    print(f"Lenght of Customers: {len(customers)}")
    for i in range(5):
        print(f"Customer name: {customers[i].name}")
        print(f"Customer arrival: {customers[i].arrival}")
        print(f"Customer pickup: {customers[i].pickup}")
        print(f"Customer dest: {customers[i].dest}\n")
    i = -1
    print(f"Customer name: {customers[i].name}")
    print(f"Customer arrival: {customers[i].arrival}")
    print(f"Customer pickup: {customers[i].pickup}")
    print(f"Customer dest: {customers[i].dest}\n")
    '''