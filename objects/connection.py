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

    def __init__(self, from_room, to_room,touch_len=10):
        super().__init__(from_room=from_room, to_room=to_room)
        self.touch_len= touch_len




class NonAdjacency(Room2Room):
    pass

class Proximity(Room2Room):
    pass
