
from random import seed
from random import random

number_of_vars_per_room = 4


def base_index(room_idx):
    return room_idx * number_of_vars_per_room

def random_value(min=0.,max=1.):
    value = random()
    scaled_value = min + (value * (max - min))
    return scaled_value
