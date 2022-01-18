from objects import *
import logging
from pyomo.util.infeasible import log_infeasible_constraints
from pyomo.opt import SolverStatus, TerminationCondition


def do_test():
    building = Building(building_length_m=20, building_width_m=15, max_floor=2)

    hall = building.add_room(Hall(), floor=0)
    corridor1 = building.add_room(Corridor())
    corridor2 = building.add_room(Corridor(), floor=1)

    #
    kitchen = building.add_room(Kitchen())
    living = building.add_room(LivingRoom())
    living2 = building.add_room(LivingRoom())
    dining = building.add_room(DiningRoom())
    bath = building.add_room(Bathroom())
    wc = building.add_room(WC())
    building.add_connection(Adjacency(from_room=corridor1, to_room=hall))
    building.add_connection(Adjacency(from_room=corridor1, to_room=dining))
    building.add_connection(Adjacency(from_room=dining, to_room=kitchen))
    building.add_connection(Adjacency(from_room=corridor1, to_room=living))
    building.add_connection(Adjacency(from_room=corridor2, to_room=living2))

    min_area_target, max_area_target, area_available = building.area_bounds()
    print('min_area_target: {0:.1f}m2, max_area_target: {1:.1f}m2, area_available: {2:.1f}m2'.format(min_area_target/1e4, max_area_target/1e4, area_available/1e4))

    # results = building.optimise_mindtpy(tee=True)
    results = building.optimise_bonmin(tee=True,time_limit_sec=12000)
    # results = building.optimise_octeract(tee=True,time_limit_sec=100)
    #results = building.optimise_couenne(tee=True,time_limit_sec=420)
    if (
            results.solver.status == SolverStatus.ok):  # and ( results.solver.termination_condition == TerminationCondition.optimal):
        # Do something when the solution in optimal and feasible
        building.draw_sketch()
    elif (results.solver.status == SolverStatus.warning):
        building.draw_sketch()
    elif (results.solver.termination_condition == TerminationCondition.infeasible):
        # Do something when model in infeasible
        print('Infeasible')
        logging.basicConfig(filename='/home/markus/ART-ificial/SynologyDrive/projekte/aicasa_pyomo/floorplan.log',
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
