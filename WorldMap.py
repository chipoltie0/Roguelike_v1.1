from tdl.map import Map
import numpy as np


class WorldMap:

    def __init__(self,width,height):
        self.tdl_map = Map(width,height)
        self.explored = []  # list of all points that the player has seen

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
        return self.tdl_map.compute_fov(point[0],point[1],radius=radius,light_walls=False)

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
        self.explored.extend(points)
