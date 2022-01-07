

def get_model(building):
    M = ConcreteModel()

    opt = SolverFactory('glpk')
    result_obj = opt.solve(model, tee=True)
    model.pprint()
