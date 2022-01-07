class Connection():

    def __init__(self):
        pass

    def define_constraint(self,model):
        pass

class Room2Building(Connection):

    def __init__(self, from_room):
        super().__init__()
        self.from_room = from_room

class OnBuildingPerimeter(Room2Building):
    pass


class Room2Room(Connection):

    def __init__(self, from_room, to_room):
        super().__init__()
        self.from_room = from_room
        self.to_room = to_room

class Adjacency(Room2Room):
    pass

    def define_constraint(self,model):
        i = self.from_room.idx
        j = self.to_room.idx
        touch_len = 100
        if i != j:
            return [[model.y[i] + model.h[i] <= model.y[j]],
                    [model.y[i] >= model.y[j] + model.h[j]],
                    [model.x[i] + model.w[i] <= model.x[j]],
                    [model.x[i] + model.w[i] <= model.x[j]],
                    [model.floor[i] >= model.floor[j] + 1],
                    [model.floor[j] >= model.floor[i] + 1]
                    ]
            model.adjacency_constraints.add((floor_idx, model.floor[room_idx], floor_idx))



class NonAdjacency(Room2Room):
    pass

class Proximity(Room2Room):
    pass
