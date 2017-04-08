import numpy as np
import re
import random


class ChunkMap:
    """
    Contains information on map of chunks, including chunk map, connection map, match_map, available surroundings
    """

    def __init__(self, width, height, chunk_size, chunk_dict):
        """
        creates chunk map and prepares it for building
        :param width: width in total tiles
        :param height: height in total tiles
        :param chunk_size: size of each chunk
        :param chunk_dict: dict of {num:Chunk}
        """
        self.width = width
        self.height = height
        self.chunk_size = chunk_size
        self.chunk_dict = chunk_dict
        self.chunk_map = None
        self.rotation_map = None
        # final output maps
        self.tile_map_walkable = np.zeros((self.height,self.width))
        self.tile_map_transparency = np.zeros((self.height,self.width))

        self.start_point = None
        self.next_available_points = []
        self.chunk_match_dict = {}

        # start the base map which will create the start point and available points
        self._build_map()
        self.create_search_dicts()

        # match string for any boundary or empty
        self.boundary_match = 'A'
        self.empty_space_match = '[A-Z]'

    def _build_map(self):
        """
        Creates chunk array for mapping

        :return: array of chunks to build, starting point to place first chunk
        """

        if (self.width % self.chunk_size != 0) or (self.height % self.chunk_size != 0):
            raise RuntimeError('chunk size will not work with map size')

        # build map of just chunks, world map can follow
        self.chunk_map = np.zeros((int(self.height / self.chunk_size), int(self.width / self.chunk_size)))
        # need array of rotation states in the map
        self.rotation_map = np.zeros((int(self.height / self.chunk_size), int(self.width / self.chunk_size)))

    def seed_map(self):
        """
        seed map with start point and connecting points
        :return: nothing
        """
        # set random start point for the chunks
        self.start_point = (
        round(np.random.triangular(0, self.height / self.chunk_size / 2, self.height / self.chunk_size)),
        round(np.random.triangular(0, self.width / self.chunk_size / 2, self.width / self.chunk_size)))

        # create seed chunk and seed rotation of chunk
        seed_chunk = random.choice(list(self.chunk_dict.keys()))
        seed_rotation = random.choice([0,1,2,3])

        # place seed chunk
        self.place_chunk(seed_chunk,self.start_point, seed_rotation)

        # self.next_available_points = self.get_surrounding(self.start_point)
        # self.next_available_points = self.remove_out_of_bounds()
        # self.next_available_points = self.remove_already_filled()

    def get_surrounding(self, point):
        """
        gets all surrounding locations to a tile
        :param point: (tuple) location to check around
        :return: list of points (tuples) surrounding point, in order

         0
        1#3
         2
        """
        out = []
        out.append((point[0] - 1, point[1]))
        out.append((point[0], point[1] - 1))
        out.append((point[0] + 1, point[1]))
        out.append((point[0], point[1] + 1))
        return out

    def constrain(self, value, vmin=0, vmax=0):
        """
        constrains value , returns flag if out of bounds and new value, exclusive of max
        :param value: value to constrain
        :param vmin: minimum allowed
        :param vmax: maximum allowed
        :return: out_of bounds, constrained value
        """
        if vmax != 0:
            vmax = self.height / self.chunk_size

        if value < vmin:
            return 'low', vmin

        elif value >= vmax:
            return 'high', vmax - 1

        else:
            return False, value

    def remove_out_of_bounds(self):
        """
        removes points in list that are below or above the bounds, this assumes square map
        :return:
        """
        vmin = 0
        # using height to set map scale
        vmax = self.height / self.chunk_size
        new_list = []
        for point in self.next_available_points:

            if (not self.constrain(point[0], vmin, vmax)[0]) and (not self.constrain(point[1], vmin, vmax)[0]):
                new_list.append(point)

        return new_list

    def remove_already_filled(self) -> list:
        """
        checks the array to see if a place is already filled (has a value other than zero
        :return: output point list
        """
        output = []
        for point in self.next_available_points:
            if self.chunk_map[point] == 0:
                output.append(point)

        return output

    def place_chunk(self, num, location, rotation):
        """
        place chunk in chunk array with number, location, and rotation stored
        :param num: chunk number
        :param location: tuple of location in chunk array
        :param rotation: rotation number of chunk in array
        :return: none, updates chunkmap
        """
        # add chunk to map
        self.chunk_map[location] = num
        self.rotation_map[location] = rotation

        self.next_available_points.extend(self.get_surrounding(location))
        self.next_available_points = self.remove_out_of_bounds()
        self.next_available_points = self.remove_already_filled()

    def pick_next_location(self):
        """
        randomly picks next location
        :return: point(tuple) fo next location
        """
        return random.choice(self.next_available_points)

    def get_match_string_for_location(self,location):
        """
        create string representing the possible matches for a location
        :param location: (tuple) representing point in space
        :return: string to match on for regex matching
        """

        chunks_around = self.get_surrounding(location)
        created_match = ''

        for i, point in enumerate(chunks_around):
            if (self.constrain(point[0], 0, self.height)[0]) or (self.constrain(point[1], 0, self.width)[0]):
                # if the point is off the match, use a default set for it's match string
                created_match += self.boundary_match
            else:
                # get chunk at location
                chunk_name = self.chunk_map[point]
                # check if chunk location is empty
                if chunk_name == 0:
                    # if the chunk is empty space
                    created_match += self.empty_space_match
                else:
                    # if the chunk is an actual chunk, not empty or boundary
                    chunk_here = self.chunk_dict[chunk_name]
                    # get rotation at location
                    rotation_of_chunk = self.rotation_map[point]
                    # get the match based on the side we are on, adding (or subtracting) 2 gets the opposite side of
                    # the chunk needed for this
                    match_string_needed = chunk_here.get_match_string(i - 2, rotation_of_chunk)
                    # add match to the total string
                    created_match += match_string_needed
        return created_match

    def match_to_list(self, match_wanted='[A-Z][A-Z][A-Z][A-Z]'):
        """
        Matches list in match wanted to a list of fields to match
        :param match_wanted: regex expression to search
        :param dicts_of_chunks: dictionaries of chunks
        :param search_order: order to search dict of chunks
        :return: dictionary key of match, internal dict of match
        """
        # if isinstance(search_order, list):
        #     raise RuntimeError('Search order not a list.')
        # iterate through search order

        # create search order here
        search_order = list(self.chunk_dict.keys())
        random.shuffle(search_order)

        # compile regular expression
        search_term = re.compile(match_wanted)

        for k in search_order:

            # search dicts of chunks in order
            rotations_shuffled = [0,1,2,3]
            random.shuffle(rotations_shuffled)

            for side in rotations_shuffled:
                if search_term.fullmatch(self.chunk_match_dict[k][side]) is not None:
                    return k, side

        # if none is found
        return None, None

    def create_search_dicts(self):
        """
        creates chunk dicts of chunks for match to list and search order
        :return: dicts {num:{rot:'str'}}
        """
        chunk_match_dict = {}
        for c in self.chunk_dict:
            chunk_match_dict[c] = self.chunk_dict[c].get_rotation_connections()

        self.chunk_match_dict = chunk_match_dict

    def place_tiles_from_chunk(self,location):
        # first get arrays needed
        chunk_id = self.chunk_map[location]
        chunk_rotation = self.rotation_map[location]
        chunk = self.chunk_dict[chunk_id]

        walk_array = chunk.get_rotated_walkable_array(chunk_rotation)
        transparent_array = chunk.get_rotated_transparent_array(chunk_rotation)

        y_start = location[0] * self.chunk_size
        x_start = location[1] * self.chunk_size

        y_end = y_start + self.chunk_size
        x_end = x_start + self.chunk_size

        self.tile_map_walkable[y_start:y_end, x_start:x_end] = walk_array
        self.tile_map_transparency[y_start:y_end, x_start:x_end] = transparent_array

    def place_tiles_from_chunk_map(self):
        """
        places all tiles from the chunk map
        :return: updates walk array and tile array with data from chunk array
        """
        # get all points to place tiles from
        locations = []
        for i in range(int(self.height / self.chunk_size)):
            for j in range(int(self.width / self.chunk_size)):
                locations.append((i,j))

        for location in locations:
            self.place_tiles_from_chunk(location)

    def print_walk_map(self):

        for i in range(int(self.height)):
            line = ''
            for j in range(int(self.width)):
                if self.tile_map_walkable[(i,j)] == 1:
                    line += '.'
                else:
                    line += '#'
            print(line)

    def generate(self,chunk_limit, fail_limit):
        """
        generate chunkmap
        :param chunk_limit: how many chunks to make into the map
        :return: updates chunk map as it works
        """
        self.seed_map()
        fail_count = 0
        for i in range(chunk_limit):
            # get the next point to update
            next_point = self.pick_next_location()

            # get the match string of the location of the next chunk
            match_string_of_next_point = self.get_match_string_for_location(next_point)

            # get new chunk number and rotation
            new_chunk_key, new_chunk_rotation = self.match_to_list(match_string_of_next_point)

            # check if no match was made
            if new_chunk_key is None:
                # if no match, then count up
                fail_count += 1

                # if failed too many times, quit generation
                if fail_count > fail_limit:
                    return
            else:
                # if no problem, then place tile
                self.place_chunk(new_chunk_key,next_point,new_chunk_rotation)




def test_chunk_map():
    x = ChunkMap(40,40,5,{1:[],2:[],3:[],4:[]})
    print(x.next_available_points)
    x.seed_map()
    print(x.chunk_map)
    print(x.next_available_points)


def build_chunks_test():
    out = {}
    out[0] = Chunk(np.zeros((5,5)),np.zeros((5,5)),['A','A','A','A'],['[A-Z]','[A-Z]','[A-Z]','[A-Z]'])
    out[1] = Chunk(np.ones((5,5)),np.ones((5,5)),['A','A','A','A'],['[AB]','[Q]','[AB]','[AB]'])
    out[2] = Chunk(np.ones((5,5)),np.ones((5,5)),['B','B','B','B'],['[AC]','[AC]','[AC]','[AC]'])
    out[3] = Chunk(np.zeros((5,5)),np.ones((5, 5)), ['C', 'Q', 'C', 'Q'], ['[AB]', '[AB]', '[AB]', '[AB]'])
    out[4] = Chunk(np.ones((5,5)),np.ones((5,5)),['C', 'C', 'C', 'C'],['[ABC]','[ABC]','[ABC]','[ABC]'])
    return out


def chunk_library():
    out = {}
    out[0] = Chunk(np.zeros((5, 5)), np.zeros((5, 5)), ['A', 'A', 'A', 'A'], ['A', 'A', 'A', 'A'])
    out[1] = Chunk(np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]), ["E", "A", "E", "A"], ["E", "A", "E", "A"])
    out[2] = Chunk(np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]), ["E", "A", "E", "E"], ["E", "A", "E", "E"])
    out[3] = Chunk(np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), ["E", "A", "E", "E"], ["E", "A", "E", "E"])
    out[4] = Chunk(np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), ["E", "A", "E", "O"], ["E", "A", "E", "O"])
    out[5] = Chunk(np.array([[0, 0, 1, 0, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), ["E", "A", "E", "O"], ["E", "A", "E", "O"])
    out[6] = Chunk(np.array([[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0]]), np.array([[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0]]), ["I", "A", "E", "A"], ["C", "A", "E", "A"])
    out[7] = Chunk(np.array([[0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 1, 1, 0], [0, 0, 1, 0, 0]]), np.array([[0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 1, 1, 0], [0, 0, 1, 0, 0]]), ["C", "A", "E", "A"], ["I", "A", "E", "A"])
    out[8] = Chunk(np.array([[0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), np.array([[0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), ["P", "A", "E", "e"], ["e", "A", "E", "P"])
    out[9] = Chunk(np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0]]), np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0]]), ["f", "P", "A", "e"], ["f", "e", "A", "P"])
    out[10] = Chunk(np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 1, 0, 0]]), ["f", "P", "E", "e"], ["f", "e", "E", "P"])
    out[11] = Chunk(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]), np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]), ["A", "E", "E", "A"], ["A", "E", "E", "A"])
    out[12] = Chunk(np.array([[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 1, 1], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]), np.array([[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 1, 1], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]), ["E", "A", "E", "E"], ["E", "A", "E", "E"])
    out[13] = Chunk(np.array([[0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["O", "A", "A", "E"], ["O", "A", "A", "E"])
    out[14] = Chunk(np.array([[0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["O", "E", "A", "A"], ["O", "E", "A", "A"])
    out[15] = Chunk(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["A", "E", "A", "E"], ["A", "E", "A", "E"])
    out[16] = Chunk(np.array([[0, 0, 0, 1, 0], [0, 0, 1, 1, 0], [1, 1, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 0, 0, 1, 0], [0, 0, 1, 1, 0], [1, 1, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["C", "E", "A", "A"], ["I", "E", "A", "A"])
    out[17] = Chunk(np.array([[0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["I", "A", "A", "E"], ["I", "A", "A", "E"])
    out[18] = Chunk(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), ["A", "A", "A", "A"], ["A", "A", "A", "A"])

    return out


def build_dungeon(width, height, chunk_size, fail_limit):
    cks = chunk_library()
    world = ChunkMap(width,height,chunk_size,cks)
    world.generate(int((width*height / chunk_size) * .8),fail_limit)
    world.place_tiles_from_chunk_map()
    world.print_walk_map()
    print(world.chunk_map)


class Chunk:
    """
    contains information on tiles structure
    both connections and match string start top first, then rotate counterclockwise

     0
    1#3
     2

    rotations will be handled as the number or rotations 90 degrees counter clockwise
    """

    def __init__(self,walk_array, transparent_array, connections, match_strings):

        # arrays that define walkability and transparency
        self.walk_array = np.array(walk_array)
        self.transparent_array = np.array(transparent_array)

        #check if connections will cause issues
        if len(connections) != 4:
            raise RuntimeError('Connections not a list of 4 characters')

        # create connections list
        # self.connections = []
        # for i in range(len(connections)):
        #     self.connections.append(connections[i:] + connections[:i])

        # set match string
        self.connections = connections
        self.match_strings = match_strings

    def get_connection(self, side, rotation):
        """
        get connection based on rotation and absolute side wanted
        :param side: side number , 0 based, counterclockwise from top
        :param rotation: rotation of 90 degrees, counterclockwise from top
        :return: connection based on side wanted and rotation handled
        """
        return self.connections[int((side - rotation) % 4)]

    def get_match_string(self, side, rotation):
        """
        get match string based on rotation and absolute side wanted
        :param side:
        :param rotation:
        :return:
        """
        return self.match_strings[int((side - rotation) % 4)]

    def get_rotation_connections(self):
        """
        gets a dictionary of side, and match string
        :return: dictionary of match strings, based on rotation
        """
        out = {}
        for rotation in range(4): # number of rotations is locked, due to 2d limitations
            #go through all sides, creating a full match string for each rotation, each match starting at the top
            out[rotation] = ''
            for side in range(4):
                out[rotation] +=(self.get_connection(side, rotation))

        return out



    # TODO make sure to add rotation commands for the numpy arrays

    def get_rotated_walkable_array(self,rotation):
        out = self.walk_array
        for i in range(int(rotation)):
            out = np.rot90(out)
        return out

    def get_rotated_transparent_array(self, rotation):
        out = self.transparent_array
        for i in range(int(rotation)):
            out = np.rot90(out)
        return out









