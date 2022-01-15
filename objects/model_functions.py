import pyomo.environ as pe
import pyomo.gdp as gdp


def define_vars_for_model(building):
    model = building.model
    # die Räume des Gebäudes entsprechend der Liste room_idx
    model.room_idx = range(building.nr_of_rooms)
    model.W = building.width
    model.H = building.len
    # model.R = pe.Param(model.room_idx,initialize=[r.aspect_ratio for r in building.rooms],mutable=False)
    model.R = 1.6180339887
    model.min_area = [r.min_area for r in building.rooms]
    model.max_area = [r.max_area for r in building.rooms]
    model.min_side_len = pe.Var(model.room_idx, bounds=(50, max(building.len, building.width)),
                                within=pe.NonNegativeReals)
    model.living_space = [r.living_space for r in building.rooms]
    model.x = pe.Var(model.room_idx, bounds=(0, building.width), within=pe.NonNegativeReals)
    model.y = pe.Var(model.room_idx, bounds=(0, building.len), within=pe.NonNegativeReals)
    model.floor = pe.Var(model.room_idx, bounds=(0, building.max_floor - 1), within=pe.Integers)
    model.h = pe.Var(model.room_idx, bounds=(50, building.len), within=pe.NonNegativeReals)
    model.w = pe.Var(model.room_idx, bounds=(50, building.width), within=pe.NonNegativeReals)
    model.floor_constraints = pe.ConstraintList()
    model.dist_x = pe.Var(model.room_idx, model.room_idx,
                          bounds=(0, 2 * building.width + building.max_floor * building.floor_height),
                          within=pe.NonNegativeReals)
    model.dist_y = pe.Var(model.room_idx, model.room_idx,
                          bounds=(0, 2 * building.len + building.max_floor * building.floor_height),
                          within=pe.NonNegativeReals)
    model.building = building
    return model


def disjunction_distance_x_rule(model, i, j):
    ref_x = model.building.reference_x
    floor_height = model.building.floor_height

    return [
        # i links von j auf gleichem floor
        [model.x[i] <= model.x[j],
         model.floor[i] == model.floor[j],
         model.dist_x == (model.x[j] + 0.5 * model.w[j]) - (model.x[i] + 0.5 * model.w[i])
         ],
        # i rechts von j auf gleichem floor
        [model.x[i] >= model.x[j],
         model.floor[i] == model.floor[j],
         model.dist_x == (model.x[i] + 0.5 * model.w[i]) - (model.x[j] + 0.5 * model.w[j])
         ],
        #  i auf floor unterhalb, situation ref_x lage 1
        [model.floor[i] <= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] >= ref_x,
         model.x[j] + 0.5 * model.w[j] >= ref_x,
         model.dist_x == ((model.x[j] + 0.5 * model.w[j]) - ref_x) + (
                     (model.x[i] + 0.5 * model.w[i]) - ref_x) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        #  i auf floor unterhalb, situation ref_x lage 2
        [model.floor[i] <= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] <= ref_x,
         model.x[j] + + 0.5 * model.w[j] >= ref_x,
         model.dist_x == ((model.x[j] + 0.5 * model.w[j]) - ref_x) + (
                     ref_x - model.x[i] - 0.5 * model.w[i]) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        # i links von j auf, i auf floor unterhalb, situation ref_x lage 3
        [model.floor[i] <= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] >= ref_x,
         model.x[j] + + 0.5 * model.w[j] <= ref_x,
         model.dist_x == (ref_x - model.x[j] - 0.5 * model.w[j]) + (
                     (model.x[i] + 0.5 * model.w[i]) - ref_x) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        # i links von j auf, i auf floor unterhalb, situation ref_x lage 4
        [model.floor[i] <= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] <= ref_x,
         model.x[j] + 0.5 * model.w[j] <= ref_x,
         model.dist_x == (ref_x - model.x[j] - 0.5 * model.w[j]) + (
                     ref_x - model.x[i] - 0.5 * model.w[i]) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        #  i auf floor oberhalb, situation ref_x lage 1
        [model.floor[i] >= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] >= ref_x,
         model.x[j] + 0.5 * model.w[j] >= ref_x,
         model.dist_x == ((model.x[j] + 0.5 * model.w[j]) - ref_x) + (
                     (model.x[i] + 0.5 * model.w[i]) - ref_x) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        #  i auf floor oberhalb, situation ref_x lage 2
        [model.floor[i] >= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] <= ref_x,
         model.x[j] + + 0.5 * model.w[j] >= ref_x,
         model.dist_x == ((model.x[j] + 0.5 * model.w[j]) - ref_x) + (
                     ref_x - model.x[i] - 0.5 * model.w[i]) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        # i links von j auf, i auf floor oberhalb, situation ref_x lage 3
        [model.floor[i] >= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] <= ref_x,
         model.x[j] + + 0.5 * model.w[j] <= ref_x,
         model.dist_x == (ref_x - model.x[j] - 0.5 * model.w[j]) + (
                     ref_x - model.x[i] - 0.5 * model.w[i]) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

        # i links von j auf, i auf floor oberhalb, situation ref_x lage 4
        [model.floor[i] >= model.floor[j] + 1,
         model.x[i] + 0.5 * model.w[i] <= ref_x,
         model.x[j] + 0.5 * model.w[j] <= ref_x,
         model.dist_x == (ref_x - model.x[j] - 0.5 * model.w[j]) + (
                     ref_x - model.x[i] - 0.5 * model.w[i]) + 0.5 * floor_height * (model.floor[j] - model.floor[i])
         ],

    ]


def define_distance_constraints(building):
    model = building.model
    model.distance_x = gdp.Disjunction(model.room_idx, model.room_idx,
                                       rule=disjunction_distance_x_rule, xor=False)
    model.distance_y = gdp.Disjunction(model.room_idx, model.room_idx,
                                       rule=disjunction_distance_y_rule, xor=False)


def define_floor_constraints(building):
    model = building.model
    for fc in building.floor_constraints:
        room_idx = fc.room.idx
        floor_idx = fc.floor
        model.floor_constraints.add((floor_idx, model.floor[room_idx], floor_idx))


def disjunction_adjacency_rule(model, i, j):
    adjacency = model.building.get_adjacency(i, j)
    if adjacency is not None:
        touch_len = adjacency.touch_len
        model.floor_constraints.add(model.floor[j] - model.floor[i] <= 0)  # must be one same floor
        model.floor_constraints.add(model.floor[i] - model.floor[j] <= 0)
        return [

            # i oberhalb von j
            [model.y[i] + model.h[i] == model.y[j],
             model.x[i] >= model.x[j],
             model.x[i] <= model.x[j] + model.w[j],
             model.x[i] + model.w[i] >= model.x[j] + model.w[j],
             model.x[j] + model.w[j] - model.x[i] >= touch_len],  # ragt nach rechts raus

            [model.y[i] + model.h[i] == model.y[j],
             model.x[i] <= model.x[j],
             model.x[i] + model.w[i] >= model.x[j],
             model.x[i] + model.w[i] <= model.x[j] + model.w[j],  # aber nicht über volle Fläche
             model.x[i] + model.w[i] - model.x[j] >= touch_len],  # ragt nach links raus

            [model.y[i] + model.h[i] == model.y[j],
             model.x[i] >= model.x[j],
             model.x[i] + model.w[i] <= model.x[j] + model.w[j],
             model.w[i] >= touch_len],  # j ragt links und rechts raus

            [model.y[i] + model.h[i] == model.y[j],
             model.x[i] <= model.x[j],
             model.x[i] + model.w[i] >= model.x[j] + model.w[j],
             model.w[j] >= touch_len],  # i ragt li und re über j raus

            # i unterhalb von j

            [model.y[i] == model.y[j] + model.h[j],
             model.x[i] >= model.x[j],
             model.x[i] <= model.x[j] + model.w[j],
             model.x[i] + model.w[i] >= model.x[j] + model.w[j],
             model.x[j] + model.w[j] - model.x[i] >= touch_len],  # i ragt nach rechts raus

            [model.y[i] == model.y[j] + model.h[j],
             model.x[i] <= model.x[j],
             model.x[i] + model.w[i] >= model.x[j],
             model.x[i] + model.w[i] <= model.x[j] + model.w[j],  # aber nicht über volle Fläche
             model.x[i] + model.w[i] - model.x[j] >= touch_len],  # ragt nach links raus

            [model.y[i] == model.y[j] + model.h[j],
             model.x[i] >= model.x[j],
             model.x[i] + model.w[i] <= model.x[j] + model.w[j],
             model.w[i] >= touch_len],  # j ragt links und rechts raus

            [model.y[i] == model.y[j] + model.h[j],
             model.x[i] <= model.x[j],
             model.x[i] + model.w[i] >= model.x[j] + model.w[j],
             model.w[j] >= touch_len],  # i ragt li und re über j raus

            # i links von j

            [model.x[i] + model.w[i] == model.x[j],
             model.y[i] <= model.y[j],
             model.y[i] + model.h[i] <= model.y[j] + model.h[j],
             model.y[i] + model.h[i] - model.y[j] >= touch_len],
            # i ragt nach oben raus, geht aber nicht bis zum unteren Ende von J

            [model.x[i] + model.w[i] == model.x[j],
             model.y[i] >= model.y[j],  # ragt nach unten raus, geht  nicht oberen Ende von J
             model.y[i] <= model.y[j] + model.h[j],
             model.y[i] + model.h[i] >= model.y[j] + model.h[j],  # aber nicht über volle Fläche
             model.y[j] + model.h[j] - model.y[i] >= touch_len],

            [model.x[i] + model.w[i] == model.x[j],
             model.y[i] >= model.y[j],
             model.y[i] + model.h[i] <= model.y[j] + model.h[j],
             model.h[i] >= touch_len],  # j ragt oben und unten raus

            [model.x[i] + model.w[i] == model.x[j],
             model.y[i] <= model.y[j],
             model.y[i] + model.h[i] >= model.y[j] + model.h[j],
             model.h[j] >= touch_len],  # i ragt li und re über j raus

            # i rechts von j

            [model.x[j] + model.w[j] == model.x[i],
             model.y[i] <= model.y[j],
             model.y[i] + model.h[i] <= model.y[j] + model.h[j],
             model.y[i] + model.h[i] - model.y[j] >= touch_len],
            # i ragt nach oben raus, geht aber nicht bis zum unteren Ende von J

            [model.x[j] + model.w[j] == model.x[i],
             model.y[i] >= model.y[j],  # ragt nach unten raus, geht  nicht oberen Ende von J
             model.y[i] <= model.y[j] + model.h[j],
             model.y[i] + model.h[i] >= model.y[j] + model.h[j],  # aber nicht über volle Fläche
             model.y[j] + model.h[j] - model.y[i] >= touch_len],

            [model.x[j] + model.w[j] == model.x[i],
             model.y[i] >= model.y[j],
             model.y[i] + model.h[i] <= model.y[j] + model.h[j],
             model.h[i] >= touch_len],  # j ragt oben und unten raus

            [model.x[j] + model.w[j] == model.x[i],
             model.y[i] <= model.y[j],
             model.y[i] + model.h[i] >= model.y[j] + model.h[j],
             model.h[j] >= touch_len],  # i ragt li und re über j raus

        ]

    else:
        return gdp.Disjunction.Skip


def define_Constraints_adjacency(building):
    model = building.model
    model.adjacency = gdp.Disjunction(model.room_idx, model.room_idx,
                                      rule=disjunction_adjacency_rule, xor=False)


def disjunction_no_intersection_rule(model, i, j):
    if i < j:
        return [[model.y[i] + model.h[i] <= model.y[j]],  # i above j
                [model.y[i] >= model.y[j] + model.h[j]],  # i below j
                [model.x[i] + model.w[i] <= model.x[j]],  # i left j
                [model.x[j] + model.w[j] <= model.x[i]],  # i right j
                [model.floor[i] >= model.floor[j] + 1],
                [model.floor[j] >= model.floor[i] + 1]
                ]
    else:
        return gdp.Disjunction.Skip


def define_Constraints_no_intersection(building):
    model = building.model
    model.no_intersection = gdp.Disjunction(model.room_idx, model.room_idx,
                                            rule=disjunction_no_intersection_rule, xor=False)


# DA müssen wir das tun
def disjunction_ratio_rule(model, i):
    return [[model.R * 0.98 <= model.w[i] / model.h[i] <= model.R * 1.02],
            [model.R * 0.98 <= model.h[i] / model.w[i] <= model.R * 1.02]]


def define_Constraints_ratio(building):
    model = building.model
    model.len_ratio = gdp.Disjunction(model.room_idx, rule=disjunction_ratio_rule)


def min_len_rule_w(model, i):
    return model.w[i] >= model.min_side_len[i]


def min_len_rule_h(model, i):
    return model.h[i] >= model.min_side_len[i]


def define_Constraints_min_side_len(building):
    model = building.model
    model.min_len_constraint_w = pe.Constraint(model.room_idx, rule=min_len_rule_w)
    model.min_len_constraint_h = pe.Constraint(model.room_idx, rule=min_len_rule_h)


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
        # expr=sum(model.w[i] for i in model.room_idx),
        expr=sum(model.min_side_len[i] for i in model.room_idx),
        sense=pe.maximize)
