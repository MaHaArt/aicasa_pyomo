## unit for lean and area: 1 cm

import math
from objects.functions_scipy import *
from objects.helper import *
import cv2




class Room:
    _aspect_ratio = 1.6180339887
    min_area = 1 * 1e4
    max_area = 10 * 1e4
    _color = (212,255,127)
    _living_space = 0
    _min_len = 0.5 * 1e2

    def __init__(self, name=None):
        if name is None:
            self.name = '{}'.format(type(self).__name__)
        else:
            self.name = name
        self.idx = 0
        self.building = None


    @property
    def color(self):
        col = type(self)._color
        return col

    @property
    def aspect_ratio(self):
        myclass = type(self)
        return myclass._aspect_ratio

    @property
    def living_space(self):
        myclass = type(self)
        return float(myclass._living_space)

    @property
    def min_len(self):
        myclass = type(self)
        return myclass._min_len



class Hall(Room):
    min_area = 1 * 1e4  # 5m2
    max_area= 20 * 1e4 # 10m2
    color = (238,238,224)
    _min_len = 2 * 1e2

    def __init__(self):
        super().__init__()


class Corridor(Room):
    _aspect_ratio = 0.
    min_area = 2 * 1e4  # 4m2
    max_area = 10 * 1e4  # 10m2
    color = (176, 192, 205)
    _min_len = 2 * 1e2

    def __init__(self):
        super().__init__()


class Kitchen(Room):
    min_area = 3 * 1e4  # 10m2
    max_area = 30 * 1e4  # 15m2
    color = (87, 207, 87)
    _living_space = 1
    _min_len = 1.5 * 1e2

    def __init__(self):
        super().__init__()


class LivingRoom(Room):
    min_area = 5 * 1e4  # 15m2
    max_area = 100 * 1e4  # 30m2
    color = (51, 51, 205)
    _living_space = 1
    _min_len = 1.5 * 1e2

    def __init__(self):
        super().__init__()


class WC(Room):
    _aspect_ratio = 0.
    min_area = 1.5 * 1e4  # 3m2
    max_area = 5 * 1e4  # 5m2
    upper_bound_len = 2 * 1e2
    color = (204, 255, 204)
    _min_len = .5 * 1e2

    def __init__(self):
        super().__init__()


class Bathroom(Room):
    _aspect_ratio = 0.
    min_area = 2 * 1e4  # 8m2
    max_area = 20 * 1e4  # 10m2
    color = (255, 204, 204)
    _min_len = .5 * 1e2

    def __init__(self):
        super().__init__()


class DiningRoom(Room):
    min_area = 5 * 1e4  # 12m2
    max_area = 25 * 1e4  # 18m2
    color = (255, 153, 204)
    _living_space = 1
    _min_len = 2.5 * 1e2

    def __init__(self):
        super().__init__()


class Pantry(Room):
    """Speisekammer
    """

    def __init__(self):
        super().__init__()


class DoubleBedroom(Room):
    min_area = 12 * 1e4
    max_area = 18 * 1e4
    _living_space = 1
    _min_len = 2.5 * 1e2

    def __init__(self):
        super().__init__()


class SingleBedroom(Room):
    min_area = 12 * 1e4  # 10m2
    max_area = 15 * 1e4
    _living_space = 1
    _min_len = 2.5 * 1e2

    def __init__(self):
        super().__init__()


class DoubleGarage(Room):

    def __init__(self):
        super().__init__()


class SingleGarage(Room):
    min_area = 18 * 1e4  # 10m2

    def __init__(self):
        super().__init__()


class Staircase(Room):
    min_area = 5 * 1e4

    def __init__(self):
        super().__init__()
