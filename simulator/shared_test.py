from vehicle import Vehicle
from graph import Graph

import random, collections, time

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

def print_map(dic):
  i = 0
  st = []
  for key in dic.keys():
    st.append(key+":"+str(dic[key]))
    if key.split('-')[0] != i:
      print("".join(st))
      i += 1
      st = []

### check result
def check_result(dic, path, original_destinations, new_customer_location, new_customer_destanation, wait_limit):
  print("---------- check result start")
  path_set = set(path)
  for dest in  original_destinations:
    if dest not in path_set:
      print("original destination " + dest + " does not exist")
  if new_customer_location not in path_set:
    print("new_customer_location " + new_customer_location + " does not exist")
  if new_customer_destanation not in path_set:
    print("new_customer_destanation " + new_customer_destanation + " does not exist")
  
  index_new_customer_location = -1
  index_new_customer_destination = -1
  cost = 0
  for i in range(len(path)):
    node = path[i]
    if i > 0:
      previous_node = path[i-1]
      for n, c in dic[previous_node]:
        if n == node:
          cost += c
    if new_customer_location == node and index_new_customer_location == -1: # visit new_customer_locatin at first
      index_new_customer_location = i
      if cost > wait_limit: # the cost excced limit
        print("the cost excced limit")
    if new_customer_destanation == node:
      index_new_customer_destination = i
  # end for
  if index_new_customer_location > index_new_customer_destination:
    print("vehicle does not visit new_customer_destination after new_customer_location")
  print("calculated cost:"+ str(cost))
  print("---------- check result end")


#
def prepareTEST(M, MAX_COST):
  map = make_map(M, MAX_COST)
  ##print_map(dic)
  graph = Graph(map)
  graph.setPrint(False)        # print off in graph functions

  ################ CREATE vehicle_list
  vehicle_list = []
  for i in range(M):
    vehicle_name = 'v' + str(i)
    vehicle_current_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
    vehicle_original_destination = set()
    for i in range(3):
      random_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
      vehicle_original_destination.add(random_location)  # random original destination
    
    vehicle = Vehicle(vehicle_name, vehicle_current_location, vehicle_original_destination)
    vehicle_list.append(vehicle)
  
  ################ vehicle settings
  # 1. First, calculate cost with orignial destinations for each vehicle (just for settings before the main test)
  vehicle_location_dic = collections.defaultdict(set)
  for v in vehicle_list:
    vehicle_location_dic[v.node].add(v)            # for findVehiclesWithinDelta_BFS
    # calculate cost with orignial destinations
    _, v.cost = graph.EAMDSP(v.node, v.dest, v.node, None, float('inf')) # just put start node for new_customer argument
  return map, graph, vehicle_location_dic





def runTEST(M, map, graph, vehicle_location_dic, print_b):
  ################ new_customer
  new_customer_location = '0-0'     # random customer location
  new_customer_destanation = str(M-1) + '-' + str(M-1)
  #new_customer_location = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))     # random customer location
  #new_customer_destanation = str(random.randint(0,M-1)) + '-' + str(random.randint(0,M-1))
  new_customer_wait_limit = 50 # min or sec

  ################ TEST START
  # 2. Select available vehicles from all vehicles by findVehiclesWithinDelta_BFS function (so it returns vehicle_list not just one vehicle)
  selected_vehicle_list = graph.findVehiclesWithinDelta_BFS(vehicle_location_dic, new_customer_location, new_customer_wait_limit) # result = [ (cost, vehicle) ]
  selected_vehicle_list = [vehicle for _, vehicle in selected_vehicle_list] # result = [vehicle]
  if print_b:
    print('selected_vehicle by reversedBFS:', selected_vehicle_list)
    print("number of selected_vehicle by reversedBFS:",len(selected_vehicle_list))

  if selected_vehicle_list:
    # 3. Select the best vehicle from selected available vehicles by EAMDSP 
    result_vehicle, cost = graph.shared_test(selected_vehicle_list, new_customer_location, new_customer_destanation, new_customer_wait_limit)
    if print_b:
      print("result vehicle:",result_vehicle)
      print("result path:",result_vehicle.path)
      print("result cost:",cost)

    # 4. Validate result
    check_result(map, result_vehicle.path, result_vehicle.dest, new_customer_location, new_customer_destanation, new_customer_wait_limit)

# Input to create map
M = 50           # nodes: M*M
MAX_COST = 5
# Input to create map END


sum = 0
for i in range(1):
  map, graph, vehicle_location_dic = prepareTEST(M, MAX_COST)  
  start = time.time() # TIME START
  runTEST(M, map, graph, vehicle_location_dic, False) # print_b: print on off
  end = time.time()   # TIME END
  print((end-start))
  sum += (end-start)
print(sum/10)