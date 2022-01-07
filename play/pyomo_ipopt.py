# rosenbrock.py: A Pyomo model for the Rosenbrock problem
from pyomo.environ import *


def rosenbrock(m):
    return (1.0-m.x)**2 + 100.0*(m.y - m.x**2)**2

if __name__ == '__main__':
    model = ConcreteModel()
    model.x = Var(initialize=1.5)
    model.y = Var(initialize=1.5)

    model.obj = Objective(rule=rosenbrock, sense=minimize)


    SolverFactory('ipopt').solve(model, tee=True)
    model.pprint()
