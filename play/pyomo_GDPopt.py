

from pyomo.environ import *
from pyomo.gdp import *

# Create a simple model

if __name__ == '__main__':
    model = ConcreteModel(name='LOA example')
    model.x = Var(bounds=(-1.2, 2))
    model.y = Var(bounds=(-10,10))
    model.c = Constraint(expr= model.x + model.y == 1)
    model.fix_x = Disjunct()
    model.fix_x.c = Constraint(expr=model.x == 0)
    model.fix_y = Disjunct()
    model.fix_y.c = Constraint(expr=model.y == 0)
    model.d = Disjunction(expr=[model.fix_x, model.fix_y])
    model.objective = Objective(expr=model.x + 0.1*model.y, sense=minimize)
    results = SolverFactory('gdpopt').solve(model, strategy='LOA', mip_solver='glpk')

    model.display()
