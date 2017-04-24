
class Piece:
    """
    This is the base object that interacts with the map object, contains information such as
    the location of the object, what map it is on, and possible a connected character sheet
    """
    def __init__(self,map, start_point, collision=False,color=(0,0,0),char='*'):

        self.map = map  # store the map this piece is on
        self.location = start_point  # store location of the piece
        self.collision = collision
        self.color = color
        self.char = char

    def move_piece_to(self,point,map=None):
        """
        moves a piece to a new location
        :param point: point to change the piece's location
        :param map: map to move the piece to, if None, then same map currently on
        :return: nothing, updates self.location
        """
        if map is not None:
            self.map = map

        self.location = point


class Stair(Piece):
    """
    This is a special case of piece that can change the player's level
    """
    def __init__(self,map, point, color,end_floor, char = '/'):
        super().__init__(map,point,color,char=char)
        self.end_floor = end_floor

    def interact(self, piece: Piece):
        """
        when a piece interacts with the stairs, it changes the pieces map value
        :param piece: piece that interacted
        :return: nothing, edits piece
        """
        piece.map = self.end_floor
