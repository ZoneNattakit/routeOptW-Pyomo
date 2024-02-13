import logging
import math
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import json
from solveRoute import *

# Configure logging
logging.basicConfig(filename='pyomo_ipy.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def distance(location1, location2):
    x_diff = location1[0] - location2[0]
    y_diff = location1[1] - location2[1]
    return math.sqrt(x_diff**2 + y_diff**2)

def get_user_input_time(customer_id):
    try:
        start_hour = int(input(f"Enter start hour for customer {customer_id}: "))
        start_minute = int(input(f"Enter start minute for customer {customer_id}: "))
        
        end_hour = int(input(f"Enter end hour for customer {customer_id}: "))
        end_minute = int(input(f"Enter end minute for customer {customer_id}: "))

        return {
            'start': {'hour': start_hour, 'minute': start_minute},
            'end': {'hour': end_hour, 'minute': end_minute}
        }

    except ValueError:
        print("Invalid time input. Use integers for hours and minutes.")
        sys.exit(1)
        
def write_input_data_to_json(input_data):
    with open('input_data.json', 'a') as json_file:
        json.dump(input_data, json_file)
        json_file.write('\n')
        
def get_position(customer_id):
    
    lat = float(input(f"Enter latitude for customer {customer_id}: " ))
    longt = float(input(f"Enter longtitude for customer {customer_id}: "))
    
    return lat, longt
        

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
        print("Usage: python script.py num_customers num_vehicles num_goods")
        sys.exit(1)

    num_customers = int(sys.argv[1])
    num_vehicles = int(sys.argv[2])
    num_goods = int(sys.argv[3])

    solve_vehicle_routing_problem(num_customers, num_vehicles, num_goods)
