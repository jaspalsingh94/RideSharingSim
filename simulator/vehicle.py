import uuid
from collections import deque
from collections import defaultdict

class Vehicle():
  WAIT = 1
  TO_CUSTOMER = 2
  TO_DESTINATION = 3
  END = 4
  def __init__(self, name, node, dest):
    self.name = name
    self.id = uuid.uuid4() # generate random ID
    self.node = node	# current node
    self.dest = dest 	# SET() 
    self.status = self.WAIT # WAIT, TO_CUSTOMER, TO_DESTINATION
    self.path = deque()     # From current to last destination
    self.dest_customer = defaultdict(list) # dest_customer[node_id] =  [ customer_id s ]
    self.customer_ids = set()
    self.cost = 0

    self.total_miles  = 0#add up as you go


  def start_move_to_customer(self):
    self.status = self.TO_CUSTOMER
    print("vehicle {} is coming from: {}, taking route: {}".format(self.name, self.node, self.path))
    #print("it will take {} minutes for the car to arrive".format(self.w_remaining)) ##################################################
  
  def start_move_to_dest(self,cost):
    self.status = self.TO_DESTINATION
    print("{} vehicle has arrived customer_location {} and It will take {} minutes from your location ({}) to your destination ({}) taking the route: {}".format(self.name, self.node, cost, self.node, self.dest, self.path))

  def end(self):
    self.status = self.END
    print("{} vehicle has arrived destiation {}".format(self.name, self.dest))
    
  def __repr__(self):
    return "name:" + self.name + " at "+ str(self.node) + ", path:" + str(self.path) + " destination:" + str(self.dest) + " customers:" + str(self.customer_ids)
  def __str__(self):
    return "name:" + self.name + " at "+ str(self.node) + ", path:" + str(self.path) + " destination:" + str(self.dest) + " customers:" + str(self.customer_ids)
      