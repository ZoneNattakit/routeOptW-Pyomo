import pyomo
from pyomo.opt import SolverFactory
import random
from testFuncTime import plot_routes, get_user_input_time, write_input_data_to_json, distance
import logging

class VehicleRoutingProblemSolver:
    def __init__(self, num_customers, num_vehicles, num_goods):
        self.num_customers = num_customers
        self.num_vehicles = num_vehicles
        self.num_goods = num_goods

        self.customers = range(1, num_customers + 1)
        self.vehicles = range(num_vehicles)
        self.goods = range(num_goods)

        self.depot = (4, 4)
        self.customer_names = {i: f"ID_{i}" for i in self.customers}
        self.customer_locations = {i: (random.uniform(0, num_customers), random.uniform(0, num_vehicles)) for i in self.customers}
        unique_goods_values = list(range(num_goods))
        random.shuffle(unique_goods_values)

        self.goods_for_cus = {i: unique_goods_values[j % num_goods] for j, i in enumerate(self.customers)}
        self.distances = {(i, j, k): distance(self.customer_locations[i], self.customer_locations[j]) for i in self.customers for j in self.customers for k in self.vehicles if i != j}

        self.model = pyomo.ConcreteModel()

    def create_variables(self):
        self.model.x = pyomo.Var(self.customers, self.customers, self.vehicles, domain=pyomo.Binary)
        self.model.goods = pyomo.Var(self.customers, self.vehicles, domain=pyomo.NonNegativeReals)  # New variable for goods carried
        self.model.arrival_time = pyomo.Var(self.customers, self.vehicles, domain=pyomo.NonNegativeReals)

    def create_objective(self):
        self.model.obj = pyomo.Objective(
            expr=(
                sum(self.distances[i, j, k] * self.model.x[i, j, k] for i in self.customers for j in self.customers for k in self.vehicles if i != j) +
                sum(self.goods_for_cus[i] * self.model.goods[i, k] for i in self.customers for k in self.vehicles)
            ),
            sense=pyomo.minimize
        )

    def create_constraints(self):
        self.create_visits_constraint()
        self.create_depot_constraint()
        self.create_capacity_constraint()
        self.create_time_window_constraints()
        self.create_arrival_time_constraints()

    def create_visits_constraint(self):
        self.model.visits_constraint = pyomo.ConstraintList()
        for i in self.customers:
            self.model.visits_constraint.add(expr=sum(self.model.x[i, j, k] for j in self.customers for k in self.vehicles) == 1)

    def create_depot_constraint(self):
        self.model.depot_constraint = pyomo.ConstraintList()
        for k in self.vehicles:
            self.model.depot_constraint.add(expr=sum(self.model.x[i, j, k] for j in self.customers for k in self.vehicles) == 1)

    def create_capacity_constraint(self):
        vehicle_capacity = 10  # Example capacity, adjust as needed
        self.model.capacity_constraint = pyomo.ConstraintList()
        for k in self.vehicles:
            self.model.capacity_constraint.add(
                expr=sum(self.goods_for_cus[i] * self.model.goods[i, k] for i in self.customers) <= vehicle_capacity
            )

    def create_time_window_constraints(self):
        self.model.time_window_constraint = pyomo.ConstraintList()
        for i in self.customers:
            time_window = get_user_input_time(i)
            for k in self.vehicles:
                self.model.time_window_constraint.add(
                    self.model.arrival_time[i, k] >= time_window['start']['hour'] * 60 + time_window['start']['minute']
                )
                self.model.time_window_constraint.add(
                    self.model.arrival_time[i, k] <= time_window['end']['hour'] * 60 + time_window['end']['minute']
                )

    def create_arrival_time_constraints(self):
        M = 10000  # A large constant to represent infinity
        for i in self.customers:
            for j in self.customers:
                for k in self.vehicles:
                    if i != j:
                        self.model.time_constraint = pyomo.Constraint(
                            expr=self.model.arrival_time[i, k] + self.distances[i, j, k] <= self.model.arrival_time[j, k] + M * (1 - self.model.x[i, j, k])
                        )

    def solve_problem(self):
        try:
            # Solve the VRP problem
            solver = SolverFactory('cbc')
            results = solver.solve(self.model, tee=True)

            # Display results
            print("\nRESULTS\n")

            print("Total distance traveled:", sum(self.distances[i, j, k] + pyomo.value(self.model.x[i, j, k]) for i in self.customers for j in self.customers for k in self.vehicles if i != j))
            print("Goods: ", self.goods_for_cus)

            if results.solver.termination_condition == pyomo.TerminationCondition.optimal:
                # Display the routes
                routes = []
                for k in self.vehicles:
                    route = [(i, j) for i in self.customers for j in self.customers if pyomo.value(self.model.x[i, j, k])]
                    routes.append(route)
                    print(f"Vehicle {k + 1} route: {[self.customer_names[i] for i, j in route]}")

                # Plot the routes
                plot_routes(routes, self.depot, self.customer_locations)

                # Write input data to JSON file
                input_data = {
                    "num_customers": self.num_customers,
                    "num_vehicles": self.num_vehicles,
                    "num_goods": self.num_goods,
                    "time_for_sent": {i: get_user_input_time(i) for i in self.customers}
                }
                write_input_data_to_json(input_data)
            else:
                print("Solver did not find an optimal solution. Check the model and solver settings.")

        except Exception as e:
            # Log the exception
            logging.error("An error occurred: %s", str(e))

# Example usage:
num_customers = 5
num_vehicles = 2
num_goods = 3
vrp_solver = VehicleRoutingProblemSolver(num_customers, num_vehicles, num_goods)
vrp_solver.create_variables()
vrp_solver.create_objective()
vrp_solver.create_constraints()
vrp_solver.solve_problem()

