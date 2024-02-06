#first step
- add time and fix condition use less car >> checked
- make it method >> checked
- make it function >> checked
- increase performance > testing


#condition
- goods and customer amount 60-100 > testing not good but in customer's condition (test 5 customers)
- former send before > not good but work
- add time limit for each customer >> checked
- make good format > in process
- check and cal vehicles > in process (make function)
- wait map api >! wait (Longdo map)

password
@Dmin1234

# Ensure that each vehicle must visit at least one customer
        # model.at_least_one_customer_constraint = pyomo.ConstraintList()
        # for k in vehicles:
        #     model.at_least_one_customer_constraint.add(
        #         expr=sum(model.x[i, j, k] for i in customers for j in customers) >= 1
        #     )