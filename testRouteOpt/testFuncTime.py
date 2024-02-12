# import needed libraries
import pyomo.environ as pyomo
from pyomo.opt import SolverFactory
import random
import logging
import math
import matplotlib.pyplot as plt
import json
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(filename='pyomo_ipy.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

#go to log
def distance(location1, location2):
    x_diff = location1[0] - location2[0]
    y_diff = location1[1] - location2[1]
    return math.sqrt(x_diff**2 + y_diff**2)

# def create_datetime(year, month, day, hour, minute):
#     return datetime(year, month, day, hour, minute)

def solve_vehicle_routing_problem(num_customers, num_vehicles, num_goods, time_windows):
    try:
        # Generate random data
        customers = range(1, num_customers + 1)
        vehicles = range(num_vehicles)
        goods = range(num_goods)

        # Coordinates of depot and customers
        depot = (4, 4)
        # Customer names
        customer_names = {i: f"ID_{i}" for i in customers}
        customer_locations = {i: (random.uniform(0, num_customers), random.uniform(0, num_vehicles)) for i in customers}
        # Generate random integer goods values for each customer
        unique_goods_values = list(range(num_goods))
        random.shuffle(unique_goods_values)

        goods_for_cus = {i: unique_goods_values[j % num_goods] for j, i in enumerate(customers)}
        # Calculate distances between locations
        distances = {(i, j, k): distance(customer_locations[i], customer_locations[j]) for i in customers for j in customers for k in vehicles if i != j}

        # Create Pyomo model
        model = pyomo.ConcreteModel()

        # Decision Variables
        model.x = pyomo.Var(customers, customers, vehicles, domain=pyomo.Binary)
        model.goods = pyomo.Var(customers, vehicles, domain=pyomo.NonNegativeReals)  # New variable for goods carried
        model.arrival_time = pyomo.Var(customers, vehicles, domain=pyomo.NonNegativeReals)

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
        vehicle_capacity = 10  # Example capacity, adjust as needed
        model.capacity_constraint = pyomo.ConstraintList()
        for k in vehicles:
            model.capacity_constraint.add(
                expr=sum(goods_for_cus[i] * model.goods[i, k] for i in customers) <= vehicle_capacity
            )

        # Time window constraints
        model.time_window_constraint = pyomo.ConstraintList()
        for i in customers:
            start_time = time_windows.get(i, {'start': {'hour': datetime.now().hour, 'minute': datetime.now().minute}})['start']
            print("start time type", type(start_time))
            end_time = time_windows.get(i, {'end': {'hour': datetime.now().hour, 'minute': datetime.now().minute}})['end']
            for k in vehicles:
                model.time_window_constraint.add(
                    model.arrival_time[i, k] >= start_time['hour'] * 60 + start_time['minute']
                )
                model.time_window_constraint.add(
                    model.arrival_time[i, k] <= end_time['hour'] * 60 + end_time['minute']
                )

        # Arrival time constraints
        M = 10000  # A large constant to represent infinity
        for i in customers:
            for j in customers:
                for k in vehicles:
                    if i != j:
                        model.time_constraint = pyomo.Constraint(
                            expr=model.arrival_time[i, k] + distances[i, j, k] <= model.arrival_time[j, k] + M * (1 - model.x[i, j, k])
                        )

        # Solve the VRP problem
        solver = SolverFactory('cbc')
        results = solver.solve(model, tee=True)

        # Display results
        print("\nRESULTS\n")

        print("Total distance traveled:", sum(distances[i, j, k] + pyomo.value(model.x[i, j, k]) for i in customers for j in customers for k in vehicles if i != j))
        print("Goods: ", goods_for_cus)
        
        if results.solver.termination_condition == pyomo.TerminationCondition.optimal:
            # Display the routes
            routes = []
            for k in vehicles:
                route = [(i, j) for i in customers for j in customers if pyomo.value(model.x[i, j, k])]
                routes.append(route)
                print(f"Vehicle {k + 1} route: {[customer_names[i] for i, j in route]}")

            # Plot the routes
            plot_routes(routes, depot, customer_locations)
        else:
            print("Solver did not find an optimal solution. Check the model and solver settings.")

    except Exception as e:
        # Log the exception
        logging.error("An error occurred: %s", str(e))

# Plot routes
def plot_routes(routes, depot, customer_locations):
    plt.figure(figsize=(10, 10))

    # Plot depot
    plt.scatter(*depot, color='black', marker='D', s=100, label='Depot')

    # Plot customer nodes
    for customer, (x, y) in customer_locations.items():
        plt.scatter(x, y, color='blue')
        plt.text(x, y, f"ID_{customer}", fontsize=8, ha='right')
    
    # Define colors for different vehicles
    colors = ['aquamarine', 'coral', 'lime', 'salmon', 'khaki', 'orchid', 
              'peru', 'slate', 'tomato', 'wheat', 'azure', 'bisque', 'cadetblue', 
              'darkorchid', 'firebrick', 'goldenrod', 'limegreen', 'navajowhite',
              'rosybrown', 'seagreen']

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

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(len(sys.argv))
        print("Usage: python script.py num_customers num_vehicles num_goods")
        sys.exit(1)

    num_customers = int(sys.argv[1])
    num_vehicles = int(sys.argv[2])
    num_goods = int(sys.argv[3])

    time_windows = {}
    for i in range(1, num_customers + 1):
        try:
            start_hour = int(input(f"Enter start hour for customer {i}: "))
            start_minute = int(input(f"Enter start minute for customer {i}: "))
            
            end_hour = int(input(f"Enter end hour for customer {i}: "))
            end_minute = int(input(f"Enter end minute for customer {i}: "))

            # Store the time windows in the dictionary
            time_windows[i] = {
                'customer_ID': i,
                'start': {'hour': start_hour, 'minute': start_minute},
                'end': {'hour': end_hour, 'minute': end_minute}
            }

        except ValueError:
            print("Invalid time input. Use integers for hours and minutes.")
            sys.exit(1)

    input_data = {
        "num_customers": num_customers,
        "num_vehicles": num_vehicles,
        "num_goods": num_goods,
        "time_for_sent": time_windows
    }

    with open('customers.log', 'a') as json_file:
        # Use json.dump to write the data to the file
        json.dump(input_data, json_file)

        # Add a newline character to separate the appended data
        json_file.write('\n')

    solve_vehicle_routing_problem(num_customers, num_vehicles, num_goods, time_windows)
    # plot_routes(num_customers, num_vehicles, num_goods)