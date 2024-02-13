import pyomo
from pyomo.opt import SolverFactory
import random 
from testFuncTime import plot_routes, get_user_input_time,  write_input_data_to_json, distance
import logging
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
            time_window = get_user_input_time(i)
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

            # Plot the routes
            plot_routes(routes, depot, customer_locations)
            
             # Write input data to JSON file
            input_data = {
                "num_customers": num_customers,
                "num_vehicles": num_vehicles,
                "num_goods": num_goods,
                "time_for_sent": {i: get_user_input_time(i) for i in customers}
            }
            write_input_data_to_json(input_data)
        else:
            print("Solver did not find an optimal solution. Check the model and solver settings.")

    except Exception as e:
        # Log the exception
        logging.error("An error occurred: %s", str(e))
