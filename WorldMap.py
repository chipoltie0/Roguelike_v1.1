from tdl.map import Map
import numpy as np
import random

class WorldMap:

    def __init__(self,width, height):
        self.tdl_map = Map(width, height)
        self.explored = set()  # list of all points that the player has seen
        self.up_stairs = None
        self.down_stairs = None

    def load_walk_map(self, walk_map):
        """
        loads walk map from a generator into the tdl map
        :param walk_map: numpy array of values
        :return: none, updates self.tdl_map
        """
        # get shape of walk_map
        height, width = np.shape(walk_map)

        for i in range(height):
            for j in range(width):
                self.tdl_map.walkable[i,j] = bool(walk_map[(i,j)])

    def load_transparent_map(self, transparent_map):
        """
        loads transparency map from a generator into the tdl map
        :param transparent_map: numpy array of values
        :return: none, updates self.tdl_map
        """
        # get shape of walk_map
        height, width = np.shape(transparent_map)

        for i in range(height):
            for j in range(width):
                self.tdl_map.transparent[i,j] = bool(transparent_map[(i,j)])

    def get_view(self,point, radius):
        """
        gets a list of all points that can be seen from this location on the world map
        :param point: point to start search
        :return: iterable of points that can be seen
        """
        viewable = list(self.tdl_map.compute_fov(point[0],point[1],radius=radius,light_walls=False,fov='DIAMOND'))
        # print(viewable)
        return viewable

    def get_path(self,start_point,end_point):
        """
        calculate path from start point to end point
        :param start_point: (x,y)
        :param end_point: (x,y)
        :return: list of tuples of shortest path
        """
        return self.tdl_map.compute_path(start_point[0],start_point[1],end_point[0],end_point[1])

    def has_been_explored(self,point):
        """
        check if point has been explored
        :param point: tuple (x,y)
        :return: True or false
        """
        return point in self.explored

    def add_to_explored(self,points):
        """
        adds list of points to self.explored list
        :param points: list of tuples to append to explored
        :return: none, updates self.explored
        """
        for point in points:
            self.explored.add(point)

    def collides_with_map(self,point):
        """
        checks if a collision will happen at a specific point
        :param point: (x,y) tuple that can be checked for collsion
        :return: True or false
        """

        return not self.tdl_map.walkable[point[0],point[1]]

    def get_available_walk_spaces(self):
        """
        returns list of all points available to put something walkable (pieces)
        :return: list of tuples
        """
        out = []
        for i in range(self.tdl_map.height):
            for j in range(self.tdl_map.width):
                if self.tdl_map.walkable[i,j]:
                    out.append((i,j))
        return out

    def set_stairs(self,place_down=True,retries=5):
        """
        place up and down stairs
        :param place_down: places stairs further down, false for final level
        :return: none, updates self.stair positions
        """
        # loop to make sure it is possible to reach the end
        locations = self.get_available_walk_spaces()
        complete = False
        while not complete:
            # place start randomly
            self.up_stairs = random.choice(locations)
            del locations[locations.index(self.up_stairs)]
            pathable = False
            iterations = 0
            if place_down:
                while (not pathable) and (iterations < retries) :
                    self.down_stairs = random.choice(locations)
                    del locations[locations.index(self.down_stairs)]
                    # check if possible to reach
                    if self.get_path(self.up_stairs,self.down_stairs):
                        pathable = True
            else:
                pathable = True

            if pathable:
                complete = True






