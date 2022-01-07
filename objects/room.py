## unit for lean and area: 1 cm

import math
from objects.functions_scipy import *
from objects.helper import *
import cv2



class Room:
    aspect_ratio = 1.6180339887
    upper_bound_len = 10 * 1e2
    lower_bound_len = 1 * 1e2
    min_area = 1 * 1e4
    max_area = 10 * 1e4
    color = (212,255,127)

    def __init__(self, name=None):
        if name is None:
            self.name = '{}'.format(type(self).__name__)
        else:
            self.name = name
        self.idx = 0
        self.building = None


    @property
    def color(self):
        col = type(self).color
        return col



class Hall(Room):
    min_area = 5 * 1e4  # 5m2
    max_area= 10 * 1e4 # 10m2
    color = (238,238,224)

    def __init__(self):
        super().__init__()


class Corridor(Room):
    min_area = 4 * 1e4  # 4m2
    max_area = 10 * 1e4  # 10m2
    color = (176, 192, 205)

    def __init__(self):
        super().__init__()


class Kitchen(Room):
    min_area = 10 * 1e4  # 10m2
    max_area = 15 * 1e4  # 15m2
    color = (87, 207, 87)

    def __init__(self):
        super().__init__()


class LivingRoom(Room):
    min_area = 15 * 1e4  # 15m2
    max_area = 30 * 1e4  # 30m2
    color = (51, 51, 205)

    def __init__(self):
        super().__init__()


class WC(Room):
    min_area = 3 * 1e4  # 3m2
    max_area = 5 * 1e4  # 5m2
    upper_bound_len = 2 * 1e2

    def __init__(self):
        super().__init__()


class Bathroom(Room):
    min_area = 8 * 1e4  # 8m2
    max_area = 10 * 1e4  # 10m2

    def __init__(self):
        super().__init__()


class DiningRoom(Room):
    min_area = 12 * 1e4  # 12m2
    max_area = 18 * 1e4  # 18m2

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

    def __init__(self):
        super().__init__()


class SingleBedroom(Room):
    min_area = 12 * 1e4  # 10m2
    max_area = 15 * 1e4

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
