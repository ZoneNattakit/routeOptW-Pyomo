# import need library
import pyomo.environ as pyomo
from pyomo.opt import SolverFactory
import random
import logging
import math
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(filename='pyomo_ipy.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Your code that might raise an exception
    logging.info('Successful')
except Exception as e:
    # Log the exception
    logging.error("An error occurred: %s", str(e))

# %%
# Generate random data
num_customers = 10 # ID 0-n (ID and Name) checked
num_vehicles = 5 #(Size of car like truck 3 sizes) ID 0-n and type 3 types

num_goods = 100
#time limit each customers(period each cus)

#obj = sent in time in day (everyday)

# %%
customers = range(1, num_customers + 1)
vehicles = range(num_vehicles)
goods = range(num_goods)

# %%
# Coordinates of depot and customers
depot = (4, 4)
customer_locations = {i: (random.uniform(0, num_customers), random.uniform(0, num_vehicles)) for i in customers}
goods_for_cus = {customer_locations: random.randint(0, num_goods) for i in customers}

# %%
# Customer names
customer_names = {i: f"ID_{i}" for i in customers}

# %%
# Calculate distances between locations
def distance(location1, location2):
    x_diff = location1[0] - location2[0]
    y_diff = location1[1] - location2[1]
    return math.sqrt(x_diff**2 + y_diff**2)

# Construct distances including vehicle index
distances = {(i, j, k): distance(customer_locations[i], customer_locations[j]) for i in customers for j in customers for k in vehicles if i != j}

# Create Pyomo model
model = pyomo.ConcreteModel()

# Decision Variables
model.x = pyomo.Var(customers, customers, vehicles, domain=pyomo.Binary)
model.goods = pyomo.Var(customers, vehicles, domain=pyomo.NonNegativeReals)  # New variable for goods carried

# Objective function: Minimize total distance traveled and total goods carried
model.obj = pyomo.Objective(
    expr=(
        sum(distances[i, j, k] * model.x[i, j, k] for i in customers for j in customers for k in vehicles if i != j) +
        sum(goods_for_cus[i] * model.goods[i, k] for i in customers for k in vehicles)
    ),
    sense=pyomo.minimize
)

# Ensure that each customer is visited exactly once
model.visits_constraint = pyomo.ConstraintList()
for i in customers:
    model.visits_constraint.add(expr=sum(model.x[i, j, k] for j in customers for k in vehicles) == 1)

# Ensure that each vehicle leaves and arrives at the depot
model.depot_constraint = pyomo.ConstraintList()
for k in vehicles:
    model.depot_constraint.add(expr=sum(model.x[i, j, k] for j in customers for k in vehicles) == 1)

# Ensure that each vehicle's goods capacity is not exceeded
vehicle_capacity = 100  # Example capacity, adjust as needed
model.capacity_constraint = pyomo.ConstraintList()
for k in vehicles:
    model.capacity_constraint.add(
        expr=sum(goods_for_cus[i] * model.goods[i, k] for i in customers) <= vehicle_capacity
    )

# %%
# Solve the VRP problem
solver = SolverFactory('cbc')
results = solver.solve(model, tee=True)

# %%
# Plot routes
def plot_routes(routes, depot, customer_locations):
    plt.figure(figsize=(10, 10))

    # Plot depot
    plt.scatter(*depot, color='black', marker='D', s=100, label='Depot')

    # Plot customer nodes
    for customer, (x, y) in customer_locations.items():
        plt.scatter(x, y, color='blue')
        plt.text(x, y, f"{customer_names[customer]}", fontsize=8, ha='right')
    
    # Define colors for different vehicles
    colors = ['red', 'orange', 'purple', 'cyan', 'magenta', 'black', 'green']

    # Plot routes
    for k, route in enumerate(routes):
        color = colors[k % len(colors)]  # Cycle through colors for each vehicle

        # Start the route from the depot
        x_values = [depot[0]] + [customer_locations[i][0] for i, j in route] + [depot[0]]
        y_values = [depot[1]] + [customer_locations[i][1] for i, j in route] + [depot[1]]

        plt.plot(x_values, y_values, color=color, marker='o')
        plt.plot([], [], color=color, label=f'Vehicle {k + 1} route')
    # Add legend outside the plot
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper right')
        

    plt.title('Vehicle Routes')
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.legend()
    plt.show()

# Display results
print("\nRESULTS\n")

print("Total distance traveled:", sum(distances[i, j, k] + pyomo.value(model.x[i, j, k]) for i in customers for j in customers for k in vehicles if i != j))

if results.solver.termination_condition == pyomo.TerminationCondition.optimal:
   
    # Display the routes
    routes = []
    for k in vehicles:
        route = [(i, j) for i in customers for j in customers if pyomo.value(model.x[i, j, k])]
        routes.append(route)
        print(f"Vehicle {k + 1} route: {[customer_names[i] for i, j in route]}")
        print("Goods for cus: ", goods_for_cus)

    # Plot the routes
    plot_routes(routes, depot, customer_locations)
else:
    print("Solver did not find an optimal solution. Check the model and solver settings.")
    