import cv2
import numpy as np
import pyomo.environ as pe

from objects.building_constraints import *
from objects.connection import Adjacency
from objects.model_functions import *
import os
import time

class Building:
    def __init__(self, building_width_m=10, building_length_m=25, max_floor=1, floor_height_m=2.5):
        self.rooms = []
        self.connections = []
        self.len = building_length_m * 1e2
        self.width = building_width_m * 1e2
        self.model = None
        self.opt_results = None
        self.max_floor = max_floor
        self.floor_constraints = []
        self.floor_height = floor_height_m * 1e2
        # referenzpunkt für abstände
        self.reference_x = 0.
        self.reference_y = 0.

    def add_room(self, room, floor=None):
        idx = self.nr_of_rooms
        room.idx = idx
        room.building = self
        self.rooms.append(room)
        if floor is not None:
            c = FloorConstraint(room, floor)
            self.floor_constraints.append(c)
        return room

    def add_connection(self, connection):
        self.connections.append(connection)

    def get_adjacency(self, from_idx, to_idx):
        for c in self.connections:
            if (type(c) == Adjacency) and (c.from_room.idx == from_idx) and (c.to_room.idx == to_idx):
                return c
        return None

    @property
    def nr_of_rooms(self):
        return len(self.rooms)

    def area_bounds(self):
        min_area, max_area = 0, 0
        for room in self.rooms:
            min_area += room.min_area
            max_area += room.max_area
        return min_area, max_area, self.width * self.len

    def define_model(self):
        self.model = pe.ConcreteModel(name='floorplan')
        define_vars_for_model(self)
        define_Constraints_no_intersection(self)
        define_Constrains_in_boundary(self)
        define_Constraints_min_area(self)
        # define_Constraints_max_area(self)
        define_Constraints_min_side_len(self)
        # define_Constraints_ratio(self)
        define_floor_constraints(self)
        define_Constraints_adjacency(self)
        define_distance_constraints(self)
        define_Objective(self)
        # pe.TransformationFactory('gdp.hull').apply_to(self.model)  #'gdp.bigm' , '
        pe.TransformationFactory('gdp.bigm').apply_to(self.model)

    def optimise_bonmin(self, tee=False,time_limit_sec=3600):
        self.define_model()
        # opt = pe.SolverFactory('gdpopt')  #' gplk
        # opt.options['ma27_pivtol'] = 1e-4
        solver = pe.SolverFactory('bonmim', executable='/home/markus/Bonmin-1.8.8/build/bin/bonmin')
        solver.options.option_file_name = "bonmin.opt"
        with open("bonmin.opt", "w") as f:
            # f.write() # Here you can specify options for Couenne
            # f.write("problem_print_level 7\n")
            f.write("bonmin.milp_strategy find_good_sol\n")
            f.write("bonmin.algorithm B-BB\n")
            # f.write("bonmin.solution_limit  1\n")
            f.write("bonmin.iteration_limit 2147483647\n")
            # f.write("bonmin.tree_search_strategy probed-dive\n")
            f.write("bonmin.variable_selection strong-branching\n")
            f.write("bonmin.bonmin.milp_solver Cbc_D\n")
            f.write("bonmin.milp_strategy  find_good_sol\n")   # find_good_sol
            # f.write("bonmin.milp_strategy  solve_to_optimality\n")   # solve_to_optimality
            f.write("max_iter 10000\n") # ipopt
            f.write("bonmin.nlp_solver  Ipopt\n")
            # f.write("bonmin.print_frequency_time  120\n")
            # f.write("bonmin.print_info_string    yes\n")
            # f.write("bonmin.print_user_options  yes\n")
            f.write("bonmin.pump_for_minlp  yes\n")
            f.write("pump_for_minlp.time_limit  60\n")
            f.write("pump_for_minlp.solution_limit  2\n")
            f.write("bonmin.time_limit {}\n".format(time_limit_sec))
            f.write("ipopt.linear_solver ma86\n")
            f.write("linear_solver ma86\n")

        # solver.options['linear_solver'] = 'ma86'  # option für ipopt ma86,ma97
        # solver.options['max_iter'] = 10000  # option für ipopt?
        # solver.options['bonmin.milp_strategy'] = 'find_good_sol'  # default: solve_to_optimality
        # solver.options['bonmin.algorithm'] = 'B-BB'  # default and recommended: B-BB. B-Hyb
        # solver.options['bonmin.solution_limit'] = 2
        # solver.options['bonmin.time_limit'] = time_limit_sec  # in sec
        # solver.options['bonmin.nlp_solver'] = 'Ipopt'  # default
        # solver.options['bonmin.iteration_limit'] = 2147483647
        self.opt_results = solver.solve(self.model, tee=tee)
        return self.opt_results

    def optimise_couenne(self):
        self.define_model()

        with pe.SolverFactory('couenne', executable='/home/markus/Couenne/build/bin/couenne') as solver:
            # solver.options['linear_solver'] = 'ma86'  # option für ipopt ma8,ma97
            solver.options.option_file_name = "couenne.opt"
            with open("couenne.opt", "w") as f:
                # f.write() # Here you can specify options for Couenne
                # f.write("problem_print_level 7\n")
                f.write("local_optimization_heuristic yes\n")
                f.write("time_limit 1200\n")
                f.write("bonmin.milp_strategy find_good_sol\n")
                f.write("bonmin.algorithm B-BB\n")
                f.write("bonmin.solution_limit  2\n")
                f.write("ipopt.linear_solver ma86\n")

            self.opt_results = solver.solve(self.model, tee=False)
            return self.opt_results

    def optimise_octeract(self, tee=False):
        self.define_model()
        os.environ["octeract_options"] = "num_cores=1"
        with pe.SolverFactory('octeract-engine',solver_io="nl",executable='/home/markus/octeract-engine-4.0.0/bin/octeract-engine') as solver:
            # solver.options['linear_solver'] = 'ma86'  # option für ipopt ma8,ma97
            # solver.options.option_file_name = "octeract.opt"
            with open("octeract.opt", "w") as f:
                # f.write() # Here you can specify options for Couenne
                # f.write("problem_print_level 7\n")
                # f.write("MILP_SOLVER=HIGHS\n")  # oder OSICBC
                f.write(
                    "CP_MAX_ITERATIONS=5\n")  # limit for the number of iterations performed by Constraint Propagation (CP), default 5
                f.write("FIRST_FEASIBLE_SOLUTION=false\n")
                f.write("MAX_SOLVER_TIME=360\n")  # in secs
                f.write("BRANCHING_STRATEGY = HYBRID_INTEGER_LEAST_REDUCED_AXIS\n")  # default:  BRANCHING_STRATEGY = MOST_VIOLATED_TERM
                # f.write("USE_MILP_RELAXATION = false\n")

            self.opt_results = solver.solve(self.model, tee=tee) # ,load_solutions=True,keepfiles=True)
            return self.opt_results



    def optimise_mindtpy(self, tee=False):
        self.define_model()
        solver = pe.SolverFactory('mindtpy')
        self.opt_results = solver.solve(self.model,
                                        strategy='OA',  # oder ECP oder GOA
                                        mip_solver='glpk',
                                        nlp_solver='ipopt',
                                        # mip_solver_args={'timelimit': 100},
                                        # nlp_solver_args={'timelimit': 100},
                                        tee=tee)
        return self.opt_results

    def draw_sketch(self, pixel_per_cm=0.5, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX, border=50):
        cv2.namedWindow('Floorplan', cv2.WINDOW_GUI_NORMAL)  # cv.WINDOW_AUTOSIZE, cv.WINDOW_NORMAL
        print('total m2 boundary: {}'.format(self.len * self.width * 1e-4))
        floor_imgs = []
        for floor in range(self.max_floor):
            img = np.ones((int(self.len * pixel_per_cm) + 2 * border, int(self.width * pixel_per_cm) + 2 * border, 3),
                          np.uint8)
            cv2.rectangle(img, (border, border), (img.shape[1] - border, img.shape[0] - border), color=(255, 255, 255))
            for i, room in enumerate(self.rooms):
                floor_idx = int(self.model.floor[i].value)
                if floor == floor_idx:
                    x, y, width, height = self.model.x[i].value, self.model.y[i].value, self.model.w[i].value, \
                                          self.model.h[i].value,
                    top_left = (int(x * pixel_per_cm) + border, int(y * pixel_per_cm) + border)
                    bottom_right = (int((x + width) * pixel_per_cm) + border, int((y + height) * pixel_per_cm) + border)
                    cv2.rectangle(img, top_left, bottom_right, color=room.color, thickness=-1)  # -1 means filled
                    room_area = round(height * width / 1e4, 1)
                    cv2.putText(img, '#{} {}: {}m2, Floor {}'.format(room.idx, room.name, room_area, floor),
                                (int((x + 0.5 * width) * pixel_per_cm) + border,
                                 int((y + 0.5 * height) * pixel_per_cm) + border),
                                fontFace=font,
                                fontScale=0.5, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)

                    print('#{} {}: {}m2, Floor {}'.format(room.idx, room.name, room_area, floor))
            floor_imgs.append(img)
        floorplan = np.concatenate(floor_imgs, axis=0)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite('Floorplan_{}.png'.format(timestr),floorplan)

        cv2.imshow('Floorplan',floorplan)
        cv2.waitKey()
