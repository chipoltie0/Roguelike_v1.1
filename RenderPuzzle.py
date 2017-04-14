import tdl
import PuzzleGenerator as pg

COLOR_BLACK = (0,0,0)
COLOR_WHITE = (255,255,255)
COLOR_DICT = {0:COLOR_BLACK,1:COLOR_WHITE}
WIDTH = 50
HEIGHT = 50


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

    while not tdl.event.is_window_closed():
        world = pg.ChunkMap(WIDTH,HEIGHT,5,cks)
        world.generate(50,200)
        world.place_tiles_from_chunk_map()

        for i in range(HEIGHT):
            for j in range(WIDTH):
                next_console.draw_char(j,i,' ',bg=COLOR_DICT[world.tile_map_walkable[(i,j)]])

        console.blit(next_console,width=WIDTH,height=HEIGHT)

        tdl.flush()

        event = tdl.event.key_wait()

        if event:
            # print(event)
            if event.type == 'QUIT':
                raise SystemExit()
