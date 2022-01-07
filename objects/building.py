import numpy as np
import cv2
from objects.room import Room
from random import seed
from random import random
from objects.helper import *
from objects.model_functions import *
import pyomo.environ as pe
import logging
from pyomo.util.infeasible import log_infeasible_constraints
from objects.building_constraints import *
from objects.connection import Adjacency


class Building:
    def __init__(self, building_width_m=10, building_length_m=25, max_floor=1):
        self.rooms = []
        self.connections = []
        self.len = building_length_m * 1e2
        self.width = building_width_m * 1e2
        self.model = None
        self.opt_result = None
        self.max_floor = max_floor
        self.floor_constraints = []

    def add_room(self, room, floor=None):
        idx = self.nr_of_rooms
        room.idx = idx
        room.building = self
        self.rooms.append(room)
        if floor is not None:
            c = FloorConstraint(room, floor)
            self.floor_constraints.append(c)

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

    def optimise(self):
        self.model = pe.ConcreteModel(name='floorplan')
        define_vars_for_model(self)
        define_Constraints_no_intersection(self)
        define_Constrains_in_boundary(self)
        define_Constraints_min_area(self)
        define_Constraints_max_area(self)
        # define_Constraints_ratio(self)
        define_floor_constraints(self)
        define_Objective(self)

        # pe.TransformationFactory('gdp.bigm').apply_to(self.model)  #'gdp.bigm' , 'gdp.hull'
        pe.TransformationFactory('gdp.bigm').apply_to(self.model)
        # opt = pe.SolverFactory('gdpopt')  #' gplk
        # opt.options['ma27_pivtol'] = 1e-4
        opt = pe.SolverFactory('mindtpy')
        self.opt_result = opt.solve(self.model, mip_solver='glpk', nlp_solver='ipopt')
        # opt = pe.SolverFactory('glpk')
        # self.opt_result = opt.solve(self.model, tee=True) # ,strategy='LOA')  # LOA, GLOA, LBB, RIC
        # self.model.pprint()
        # self.model.display()
        log_infeasible_constraints(self.model, log_expression=False, log_variables=False)
        logging.basicConfig(filename='/home/markus/infeasible_constraints_floorplan.log', level=logging.INFO)

    def draw_sketch(self, pixel_per_cm=0.5, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX, border=50):
        cv2.namedWindow('Floorplan', cv2.WINDOW_AUTOSIZE)  # cv.WINDOW_AUTOSIZE, cv.WINDOW_NORMAL
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
                    cv2.rectangle(img, top_left, bottom_right, color=room.color, thickness=1)  # -1 means filled
                    room_area = round(height * width / 1e4, 1)
                    cv2.putText(img, '#{} {}: {}m2, Floor {}'.format(room.idx, room.name, room_area, floor),
                                (int((x + 0.5 * width) * pixel_per_cm) + border,
                                 int((y + 0.5 * height) * pixel_per_cm) + border),
                                fontFace=font,
                                fontScale=0.5, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)

                    print('#{} {}: {}m2, Floor {}'.format(room.idx, room.name, room_area, floor))
            floor_imgs.append(img)
        floorplan = np.concatenate(floor_imgs, axis=0)
        cv2.imshow('Floorplan', floorplan)
        cv2.waitKey()
