import numpy as np
import re



def match_to_list(match_wanted='[A-Z][A-Z][A-Z][A-Z]', dicts_of_chunks=None, search_order = None):
    """
    Matches list in match wanted to a list of fields to match
    :param match_wanted: regex expression to search
    :param dicts_of_chunks: dictionaries of chunks
    :param search_order: order to search dict of chunks
    :return: dictionary key of match, internal dict of match
    """
    if isinstance(search_order,list):
        raise RuntimeError('Search order not a list.')
    # iterate through search order

    # compile regular expression
    search_term = re.compile(match_wanted)

    for k in search_order:

        #search dicts of chunks in order
        for key, rotation in dicts_of_chunks[k].items():
            if search_term.fullmatch(rotation) is not None:
                return k, rotation


    #if none is found
    return None, None

class Chunk:
    """
    contains information on tiles structure
    """
    def __init__(self, walk_array, transparent_array, connections, match_string):
        self.walk_array = np.array(walk_array)
        self.transparent_array = np.array(transparent_array)
        if not isinstance(connections,str) or len(connections) != 4:
            raise RuntimeError('Connections not a list of 4 characters')

        # create connections list
        self.connections = []
        for i in range(len(connections)):
            self.connections.append(connections[i:] + connections[:i])

        # set match string


