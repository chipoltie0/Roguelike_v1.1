import tdl
import WorldMap as wm
import PuzzleGenerator as pg
import GamePiece as gp
import KeyboardInput as ki
import GameInventory as gi
import random

WIDTH = 50
HEIGHT = 50

def test_engine():
    """run test of world generation and placing a piece"""
    cks = pg.chunk_library()
    chunk_map = pg.ChunkMap(50,50,5,cks)
    chunk_map.generate(80,80)
    chunk_map.place_tiles_from_chunk_map()

    dungeon = wm.WorldMap(50,50)
    dungeon.load_transparent_map(chunk_map.tile_map_transparency)
    dungeon.load_walk_map(chunk_map.tile_map_walkable)

    points_available = dungeon.get_available_walk_spaces()
    print(points_available)
    start_point = random.choice(points_available)

    player = gp.Piece(dungeon,start_point=start_point, char='@')
    print('Player placed at {}'.format(start_point))
    player.move_piece_to()


def create_consoles():
    # create console
    console = tdl.init(WIDTH, HEIGHT, title='Room View')

    # create next console in cycle
    next_console = tdl.Console(WIDTH, HEIGHT)
    #comment is comment

    return console, next_console


if __name__ == '__main__':
    console, next_console = create_consoles()

    cks = pg.chunk_library()
    levels = {}

    for i in range(20):
        world = pg.ChunkMap(WIDTH, HEIGHT, 5, cks)
        world.generate(50, 200)
        world.place_tiles_from_chunk_map()

        dungeon = wm.WorldMap(50, 50)
        dungeon.load_transparent_map(world.tile_map_transparency)
        dungeon.load_walk_map(world.tile_map_walkable)

        if i == (20-1):
            dungeon.set_stairs(False)
        else:
            dungeon.set_stairs()

        # add pieces to dungeon
        points_to_place = dungeon.get_available_walk_spaces()
        for x in range(int(random.triangular(0,7,3))):
            loc = random.choice(points_to_place)
            inv = [gi.Item('gold','gold',int(random.triangular(1,100,20)))]
            p = gi.Pile(dungeon,loc,color=(200,200,0), char='*',inventory=inv)
            dungeon.add_piece(p)


        # add level to dungeon whole
        levels[i]= dungeon
    player_level = 0

    points_available = levels[player_level].get_available_walk_spaces()
    player_start = levels[player_level].up_stairs
    player = gp.Piece(levels[player_level],player_start,color=(0,0,0),char='@')
    player_inventory = gi.Inventory()

    while not tdl.event.is_window_closed():

        # get all explored tiles
        view = levels[player_level].get_view(player.location,5)
        levels[player_level].add_to_explored(view)

        for i in range(HEIGHT):
            for j in range(WIDTH):
                next_console.draw_char(i,j,' ',bg=(0,0,0))

        for tile in levels[player_level].explored:
            next_console.draw_char(tile[0],tile[1],' ',bg=(40,40,40))

        for tile in view:
            next_console.draw_char(tile[0], tile[1], ' ', bg=(100, 100, 100))
            
        # render stairs
        if levels[player_level].up_stairs in view:
            next_console.draw_char(levels[player_level].up_stairs[0],levels[player_level].up_stairs[1],
                                   char='^',fg=(255,255,255),bg=(100,100,100))
        elif levels[player_level].up_stairs in levels[player_level].explored:
            next_console.draw_char(levels[player_level].up_stairs[0], levels[player_level].up_stairs[1],
                                   char='^', fg=(100, 100, 100), bg=(40, 40, 40))
        else:
            pass
        # check if down stair is available
        if levels[player_level].down_stairs:
            if levels[player_level].down_stairs in view:
                next_console.draw_char(levels[player_level].down_stairs[0],levels[player_level].down_stairs[1],
                                       char='v',fg=(255,255,255),bg=(100,100,100))
            elif levels[player_level].down_stairs in levels[player_level].explored:
                next_console.draw_char(levels[player_level].down_stairs[0], levels[player_level].down_stairs[1],
                                       char='v', fg=(100, 100, 100), bg=(40, 40, 40))
            else:
                pass

        # draw pieces
        for piece in levels[player_level].pieces:
            if piece.location in view:
                next_console.draw_char(piece.location[0],piece.location[1],char=piece.char,fg=piece.color,bg=(100,100,100))

        # draw player
        next_console.draw_char(player.location[0],player.location[1],player.char,
                               fg=(255,255,0),bg=(100,100,100))

        console.blit(next_console)
        tdl.flush()
        # wait for next event
        event = tdl.event.key_wait()
        if event.type == 'QUIT':
            raise SystemExit
        action = ki.get_action(event)
        player_x = player.location[0]
        player_y = player.location[1]
        if action == 'up':
            if not levels[player_level].collides_with_map((player_x,player_y-1)):
                player.move_piece_to((player_x,player_y-1))
        elif action == 'left':
            if not levels[player_level].collides_with_map((player_x-1,player_y)):
                player.move_piece_to((player_x-1,player_y))
        elif action == 'right':
            if not levels[player_level].collides_with_map((player_x+1,player_y)):
                player.move_piece_to((player_x+1,player_y))
        elif action == 'down':
            if not levels[player_level].collides_with_map((player_x,player_y+1)):
                player.move_piece_to((player_x,player_y+1))
        elif action == 'accept':
            if player.location == levels[player_level].up_stairs:
                player_level -= 1
                player.move_piece_to(levels[player_level].down_stairs)
            elif player.location == levels[player_level].down_stairs:
                player_level += 1
                player.move_piece_to(levels[player_level].up_stairs)
            else:
                pass
        elif action == 'pickup':
            loc = player.location

            for pile in levels[player_level].pieces:
                if loc == pile.location:
                    if hasattr(pile,'inventory'):
                        player_inventory.add_item(pile.inventory.inventory)
                        levels[player_level].pieces.remove(pile)
                        print(player_inventory.inventory[0].amount)


        else:
            pass





