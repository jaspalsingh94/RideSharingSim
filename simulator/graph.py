import collections
import time

from vehicle import Vehicle

class Graph():
    def __init__(self, adjacency_list): # dictionary
        self.adjacency_list = adjacency_list
        self.print = True
        self.reverse_adjacency_list = collections.defaultdict(list) # vehicle BFS search
        for key in self.adjacency_list:
          for end_point, weight in self.adjacency_list[key]:
            self.reverse_adjacency_list[end_point].append((key, weight))

    def setPrint(self, print):
        self.print = print
    
    # --- A* Algorithm START ---
    def get_neighbors(self, v):
        return self.adjacency_list[v]
    def get_reverse_neighbors(self, v):
        return self.reverse_adjacency_list[v]

    # heuristic function with equal values for all nodes
    def h(self, n):
        '''
        H = {}
        for key in self.adjacency_list:
            H[key] = 1
        '''
        return 1

    def a_star_algorithm(self, start_node, stop_node, minimum_cost = float('inf'), new_customer = None, new_dest = None, new_customer_wait_limit = float('inf')):
        # open_list is a list of nodes which have been visited, but who's neighbors
        # haven't all been inspected, starts off with the start node
        # closed_list is a list of nodes which have been visited
        # and who's neighbors have been inspected
        open_list = set([start_node])
        closed_list = set([])

        # g contains current distances from start_node to all other nodes
        # the default value (if it's not found in the map) is +infinity
        g = {}

        g[start_node] = 0

        # parents contains an adjacency map of all nodes
        parents = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None

            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n == None or g[v] + self.h(v) < g[n] + self.h(n):
                    n = v;

            if n == None and self.print:
                print('request dropped: path does not exist')
                return None

            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            if n == stop_node:
                reconst_path = []
                reconst_set = set() # for multiple destination
                reconst_dic = {}
                final_cost = g[n]
                cost_start_new_customer = float('inf') # cost from start to new_customer
                while parents[n] != n:
                    if new_customer == n:             # if the node == new_customer_location
                      cost_start_new_customer = g[n]  # cost from start to new_customer
                      reconst_dic[n] = g[n]
                    if new_dest == n and n not in reconst_dic: # if the node == new_dest AND did not visit new_dest before # to consider NEW_DESTINATION -> NEW_CUSTOMER -> "NEW_DESTINATION"
                      reconst_dic[n] = g[n]
                    reconst_set.add(n)
                    reconst_path.append(n)
                    n = parents[n]
                if (new_customer is not None) and (cost_start_new_customer > new_customer_wait_limit): # new_customer requirement AND cost exceeds wait_limit
                  return None # drop

                reconst_path.append(start_node)

                reconst_path.reverse()

                # if self.print:
                #     print('Path found: {}'.format(reconst_path))
                #     print('Cost:', final_cost)
                return final_cost, reconst_path, reconst_set, reconst_dic
                

            # for all neighbors of the current node do
            for (m, weight) in self.get_neighbors(n):
                # only if cost is less than minimum_cost(already calculated for the previous car or wait_limit)
                if g[n] + weight <= minimum_cost:
                  # if the current node isn't in both open_list and closed_list
                  # add it to open_list and note n as it's parent
                  if m not in open_list and m not in closed_list:
                      open_list.add(m)
                      parents[m] = n
                      g[m] = g[n] + weight

                  # otherwise, check if it's quicker to first visit n, then m
                  # and if it is, update parent data and g data
                  # and if the node was in the closed_list, move it to open_list
                  else:
                      if g[m] > g[n] + weight:
                          g[m] = g[n] + weight
                          parents[m] = n

                          if m in closed_list:
                              closed_list.remove(m)
                              open_list.add(m)

            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)
        if self.print:
            print('Path does not exist!')
        return None

        # A* algorithm END ---
      ########################################################
    '''
    def findVehicleBFS(self, vehicle_list, customer_location, wait_limit= float('inf')):
        deq = collections.deque([([customer_location], 0)]) # (path, cost) 
        minimum_cost = wait_limit #float('inf') # set infinity
        # default = None = Cannot allocate vehicle
        vehicle_path = None

        #visited = set()   #?? do we need to check visited node?
        while deq:
          path, cost = deq.popleft()
          node = path[-1]
          #visited.add(node)
          counter = 0
          for vehicle in vehicle_list:
            if node == vehicle.node and vehicle.path == [] and cost < minimum_cost: # node has a car AND the cost of this car < minimum ==> UPDATE
              vehicle_list[counter].path = []
              vehicle_list[counter].w_remaining = 0
              vehicle_list[counter].c = 0
              counter = vehicle_list.index(vehicle)
              vehicle.path = path[0:-1]
              vehicle.w_remaining = self.getReversedWeight(vehicle)
              minimum_cost = cost
              vehicle_path = path
              

          for new_node, weight in self.get_reverse_neighbors(node):
            new_cost = cost + weight
            if new_cost < minimum_cost:
              new_path = list(path) # new list
              new_path.append(new_node)
              deq.append((new_path, new_cost))

        for vehicle in vehicle_list:
          vehicle.path = vehicle.path[::-1]
        return vehicle_list[counter], minimum_cost

    def findVehicleAstar(self, vehicle_list, customer_location, wait_limit= float('inf')):
      minimum_cost = wait_limit #float('inf') set infinity
      vehicle_path = None # default = None = Cannot allocate vehicle
      for vehicle in vehicle_list: # vehicle -> customer_location
        vehicle = vehicle.node
        result = self.a_star_algorithm(vehicle, customer_location, minimum_cost)
        if result is not None:
          cost = result[0]
          path = result[1]
          if cost < minimum_cost:
            minimum_cost = cost
            vehicle_path = path
      return vehicle_path, minimum_cost
    '''
    def getWeight(self, vehicle):
      if vehicle.path != []:
        node = vehicle.node
        next_node = vehicle.path[0]
        for new_node, weight in self.get_neighbors(node):
          if new_node == next_node:
            return weight
      else:
        return 0

    def getReversedWeight(self, vehicle):
      if vehicle.path != []:
        node = vehicle.node
        next_node = vehicle.path[-1]
        for new_node, weight in self.get_reverse_neighbors(next_node):
          if new_node == node:
            return weight
      else:
        return 0

    def EAMDSP(self, start, T, new_customer, new_dest, new_customer_wait_limit): # T = set(): original muptiple destination
      L3 = [start]
      total_cost = 0
      if new_customer == start: # if car is already at new_customer location
        if new_dest is not None:
          T.add(new_dest)
        new_customer = None
      else:
        T.add(new_customer)     # else add new customer location
      if start in T:            # if start is in original destinations, remove start
        T.remove(start)
      
      while T:
        shortest_path = []
        shortest_cost = float('inf')
        shortest_set = set()
        shortest_dic = {}
        #L2 = []
        if new_customer is None:      # car already took new_customer -> no need to consider new_customer requirement
          new_customer_wait_limit = float('inf')
        for dest in T:
          result = self.a_star_algorithm(start, dest, shortest_cost, new_customer, new_dest, new_customer_wait_limit)
          
          if result is not None:      # if path is available (= if path is not dropped)
            final_cost, nodes_path, nodes_set, nodes_dic = result
            if final_cost < shortest_cost:
              shortest_path = nodes_path
              shortest_cost = final_cost
              shortest_set = nodes_set
              shortest_dic = nodes_dic

        if self.print:
          print(shortest_path, shortest_cost, shortest_set, shortest_dic )
        
        if shortest_path: # path is available
          L3.extend(shortest_path[1:])     # L3 + [a b c d e...]
          total_cost += shortest_cost
          for node in (shortest_set.intersection(T)): # remove all destination included in shortest_path
            T.remove(node)
          
          if new_customer in shortest_dic:    # if vehicle visit new_customer's location
            if new_dest not in shortest_dic or shortest_dic[new_dest] < shortest_dic[new_customer]: # new_dest NOT IN path OR (new_dest in path AND the vehicle visit new_destination before new_customer)
              T.add(new_dest)                 # add new customer's destination to T destinations.
            new_customer = None
          start = shortest_path[-1] # update start node with destination of shortest path
        else: # path is not available
          print("request dropped: path does not exist, which can visit new_customer_location within new_customer_wait_limit(delta)")
          return L3, total_cost
      return L3, total_cost

    def findVehiclesWithinDelta_BFS(self, vehicle_location_dic, customer_location, wait_limit= float('inf')):
      deq = collections.deque([(customer_location, 0)]) # (node, cost) 
      # for return
      selected_vehicles = []
      
      visited_map = collections.defaultdict(lambda: float('inf')) # map[node] = minimum_cost
      visited_map[customer_location] = 0 # start node

      while deq:
        node, cost = deq.popleft()
        #print(node,cost)
        if node in vehicle_location_dic and cost < wait_limit:
          for v in vehicle_location_dic[node]: # vehicle_location_dic[node] = set([vehicles])
            # add contraint like number of customers in this vehicle !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if len(v.customer_ids) < 6:
              selected_vehicles.append((cost,v))
          del vehicle_location_dic[node] # to remove duplicate case
        
        # add neighbor nodes to deque
        for new_node, weight in self.get_reverse_neighbors(node):
          new_cost = cost + weight
          if new_cost < wait_limit and new_cost < visited_map[new_node]: # new_cost less than wait_limit AND less than old cost that visited it before
            visited_map[new_node] = new_cost
            deq.append((new_node, new_cost))
      return selected_vehicles

    def shared_test(self, vehicle_list, new_customer_location, new_customer_destanation, new_customer_wait_limit):
      cost = float('inf')
      least_cost_difference = float('inf')
      selected_vehicle = None
      # Input for EAMDSP
      for v in vehicle_list:
        result = self.EAMDSP(v.node, v.dest, new_customer_location, new_customer_destanation, new_customer_wait_limit)
        if not result[0]:
          print(v.name + "request has been dropped due to new_customer_wait_limit(delta)")
        else:
          new_cost = result[1]
          cost_difference = new_cost - v.cost # new_cost - old_cost
          if self.print:
            print("v.name", v.name,"new_cost vs old_cost", new_cost, v.cost, "cost_difference", cost_difference)
          if cost_difference < least_cost_difference:
            selected_vehicle = v
            v.path = result[0]
            cost = new_cost
            least_cost_difference = cost_difference
      return selected_vehicle, cost