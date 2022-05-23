from vehicle import Vehicle
from graph import Graph

import random
import collections

def make_map(M, max_cost): # each cost is random: 1 ~ max_cost
  dic = collections.defaultdict(list)
  # dic [start_node] list of (destination_node, cost)
  # node name: "(row_number)-(column_number)"   example: "2-4"
  # use print_dic function
  dir = [[0,1],[0,-1],[1,0],[-1,0]]
  
  for i in range(M):
    for j in range(M):
      for d in dir:
        x = i + d[0]
        y = j + d[1]
        if x >= 0 and x < M and y >= 0 and y < M:
          # dic[start] . append ( end_node  ,   cost  )
          cost = random.randint(1,max_cost)
          dic[str(i)+'-'+str(j)].append((str(x)+'-'+str(y), cost))
  return dic

M = 50       ####### M * M nodes, and M vehicles
MAX_COST = 5  ####### edge weight: 1~MAX_COST
map = make_map(M,MAX_COST)
graph = Graph(map)
graph.setPrint(False)        # print off

# random customer location
customer_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
customer_destination = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
wait_limit = 30 #

for i in range(1):
    customer_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))     # random customer location
    vehicle_location_dic = collections.defaultdict(set)
    for i in range(M):
        vehicle_name = 'v' + str(i)  # M vehicles at random location
        vehicle_current_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
        vehicle_original_destination = None
        
        vehicle = Vehicle(vehicle_name, vehicle_current_location, vehicle_original_destination)
        #vehicle_list.append(vehicle)
        vehicle_location_dic[vehicle_current_location].add(vehicle)
    print("Reversed BFS", len(vehicle_location_dic))
    
    results = graph.findVehiclesWithinDelta_BFS(vehicle_location_dic, customer_location, wait_limit)
    print(results)
    results.sort(key = lambda x : x[0])
    print(results[0][0])


