import pyomo.environ as pyomo
from pyomo.opt import SolverFactory
import random
import logging
import math
import json
from datetime import datetime
import sys
import folium
from nanoid import generate

# Configure logging
logging.basicConfig(filename='pyomo_ipy.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Distance function that wait to fix (Use Pythagoras' theory)
def distance(location1, location2):
    x_diff = location1[0] - location2[0]
    y_diff = location1[1] - location2[1]
    return math.sqrt(x_diff**2 + y_diff**2)

def get_user_ID(customer_id):
    # Generate a unique ID using nanoid with 13 characters
    customer_id = generate(size=13)
    return customer_id

def get_user_goods(customer_id):
        return int(input(f"Enter goods ID for customer {customer_id}: "))
    
# def get_user_input_time(customer_id):
#     try:
#         start_hour = int(input(f"Enter start hour for customer {customer_id}: "))
#         start_minute = int(input(f"Enter start minute for customer {customer_id}: "))
        
#         end_hour = int(input(f"Enter end hour for customer {customer_id}: "))
#         end_minute = int(input(f"Enter end minute for customer {customer_id}: "))

#         return {
#             'start': {'hour': start_hour, 'minute': start_minute},
#             'end': {'hour': end_hour, 'minute': end_minute}
#         }

    # except ValueError:
    #     print("Invalid time input. Use integers for hours and minutes.")
    #     sys.exit(1)
    
def get_user_input_set():
    start_latitude = float(input("Enter the starting latitude: "))
    start_longitude = float(input("Enter the starting longitude: "))

    start_point = (start_latitude, start_longitude)

    time_windows = {}
    customer_locations = {}

    for i in range(1, num_customers + 1):
        latitude = float(input(f"Enter latitude for customer {i}: "))
        longitude = float(input(f"Enter longitude for customer {i}: "))
        customer_locations[i] = (latitude, longitude)

        start_hour = int(input(f"Enter start hour for customer {i}: "))
        start_minute = int(input(f"Enter start minute for customer {i}: "))
        end_hour = int(input(f"Enter end hour for customer {i}: "))
        end_minute = int(input(f"Enter end minute for customer {i}: "))

        time_windows[i] = {
            'customer_ID': i,
            'start': {'hour': start_hour, 'minute': start_minute},
            'end': {'hour': end_hour, 'minute': end_minute}
        }

    return num_customers, num_vehicles, num_goods, start_point, customer_locations, time_windows

def write_input_data_to_json(input_data):
    with open('input_data.json', 'a') as json_file:
        json.dump(input_data, json_file, indent=2)

def solve_vehicle_routing_problem(num_customers, num_vehicles, num_goods):
    try:
        # Generate random data
        customers = range(1, num_customers + 1)
        vehicles = range(num_vehicles)
        goods = range(num_goods)

        # Coordinates of depot and customers
        depot = (4, 4)
        # Customer names
        customer_names = {i: f"ID_{i}" for i in customers}
        customer_locations = {i: (random.uniform(0, 10), random.uniform(0, 10)) for i in customers}  # Adjust the range as needed
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
            time_window = get_user_input_set(i)
            for k in vehicles:
                model.time_window_constraint.add(
                    model.arrival_time[i, k] >= time_window['start']['hour'] * 60 + time_window['start']['minute']
                )
                model.time_window_constraint.add(
                    model.arrival_time[i, k] <= time_window['end']['hour'] * 60 + time_window['end']['minute']
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

            # Plot the routes on a map using Folium
            plot_routes_on_map(depot, customer_locations, routes)

            # Write input data to JSON file
            input_data = {
                "num_customers": num_customers,
                "num_vehicles": num_vehicles,
                "num_goods": num_goods,
                "time_for_sent": {i: get_user_input_set(i) for i in customers}
            }
            write_input_data_to_json(input_data)
        else:
            print("Solver did not find an optimal solution. Check the model and solver settings.")

    except Exception as e:
        # Log the exception
        logging.error("An error occurred: %s", str(e))

def plot_routes_on_map(depot, customer_locations, routes):
    # Create a Folium map centered around the depot
    map_center = depot
    route_map = folium.Map(location=map_center, zoom_start=14)

    # Add markers for the depot and customers
    folium.Marker(depot, popup='Depot', icon=folium.Icon(color='black', icon='home')).add_to(route_map)
    for customer, location in customer_locations.items():
        folium.Marker(location, popup=f'Customer {customer}', icon=folium.Icon(color='red', icon='user')).add_to(route_map)

    # Draw lines for each route
    for k, route in enumerate(routes):
        color = get_color(k)
        coordinates = [depot] + [customer_locations[i] for i, j in route] + [depot]
        folium.PolyLine(coordinates, color=color, weight=2.5, opacity=1).add_to(route_map)

    # Save the map to an HTML file
    route_map.save('vehicle_routes_map.html')

def get_color(index):
    # Define colors for different routes
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'brown', 'gray', 'olive', 'cyan']
    return colors[index % len(colors)]

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py num_customers num_vehicles num_goods")
        sys.exit(1)

    num_customers = int(sys.argv[1])
    num_vehicles = int(sys.argv[2])
    num_goods = int(sys.argv[3])

    # Comment out the following lines
    # num_customers, num_vehicles, num_goods, time_windows = get_user_input_set()
    # depot, customer_locations, goods_for_cus, distances = generate_random_data(num_customers, num_vehicles, num_goods)

    # Replace with the function call
    num_customers, num_vehicles, num_goods, time_windows = get_user_input_set()

    # Rest of your code remains unchanged
    solve_vehicle_routing_problem(num_customers, num_vehicles, num_goods)
