
# import tdl map so that an inherited map class can be made, tdl map already has fov and path calcuations methods
# inside it

from tdl.map import Map
# import.map numpy, which will be used for the block map
import numpy as np


class DungeonMap(Map):
    """
    DungeonMap object will extend tdl.map adding functions for pieces and adding maps together
    """

    def __init__(self, width, height):
        # super original function, passing width and height
        super().__init__(width, height)
        # create dictionary that will hold pieces
        self.pieces = {}
        # create next id for pieces, will iterate every time a piece is added
        self.next_id = 0

        # set for explored tiles, will contain tuple sets for coordinates that the player has seen / can see
        self.explored = np.zeros((height, width))
        # get type array for map additions, 1 means true, can override, 0 is false, cannot override

        self.override_array = np.ones((height, width))

    def add_piece(self,piece):
        """

        :param piece: Piece object that will be linked in pieces dictionary
        :return: nothing returned, simply adds pieces
        """
        # only add piece if location is possible
        if self.can_move_here(piece.location_y,piece.location_x) is None:
            # add piece to dictionary
            self.pieces[self.next_id] = piece

            # increment id for next piece to be put in
            self.next_id += 1
        else:
            raise Exception('Piece collided as it was placed at {} {}'.format(piece.location_y,piece.location_x))

    def load_from_generator(self, walk_array, transparency_array, override_array ):
        """
        does nothing right now, but will take data from a generator and set up a map
        :param walk_array: 2d array of walkability
        :param transparency_array: 2d array of transparency
        :return: nothing returned
        """
        # check that lengths match
        if len(walk_array[0]) == self.width and len(walk_array) == self.height:
            # load array into walkable array
            for y_val in range(self.height):
                for x_val in range(self.width):
                    self.walkable[y_val, x_val] = walk_array[y_val][x_val]
        else:
            raise Exception('walk array did not match lengths')

        # check that lengths match
        if len(transparency_array[0]) == self.width and len(transparency_array) == self.height:
            # load array into transparent array
            for y_val in range(self.height):
                for x_val in range(self.width):
                    self.transparent[y_val, x_val] = transparency_array[y_val][x_val]
        else:
            raise Exception('transparency array did not match lengths')

    def can_move_here(self, x, y):
        """
        check if there is a tile or piece blocking the way
        :param x: position to check
        :param y: position to check
        :return: 'wall' if tile blocks the way, piece id if piece blocks the way
        """
        if not self.walkable[y, x]:
            return 'tile'
        else:
            for p_id in self.pieces.keys():
                # check if the pieces location matches y,x location
                if self.pieces[p_id].location_y == y and self.pieces[p_id].location_x == x:
                    return p_id

        # if nothing returned, means area is clear to move
        return None

    def can_override(self, x, y):
        """
        can the current position be overriden by another map piece or edge of the map
        :param x: x value
        :param y: y value
        :return: True false
        """
        if self.override_array[y, x] == 1:
            return True
        else:
            return False

    def append(self,other_map, x, y ):
        """
        adds new map to this map
        :param other_map: other dungeonmap object
        :param x: x position to start at on current map
        :param y: y position to start at on current map
        :return: True if append occurred, false if append failed

        """
        # first check if maps can overlap
        # create iterator of points to check if maps can be added

        points = ((i, j) for j in range(other_map.height) for i in range(other_map.width))

        # iterate through points, adding override values from both other_map and self, if greater than one, two
        # overrides overlap and addition cannot be done

        for point in points:
            # fix points j i to point[0] and point[1]
            if other_map.override_array[j, i] + self.override_array[ j + y, i + x] > 1:
                return False





class Piece:
    """
    This class contains all the information that a basic piece requires on the board
    """
    def __init__(self,
                 character,
                 name,
                 location_y,
                 location_x,
                 parent_map,
                 fg_color,
                 bg_color=Ellipsis,
                 walkable=False,
                 transparent=True):

        # ascii char for piece
        self.character = character
        # name for piece if it is referenced
        self.name = name
        # location of piece in y, x coords
        self.location_y = location_y
        self.location_x = location_x
        # color data of piece
        self.fg_color = fg_color
        self.bg_color = bg_color
        # can the piece be collided with?
        self.walkable = walkable
        # can the piece be seen through?
        self.transparent = transparent
        # parent map
        self.parent_map = parent_map
        # storage of tile under piece
        self.tile_under_walkable = True
        self.tile_under_transparent = True

    def move(self, new_y, new_x):
        if self.parent_map.can_move_here(new_y, new_x) is None:
            # reset values underneath piece when it moves
            self.parent_map.walkable[self.location_y, self.location_x] = self.tile_under_walkable
            self.parent_map.transparent[self.location_y, self.location_x] = self.tile_under_transparent
            # move piece to new location
            self.location_y = new_y
            self.location_x = new_x
            # get tile information to save for later
            self.tile_under_walkable = self.parent_map.walkable[self.location_y, self.location_x]
            self.tile_under_transparent = self.parent_map.transparent[self.location_y, self.location_x]
            # update map walkability and transparency so pathfinding can work later
            self.parent_map.walkable[self.location_y, self.location_x] = self.walkable
            self.parent_map.transparent[self.location_y, self.location_x] = self.transparent


if __name__ == '__main__':
    print('started')
    m = DungeonMap(10, 10)
    p = Piece('@', name='player', location_y=1, location_x=1, parent_map=m, fg_color=(0, 0, 0))
    print('dungeon and piece made')
    for i in range(10):
        for j in range(10):
            m.walkable[i, j] = True
    print('2,2 is transparent = {}'.format(m.transparent[2,2]))
    m.add_piece(p)
    print('piece added at {} {}'.format(p.location_y,p.location_x))
    path = m.compute_path(p.location_x, p.location_y, 9, 9)
    print(list(path))
    for point in path:
        p.move(point[0],point[1])
        print('piece moved to {} {} and walkable = {} transparent = {}'.format(point[0],point[1], m.walkable[point[0], point[1]],m.transparent[point[0], point[1]] ))

    print('piece is now at {} {}'.format(p.location_y,p.location_x))
    print('previous location 2,2 is walkable = {} and transparent = {}'.format(m.walkable[2,2], m.transparent[2,2]))



