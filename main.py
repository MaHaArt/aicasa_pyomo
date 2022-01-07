
from objects import *
import logging
from pyomo.util.infeasible import log_infeasible_constraints

def do_test():
    building = Building(building_length_m=8,building_width_m=10,max_floor=2)


    hall = building.add_room(Hall(),floor=0)
    corridor= building.add_room(Corridor())

    # building.add_connection(Adjacency(from_room=hall,to_room=corridor))
    #
    kitchen =  building.add_room(Kitchen())
    living =  building.add_room(LivingRoom())
    living2 =  building.add_room(LivingRoom())
    building.add_connection(Adjacency(from_room=corridor,to_room=kitchen))
    # building.add_connection(Adjacency(from_room=corridor,to_room=living))

    # res = building.optimise(solver='glpk')
    res = building.optimise()

    building.draw_sketch()

if __name__ == '__main__':
    do_test()
