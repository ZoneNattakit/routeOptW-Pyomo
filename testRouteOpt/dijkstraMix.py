from pyomo.environ import *
import logging

# Configure logging
logging.basicConfig(filename='mixTest.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Your code that might raise an exception
    # Note: This section is currently empty. You may want to add code that can raise an exception.
    logging.info('Successful')
except Exception as e:
    # Log the exception
    logging.error("An error occurred: %s", str(e))


# สร้างโมเดล
model = ConcreteModel()

# กำหนดข้อมูลกราฟ
nodes = ['A', 'B', 'C', 'D']
edges = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5), ('C', 'D', 1)]

# กำหนดตัวแปร
model.x = Var(edges, domain=Binary)

# กำหนดฟังก์ชั่น
model.obj = Objective(expr=sum(model.x[i, j, w] * w for (i, j, w) in edges), sense=minimize)

# กำหนดเงื่อนไข
model.constraints = ConstraintList()
for node in nodes:
    # ฟังก์ชั่นต้องผ่านทุกระยะทางจาก A ถึง D
    if node != 'A':
        model.constraints.add(sum(model.x[i, j, w] for (i, j, w) in edges if j == node) == 1)
    if node != 'D':
        model.constraints.add(sum(model.x[i, j, w] for (i, j, w) in edges if i == node) == 1)

# การเรียก CBC SolverFactory
solver = SolverFactory('cbc')
solver.solve(model, tee=True)

# แสดงผลลัพธ์
print("Optimal solution:")
for (i, j, w) in edges:
    if value(model.x[i, j, w]) == 1:
        print(f"From {i} to {j} distance: {w}")
        
