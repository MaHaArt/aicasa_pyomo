from objects import *
import logging
from pyomo.util.infeasible import log_infeasible_constraints
from pyomo.opt import SolverStatus, TerminationCondition


def do_test():
    building = Building(building_length_m=8, building_width_m=10, max_floor=2)

    hall = building.add_room(Hall(), floor=0)
    corridor1 = building.add_room(Corridor())
    corridor2 = building.add_room(Corridor(), floor=1)

    # building.add_connection(Adjacency(from_room=hall,to_room=corridor))
    #
    kitchen = building.add_room(Kitchen())
    living = building.add_room(LivingRoom())
    living2 = building.add_room(LivingRoom())
    dining = building.add_room(DiningRoom())
    # bath = building.add_room(Bathroom())
    # wc = building.add_room(WC())
    building.add_connection(Adjacency(from_room=corridor1, to_room=hall))
    building.add_connection(Adjacency(from_room=corridor1, to_room=dining))
    building.add_connection(Adjacency(from_room=dining, to_room=kitchen))
    building.add_connection(Adjacency(from_room=corridor1, to_room=living))
    building.add_connection(Adjacency(from_room=corridor2, to_room=living2))


    # results = building.optimise_mindtpy(tee=True)
    results = building.optimise_bonmin(tee=False)
    # results = building.optimise_couenne()

    if (
            results.solver.status == SolverStatus.ok):  # and ( results.solver.termination_condition == TerminationCondition.optimal):
        # Do something when the solution in optimal and feasible
        building.draw_sketch()

    elif (results.solver.termination_condition == TerminationCondition.infeasible):
        # Do something when model in infeasible
        print('Infeasible')
        logging.basicConfig(filename='/home/markus/ART-ificial/SynologyDrive/projekte/pyomo_disjunct/floorplan.log',
                            level=logging.INFO)
        root_logger = logging.getLogger('')
        log_infeasible_constraints(building.model, log_expression=True, log_variables=True, logger=root_logger)

    # elif (results.solver.status == SolverStatus.warning):
    #     building.draw_sketch()
    else:
        # Something else is wrong
        print('Solver Status: {}'.format(results.solver.status))





if __name__ == '__main__':
    do_test()
