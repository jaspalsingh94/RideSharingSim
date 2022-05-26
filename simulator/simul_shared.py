from vehicle import Vehicle
from graph import Graph

import pickle
import collections
import heapq
import uuid
import math
from collections import deque
from db import connect

from object_model import DISTANCES, ZONES
from generate_random import TRAVEL_TIMES, TravelTime


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
    with open('data/map_graph.pickle', 'wb') as handle:
        pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # return graph


def get_map():
    with open('data/map_graph.pickle', 'rb') as handle:
        graph = pickle.load(handle)
    return graph


def simulation_test(customers, customer_limit=1, wait_limit=900, VEHICLE_NUM_PER_ZONE=1, printB=False):
    #customers = generate_customer_list(size=50)
    # make_map()
    map_ = get_map()
    rejected_customer_cnt = 0
    rejected_event_cnt = 0
    dropoff_cnt = 0
    if printB: print(f"Number of customer {len(customers)}")
    if printB: print(customers)
    if printB: print(map_)

    dic_customer = {}
    for cu in customers:
        dic_customer[cu.name] = cu

    #(Time that this event will occur, (type of class), object_name, <id>, ‘event_type’)
    MIN_HEAP = [ (cu.arrival, 'c', cu.name) for cu in customers]
    heapq.heapify(MIN_HEAP)
    #if printB: print(MIN_HEAP)

    #customer_limit = 4
    ############### WAIT LIMIT
    #wait_limit = 900
    ############# vehicle_dic[v.name] = vehicle object
    #VEHICLE_NUM_PER_ZONE = 4
    vehicle_dic = {}
    vehicle_location_dic = collections.defaultdict(set)
    index = 0
    for node_id in map_:
        for _ in range(VEHICLE_NUM_PER_ZONE):
            vehicle = Vehicle('v'+str(index), node_id, set())
            vehicle_dic[vehicle.name] = vehicle
            vehicle_location_dic[node_id].add(vehicle)
            index += 1

    if printB: print('len(vehicle_location_dic)',len(vehicle_location_dic))
    graph = Graph(map_)
    graph.setPrint(printB)
    tt = TravelTime()

    while MIN_HEAP:
        obj = heapq.heappop(MIN_HEAP)
        curr_time = obj[0]
        if printB: print('curr_time', curr_time, obj)
        class_type = obj[1]
        obj_name = obj[2]
        #if printB: print(obj)
        if class_type == 'c': # generate customer request
            customer = dic_customer[obj_name]
            if printB: print(customer)
            selected_vehicle_list = graph.findVehiclesWithinDelta_BFS(vehicle_location_dic, customer.pickup, wait_limit,customer_limit)
            
            if not selected_vehicle_list:
                rejected_customer_cnt += 1
                # customer.arrival += 180.0
                # heapq.heappush(MIN_HEAP, (customer.arrival, 'c', customer.name)) # re-request after 500s
                #if printB: print('customer_rejected')
                continue
            
            best_vehicle_cost = math.inf
            least_cost_difference = math.inf
            best_vehicle = None
            
            # find best vehicle
            for cost, v in selected_vehicle_list: # cost = vehicle.node -> customer.pickup
                if v.dest:  # if vehicle already has  destinations (=has customer)
                    result = graph.EAMDSP(v.node, v.dest, customer.pickup, customer.dropoff, wait_limit) #new_customer_wait_limit
                    if not result[0]:
                        if printB: print(v.name + ": this vehicle has been dropped due to new_customer_wait_limit(delta)")
                        continue
                    else:
                        new_cost = result[1]
                        new_path = result[0] # !! entire path: vehicle.node -> customer.pickup -> customer.dropoff
                        cost_difference = new_cost - v.cost # new_cost - old_cost
                
                else:       # if vehicle does NOT have destination (=doesn't have customer =doesn't have current cost)
                    if v.cost != 0 or v.customer_ids:
                        print(v)
                        raise Exception('vehicle does NOT have destination  but v.cost == 0 or v.customer_ids')
                    pickup_dropoff_cost, reconst_path, _, _ = graph.a_star_algorithm(customer.pickup, customer.dropoff)
                    
                    new_cost = cost + pickup_dropoff_cost # (total cost = vehicle.node -> customer.pickup -> customer.dropoff)
                    new_path = reconst_path # !! only path for customer.pickup -> customer.dropoff
                    cost_difference = new_cost - v.cost # (total cost) - 0(v.cost=0)

                if graph.print:
                    if printB: print("v.name", v.name,"new_cost vs old_cost", new_cost, v.cost, "cost_difference", cost_difference)
                if cost_difference < least_cost_difference: # choose best vehicle
                    best_vehicle = v
                    best_vehicle_path = new_path
                    best_vehicle_cost = new_cost
                    least_cost_difference = cost_difference
            
            vehicle = vehicle_dic[best_vehicle.name] # get original object
            vehicle.cost = best_vehicle_cost
            vehicle.path = deque(best_vehicle_path)
            vehicle.path.popleft()
            
            if len(vehicle.customer_ids) == 0:   # if best_vehicle WITHOUT customer is selected
                # path should be added, because current vehicle.path :  customer.pickup -> customer.dropoff
                if printB: print('len(vehicle.dest) == 0:: empty vehicle:', vehicle)
                if vehicle.node != customer.pickup: # different zone
                    final_cost, reconst_path, _, _ = graph.a_star_algorithm(vehicle.node, customer.pickup) # vehicle.node -> customer.pickup
                    if printB: print(reconst_path)
                    #if customer.pickup == customer.dropoff:
                    #    reconst_path.pop()
                    vehicle.path = deque(reconst_path[1:] + list(vehicle.path)) # vehicle.node -> customer.pickup -> customer.dropoff
                    if printB: print(vehicle.path)
            else:
                if printB: print('len(vehicle.dest) > 0:: vehicle.id updated:', vehicle)
                vehicle.id = uuid.uuid4()       # vehicle's path has been changed. generate new id (to reject old events)

            vehicle.dest.add(customer.dropoff)
            vehicle.dest_customer[customer.dropoff].add(customer.name)
            vehicle.pick_customer[customer.pickup].add(customer.name)
            vehicle.customer_ids.add(customer.name)
            
            add_meters = 0
            if vehicle.pick_customer[vehicle.node] or vehicle.dest_customer[vehicle.node]: # need to visit same zone
                if printB: print('need to visit same zone', vehicle)
                add_meters += ZONES[vehicle.node]['avg_dist'] # get distance for same zone
                same_zone_travel_time = tt.next_time(vehicle.node, customer.pickup) // 2 # travel to same zone (for pickup)
                if printB: print('heappush 2:', vehicle, curr_time + same_zone_travel_time)
                heapq.heappush(MIN_HEAP, (curr_time + same_zone_travel_time, 'v', vehicle.name, vehicle.id, 2, add_meters))
            else: # vehicle.node != customer.pickup: # To the next zone
                if printB: print('NO need to visit same zone', vehicle)
                next_zone_travel_time = tt.next_time(vehicle.node, vehicle.path[0]) 
                if printB: print('heappush 1:', vehicle, curr_time + (next_zone_travel_time//2))
                if printB: print('heappush 2:', vehicle, curr_time + next_zone_travel_time)
                heapq.heappush(MIN_HEAP, (curr_time + (next_zone_travel_time//2), 'v', vehicle.name, vehicle.id, 1)) # border line
                heapq.heappush(MIN_HEAP, (curr_time + next_zone_travel_time, 'v', vehicle.name, vehicle.id, 2, add_meters))

            # test -- check continuous two nodes
            if len(vehicle.path) >= 1:
                prev_node = vehicle.path[0]
                if printB: print(vehicle)
                for node in list(vehicle.path)[1:]:
                    if prev_node == node:
                        print('!!!!!!!!! continuous two nodes', prev_node, node)
                        raise Exception()
                    prev_node = node
            # -- check continuous two nodes

            if printB: print('pickup reserved vehicle:',vehicle)
            if printB: print('pickup reserved customer:', customer)


        elif class_type == 'v': # vehicle event
            #if printB: print(obj)
            vehicle = vehicle_dic[obj_name]
            vehicle_id = obj[3]
            if printB: print(vehicle)
            if vehicle_id != vehicle.id: # vehicle's path was updated. -> reject the event
                if printB: print('vehicle_id != vehicle.id: rejected_event_cnt',obj,vehicle)
                rejected_event_cnt += 1
                continue

            elif obj[4] == 1: # vehicle arrive borderline. update current zone of vehicle
                #if printB: print(obj)
                if printB: print('obj[4] == 1: vehicle arrives borderline: ',vehicle)
                prev = vehicle.node
                vehicle.node = vehicle.path.popleft()
                # + mile -> obj[4] == 2:
                vehicle.total_meters += DISTANCES[prev][vehicle.node ]
                vehicle_location_dic[prev].remove(vehicle)
                vehicle_location_dic[vehicle.node].add(vehicle)

            elif obj[4] == 2: # if destination -> (if curr_node == dest ) -> dropoff
                add_meters = obj[5]
                if printB: print('obj[4] == 2: vehicle arrives zone:',vehicle)
                if vehicle.pick_customer[vehicle.node]:
                    customer_id = vehicle.pick_customer[vehicle.node].pop() # just one customer
                
                elif vehicle.dest_customer[vehicle.node]:
                    customer_id = vehicle.dest_customer[vehicle.node].pop() # just one customer
                    dropoff_cnt += 1 
                    if printB: print('############################# customer:',customer_id,' dropoff from', vehicle)
                    vehicle.customer_ids.remove(customer_id)
                    vehicle.total_meters += add_meters

                    if not vehicle.dest_customer[vehicle.node]: # all customer with ths destiantion drop off -> remove destination 
                        if printB: print('not vehicle.dest_customer[vehicle.node]:')
                        vehicle.dest.remove(vehicle.node)
                        del vehicle.dest_customer[vehicle.node]
                
                
                
                if vehicle.pick_customer[vehicle.node] or vehicle.dest_customer[vehicle.node]: # need to visit same zone
                    if printB: print('same zone:',vehicle, vehicle.pick_customer[vehicle.node], vehicle.dest_customer[vehicle.node])
                    add_meters = ZONES[vehicle.node]['avg_dist'] # get distance for same zone
                    same_zone_travel_time = tt.next_time(vehicle.node, vehicle.node) // 2 # travel to same zone (for pickup)
                    if printB: print('heappush 2:', vehicle, curr_time + same_zone_travel_time)
                    heapq.heappush(MIN_HEAP, (curr_time + same_zone_travel_time, 'v', vehicle.name, vehicle.id, 2, add_meters))
                elif len(vehicle.dest) >= 1: # more dest remained : To the next zone
                    if printB: print('len(vehicle.dest) >= 1:', vehicle)
                    next_zone_travel_time = tt.next_time(vehicle.node, vehicle.path[0])
                    if printB: print('heappush 1:', vehicle, curr_time + (next_zone_travel_time//2))
                    if printB: print('heappush 2:', vehicle, curr_time + next_zone_travel_time)
                    heapq.heappush(MIN_HEAP, (curr_time + (next_zone_travel_time//2), 'v', vehicle.name, vehicle.id, 1))
                    heapq.heappush(MIN_HEAP, (curr_time + next_zone_travel_time, 'v', vehicle.name, vehicle.id, 2, 0))
                
                else: # path end => travel end
                    if len(vehicle.customer_ids) > 0:
                        print('!! travel end, but len(vehicle.customer_ids) > 0:', vehicle)
                        raise Exception()
                    vehicle.path = deque()
                    vehicle.cost = 0
                    vehicle.dest_customer = collections.defaultdict(set)
                    vehicle.pick_customer = collections.defaultdict(set)

            
    if printB: print('dropoff_cnt', dropoff_cnt)
    if printB: print('rejected_customer_cnt', rejected_customer_cnt)
    if printB: print('rejected_event_cnt', rejected_event_cnt)
    if printB: print('customers', len(customers))

    meters = 0      
    for v_name in vehicle_dic:
        v = vehicle_dic[v_name]
        meters += v.total_meters
    if printB: print('meters:',meters)

    return {'dropoff_cnt':dropoff_cnt,'rejected_customer_cnt': rejected_customer_cnt,'rejected_event_cnt':rejected_event_cnt,'meters':meters}