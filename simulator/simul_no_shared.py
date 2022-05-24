from vehicle import Vehicle
from graph import Graph

import random
import collections
import heapq
import math
from collections import deque

from object_model import DISTANCES
from generate_random import TRAVEL_TIMES, TravelTime
from generate_customers import generate_customer_list
from db import connect

def make_map(): # each cost is random: 1 ~ max_cost
    graph = collections.defaultdict(list)
    # dic [start_node] list of (destination_node, cost)
    # node name: "(row_number)-(column_number)"   example: "2-4"
    # use print_dic function  
    adjacency_dic = collections.defaultdict(dict)
    conn = connect()
    with conn.cursor() as curs:
        curs.execute("SELECT zone_1, zone_2 FROM adjacency_zones;")
        while True:
            result = curs.fetchone()
            if not result:
                break
            zone_1 = result[0]
            zone_2 = result[1]
            adjacency_dic[zone_1][zone_2] = 1

    for node in TRAVEL_TIMES:
        for node2 in TRAVEL_TIMES[node]:
            #print(node, node2, adjacency_dic[node])
            if int(node2) in adjacency_dic[int(node)]: # adjacency
                #print('ad')
                weight = TRAVEL_TIMES[node][node2]['mean']
                graph[node].append((node2,weight))
        
    return graph


customers = generate_customer_list(size=50)
map_ = make_map()
rejected_customer_cnt = 0
rejected_event_cnt = 0
dropoff_cnt = 0
print(f"Number of customer {len(customers)}")
print(customers)
print(map_)

dic_customer = {}
for cu in customers:
    dic_customer[cu.name] = cu

#(Time that this event will occur, (type of class), object_name, <id>, ‘event_type’)
MIN_HEAP = [ (cu.arrival, 'c', cu.name) for cu in customers]
heapq.heapify(MIN_HEAP)
#print(MIN_HEAP)

############### WAIT LIMIT
wait_limit = 3000
############# vehicle_dic[v.name] = vehicle object
VEHICLE_NUM_PER_ZONE = 1
vehicle_dic = {}
vehicle_location_dic = collections.defaultdict(set)
index = 0
for node_id in map_:
    for _ in range(VEHICLE_NUM_PER_ZONE):
        vehicle = Vehicle('v'+str(index), node_id, set())
        index += 1
        vehicle_dic[vehicle.name] = vehicle
        vehicle_location_dic[node_id].add(vehicle)

print('len(vehicle_location_dic)',len(vehicle_location_dic))
graph = Graph(map_)

tt = TravelTime()

while MIN_HEAP:
    obj = heapq.heappop(MIN_HEAP)
    curr_time = obj[0]
    print('curr_time', curr_time, obj)
    class_type = obj[1]
    obj_name = obj[2]
    #print(obj)
    if class_type == 'c': # generate customer request
        customer = dic_customer[obj_name]
        #customer.pickup
        #customer.dropoff

        results = graph.findVehiclesWithinDelta_BFS(vehicle_location_dic, customer.pickup, wait_limit)
        
        if not results:
            rejected_customer_cnt += 1
            #print('customer_rejected')
            continue
        
        best_vehicle_cost = math.inf
        best_vehicle = None # vehicle name
        for cost, v in results: 
            if cost < best_vehicle_cost:        # pick the best vehicle
                best_vehicle = v
                best_vehicle_cost = cost
        
        vehicle = vehicle_dic[best_vehicle.name] # get original object
        
        vehicle.dest.add(customer.dropoff)
        vehicle.dest_customer[customer.dropoff].append(customer.name)
        vehicle.customer_ids.add(customer.name)

        
        if vehicle.node == customer.pickup: # same zone
            #!!!!!!!!!!!!! need to get distance for same zone
            #vehicle.total_miles += DISTANCES[prev][vehicle.node]
            time_add = tt.next_time(vehicle.node, customer.pickup) // 2 # travel to same zone (for pickup)

            if customer.pickup == customer.dropoff:
                if not vehicle.path:
                    vehicle.path.append(vehicle.node)
            else: # diff zone (customer.pickup and customer.dropoff)
                final_cost, reconst_path, _, _ = graph.a_star_algorithm(customer.pickup, customer.dropoff)
                vehicle.path = deque(reconst_path)
                time_add += tt.next_time(vehicle.path[0], vehicle.path[1])
            
                heapq.heappush(MIN_HEAP, (curr_time + (time_add//2), 'v', vehicle.name, vehicle.id, 1))
            heapq.heappush(MIN_HEAP, (curr_time + time_add, 'v', vehicle.name, vehicle.id, 2))

        else: # different zone
            final_cost, reconst_path_1, _, _ = graph.a_star_algorithm(vehicle.node, customer.pickup)
            
            if customer.pickup == customer.dropoff:
                vehicle.path = deque(reconst_path_1)
            else: # same zone (customer.pickup and customer.dropoff)
                final_cost, reconst_path_2, _, _ = graph.a_star_algorithm(customer.pickup, customer.dropoff)
                reconst_path_1.pop()
                vehicle.path = deque(reconst_path_1 + reconst_path_2)

            # test -- check continuous two nodes
            if len(vehicle.path) >= 1:
                prev_node = vehicle.path[0]
                #print(vehicle.path)
                for node in list(vehicle.path)[1:]:
                    if prev_node == node:
                        print('!! continuous two nodes', prev_node, node)
                        raise Exception()
                    prev_node = node
            # -- check continuous two nodes
            
            time_add = tt.next_time(vehicle.path[0], vehicle.path[1]) # vehicle -> customer_pickup

            heapq.heappush(MIN_HEAP, (curr_time + (time_add//2), 'v', vehicle.name, vehicle.id, 1))
            heapq.heappush(MIN_HEAP, (curr_time + time_add, 'v', vehicle.name, vehicle.id, 2))
        
        print('pickup reserved vehicle:',vehicle)
        print('pickup reserved customer:', customer)

    elif class_type == 'v':
        #print(obj)
        vehicle_id = obj[3]
        vehicle = vehicle_dic[obj_name]
        if vehicle_id != vehicle.id: # vehicle was updated. -> reject the event
            print('vehicle_id != vehicle.id:')
            rejected_event_cnt += 1
            continue

        elif obj[4] == 1: # vehicle arrive borderline. update current zone of vehicle
            #print(obj)
            prev = vehicle.path.popleft()
            vehicle.node = vehicle.path[0]
            # + mile
            vehicle.total_miles += DISTANCES[prev][vehicle.node ]
            vehicle_location_dic[prev].remove(vehicle)
            vehicle_location_dic[vehicle.node].add(vehicle)

        elif obj[4] == 2: # if destination -> (if curr_node == dest ) -> dropoff
            if vehicle.node in vehicle.dest:
                for customer_id in vehicle.dest_customer[vehicle.node]:
                    dropoff_cnt += 1 
                    print('############################# customer:',customer_id,' dropoff from', vehicle)
                    vehicle.customer_ids.remove(customer_id)
                
                vehicle.dest.remove(vehicle.node)
                vehicle.dest_customer[vehicle.node] = []
            
            if len(vehicle.dest) >= 1: # more dest remained
                time_add = tt.next_time(vehicle.path[0], vehicle.path[1])
            
                heapq.heappush(MIN_HEAP, (curr_time + (time_add//2), 'v', vehicle.name, vehicle.id, 1))
                heapq.heappush(MIN_HEAP, (curr_time + time_add, 'v', vehicle.name, vehicle.id, 2))
            else: # path end => travel end
                if len(vehicle.customer_ids) > 0:
                    print('!! travel end, but len(vehicle.customer_ids) > 0:', vehicle)
                    raise Exception()
                vehicle.path = deque()

        
print('dropoff_cnt', dropoff_cnt)
print('rejected_customer_cnt', rejected_customer_cnt)
print('rejected_event_cnt', rejected_event_cnt)
print('customers', len(customers))
            
            