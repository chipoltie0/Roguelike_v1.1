DEFAULT_KEYBINDS = {
    'KP1':'down_left',
    'KP2':'down',
    'KP3':'down_right',
    'KP4':'left',
    'KP5':'none',
    'KP6':'right',
    'KP7':'up_left',
    'KP8':'up',
    'KP9':'up_right',
    'ENTER':'accept',
    'ESCAPE':'menu',
    'TAB':'inventory',
    'w':'up',
    'a':'left',
    's':'down',
    'd':'right',
    'RIGHT':'right',
    'UP':'up',
    'LEFT':'left',
    'DOWN':'down',
    'p':'pickup'}


def get_action(event,binding=DEFAULT_KEYBINDS):
    """
    interprets keyboard input to a specific action
    :param: event from tdl.event
    :return: key specifically pressed
    """
    key = event.key  # get the character pressed
    keychar = event.keychar
    if key == 'CHAR':
        key = keychar

    if key not in binding:
        return 'none'
    return binding[key]


