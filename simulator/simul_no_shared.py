from vehicle import Vehicle
from graph import Graph

import random
import collections

from generate_random import TRAVEL_TIMES
from generate_customers import generate_customer_list
from db import connect

def make_map(): # each cost is random: 1 ~ max_cost
    graph = collections.defaultdict(list)
    # dic [start_node] list of (destination_node, cost)
    # node name: "(row_number)-(column_number)"   example: "2-4"
    # use print_dic function
    dir = [[0,1],[0,-1],[1,0],[-1,0]]
  
  
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


customers = generate_customer_list(size=5)
map_ = make_map()

print(len(customers))
print(customers)
print(map_)


MIN_HEAP = []

