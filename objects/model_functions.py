import pyomo.environ as pe
import pyomo.gdp as gdp


def define_vars_for_model(building):
    model = building.model
    # die Räume des Gebäudes entsprechend der Liste room_idx
    model.room_idx = range(building.nr_of_rooms)
    model.W = building.width
    model.H = building.len
    model.R = 1.6180339887
    model.min_area = [r.min_area for r in building.rooms]
    model.max_area = [r.max_area for r in building.rooms]
    model.x = pe.Var(model.room_idx, bounds=(0, building.width), within=pe.NonNegativeReals)
    model.y = pe.Var(model.room_idx, bounds=(0, building.len), within=pe.NonNegativeReals)
    model.floor = pe.Var(model.room_idx, bounds=(0, building.max_floor - 1), within=pe.Integers)
    model.h = pe.Var(model.room_idx, bounds=(100, building.len), within=pe.NonNegativeReals)
    model.w = pe.Var(model.room_idx, bounds=(100, building.width), within=pe.NonNegativeReals)
    model.floor_constraints = pe.ConstraintList()
    model.adjacency_constraints = pe.ConstraintList()
    model.building = building
    return model


def define_floor_constraints(building):
    model = building.model
    for fc in building.floor_constraints:
        room_idx = fc.room.idx
        floor_idx = fc.floor
        model.floor_constraints.add((floor_idx, model.floor[room_idx], floor_idx))


def disjunction_adjacency_rule(model, i, j):
    adjacency = model.building.get_adjacency(i, j)
    if not adjacency is None:
        touch_len = adjacency.touch_len
        model.floor_constraints.add((model.floor[j], model.floor[i], model.floor[j]))  # must be one same floor
        return [[model.y[i] + model.h[i] == model.y[j],
                 model.x[i] >= model.x[j], model.x[i] <= model.x[j] + model.w[j],
                 model.x[i] + model.w[i] >= model.x[j] + model.w[j],
                 model.x[j] + model.w[j] - model.x[i] >= touch_len], # i oberhalb von j, ragt nach rechts raus

                [model.y[i] + model.h[i] == model.y[j],
                 model.x[i] <= model.x[j], model.x[i] + model.w[i] >= model.x[j],
                 model.x[i] + model.w[i] - model.x[j] >= touch_len],  # i oberhalb von j, ragt nach links raus



                [model.y[i] >= model.y[j] + model.h[j]],
                [model.x[i] + model.w[i] <= model.x[j]],
                [model.x[i] + model.w[i] <= model.x[j]],
                ]

    else:
        return gdp.Disjunction.Skip


def define_Constraints_adjacency(building):
    model = building.model
    model.no_intersection = gdp.Disjunction(model.room_idx, model.room_idx,
                                            rule=disjunction_adjacency_rule, xor=False)


def disjunction_no_intersection_rule(model, i, j):
    if i < j:
        return [[model.y[i] + model.h[i] <= model.y[j]],  # above
                [model.y[i] >= model.y[j] + model.h[j]],  # below
                [model.x[i] + model.w[i] <= model.x[j]],  # left
                [model.x[i] + model.w[i] <= model.x[j]],  # right
                [model.floor[i] >= model.floor[j] + 1],
                [model.floor[j] >= model.floor[i] + 1]
                ]
    else:
        return gdp.Disjunction.Skip


def define_Constraints_no_intersection(building):
    model = building.model
    model.no_intersection = gdp.Disjunction(model.room_idx, model.room_idx,
                                            rule=disjunction_no_intersection_rule, xor=False)


def disjunction_ratio_rule(model, i):
    return [[model.R * 0.98 <= model.w[i] / model.h[i] <= model.R * 1.02],
            [model.R * 0.98 <= model.h[i] / model.w[i] <= model.R * 1.02]
            ]


def define_Constraints_ratio(building):
    model = building.model
    model.ratio = gdp.Disjunction(model.room_idx, rule=disjunction_ratio_rule)


def min_area_rule(model, i):
    return model.w[i] * model.h[i] >= model.min_area[i]


def define_Constraints_min_area(building):
    model = building.model
    model.min_area_constraint = pe.Constraint(model.room_idx, rule=min_area_rule)


def max_area_rule(model, i):
    return model.w[i] * model.h[i] <= model.max_area[i]


def define_Constraints_max_area(building):
    model = building.model
    model.max_area_constraint = pe.Constraint(model.room_idx, rule=max_area_rule)


def horizonal_boundary_rule(model, i):
    return model.x[i] + model.w[i] <= model.W


def vertical_boundary_rule(model, i):
    return model.y[i] + model.h[i] <= model.H


def define_Constrains_in_boundary(building):
    model = building.model
    model.horizonal_boundary = pe.Constraint(model.room_idx, rule=horizonal_boundary_rule)
    model.vertical_boundary = pe.Constraint(model.room_idx, rule=vertical_boundary_rule)


def define_Objective(building):
    model = building.model
    model.value = pe.Objective(
        expr=sum(model.w[i] * model.h[i] for i in model.room_idx),
        sense=pe.maximize)