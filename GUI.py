"""
For creating the GUI view.
"""

import sys
import Json
import pygame as p
import pygame_widgets as pw

json_data = Json.read_from_json()  # global parameter that contains values from settings.json JSON file.


def main_menu(screen):
    """
    Method for creating main menu GUI window.
    :param screen:
    :return:
    """
    name, board_width, board_height, settings = Json.get_json_data(json_data)
    button_names = json_data['MAIN_MENU']

    new_game = draw_button(screen, board_width, board_height // 2 - 50, button_names['NEW_GAME'])
    volume = draw_button(screen, board_width, board_height // 2, button_names['SOUND'])
    exit_game = draw_button(screen, board_width, board_height // 2 + 75, button_names['EXIT'])

    new_game.onRelease = lambda: new_game_menu(screen)
    volume.onRelease = lambda: sound_menu(screen)
    exit_game.onRelease = lambda: sys.exit()

    buttons = []
    buttons.extend([new_game, volume, exit_game])
    draw_state(screen, name, buttons)


def new_game_menu(screen):
    """
    Method for creating new game menu GUI window.
    :param screen:
    :return:
    """
    name, board_width, board_height, settings = Json.get_json_data(json_data)
    button_names = json_data['NEW_GAME_MENU']

    easy = draw_button(screen, board_width, board_height // 2 - 75, button_names['EASY'])
    medium = draw_button(screen, board_width, board_height // 2 - 35, button_names['MEDIUM'])
    hard = draw_button(screen, board_width, board_height // 2 + 5, button_names['HARD'])
    back = draw_button(screen, board_width, board_height // 2 + 80, json_data['BACK'])

    easy.onRelease = lambda: white_or_black_menu(screen)
    medium.onRelease = lambda: white_or_black_menu(screen)
    hard.onRelease = lambda: white_or_black_menu(screen)
    back.onRelease = lambda: main_menu(screen)

    buttons = []
    buttons.extend([easy, medium, hard, back])
    draw_state(screen, json_data['DIFFICULTY'], buttons)


def white_or_black_menu(screen):
    """
    Chose white or black pieces to play with.
    :param screen:
    :return:
    """
    name, board_width, board_height, _ = Json.get_json_data(json_data)
    button_names = json_data['PLAY_AS']

    white = draw_button(screen, board_width, board_height // 2 - 40, button_names['WHITE'])
    black = draw_button(screen, board_width, board_height // 2, button_names['BLACK'])
    back = draw_button(screen, board_width, board_height // 2 + 80, json_data['BACK'])

    back.onRelease = lambda: new_game_menu(screen)

    buttons = []
    buttons.extend([white, black, back])
    draw_state(screen, json_data['BLACK_WHITE'], buttons)


def sound_menu(screen):
    """
    Method for creating sound menu GUI window.
    :param screen:
    :return:
    """
    name, board_width, board_height, settings = Json.get_json_data(json_data)
    color = json_data['COLORS']
    button_names = json_data['SOUND_MENU']

    off = draw_button(screen, board_width, board_height // 2 - 75, button_names['OFF'], get_color(color, settings, button_names['OFF']))
    low = draw_button(screen, board_width, board_height // 2 - 35, button_names['LOW'], get_color(color, settings, button_names['LOW']))
    medium = draw_button(screen, board_width, board_height // 2 + 5, button_names['MEDIUM'], get_color(color, settings, button_names['MEDIUM']))
    loud = draw_button(screen, board_width, board_height // 2 + 45, button_names['LOUD'], get_color(color, settings, button_names['LOUD']))
    back = draw_button(screen, board_width, board_height // 2 + 120, json_data['BACK'])

    off.onClick = lambda: change_settings(screen, off.string)
    low.onClick = lambda: change_settings(screen, low.string)
    medium.onClick = lambda: change_settings(screen, medium.string)
    loud.onClick = lambda: change_settings(screen, loud.string)

    off.onRelease = lambda: sound_menu(screen)
    low.onRelease = lambda: sound_menu(screen)
    medium.onRelease = lambda: sound_menu(screen)
    loud.onRelease = lambda: sound_menu(screen)
    back.onRelease = lambda: main_menu(screen)

    buttons = []
    buttons.extend([off, low, medium, loud, back])
    draw_state(screen, json_data['MAIN_MENU']['SOUND'], buttons)


def draw_button(screen, width, height, button_text, color=p.Color(json_data['COLORS']['INITIAL'])):
    """
    Method for drawing button objects inside GUI window.
    :param screen:
    :param width:
    :param height:
    :param button_text:
    :param color:
    :return:
    """
    button = pw.Button(screen, width // 2 - 100, height, 200, 30, text=button_text, font=p.font.SysFont(json_data['GUI_FONT']['FONT'], json_data['GUI_FONT']['SIZE']),
                       inactiveColour=color, hoverColour=p.Color(json_data['COLORS']['HOVER']), shadowDistance=-3, shadowColour=p.Color(json_data['SHADOW_COLOR']), radius=5)
    return button


def draw_state(screen, name, buttons):
    """
    Method for creating and rendering current shown state.
    :param screen:
    :param name:
    :param buttons:
    :return:
    """
    while True:
        try:
            events = p.event.get()
            for event in events:
                if event.type == p.QUIT:
                    sys.exit()
            screen.fill((json_data['BACKGROUND_COLOR']['RED'], json_data['BACKGROUND_COLOR']['GREEN'], json_data['BACKGROUND_COLOR']['BLUE']))
            draw_text(screen, name, True)
            for button in buttons:
                button.listen(events)
                button.draw()
            p.display.update()
        except KeyboardInterrupt:
            sys.exit()


def draw_text(screen, text, title=False):
    """
    Draw and render text on screen.
    :param screen:
    :param text:
    :param title:
    :return:
    """
    gui_draw_text = json_data['GUI_DRAW_TEXT']
    if not title:
        font = p.font.SysFont(gui_draw_text['GAME_FONT'], gui_draw_text['FONT_SIZE'], True, True)
        text_object = font.render(text, False, p.Color(gui_draw_text['3D_COLOR']))
        text_location = p.Rect(0, 0, json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT']).move(json_data['BOARD_WIDTH'] / 2 - text_object.get_width() / 2,
                                                                                               json_data['BOARD_HEIGHT'] / 2 - text_object.get_height() / 2)

        text_width = text_object.get_size()[0]
        text_height = text_object.get_size()[1]
        console_rectangle = p.Rect((json_data['BOARD_WIDTH'] - text_width) / 2, (json_data['BOARD_HEIGHT'] - text_object.get_height()) / 2,
                                   text_width + 5, text_height + 5)  # make rectangle
        p.draw.rect(screen, p.Color(gui_draw_text['BACKGROUND_COLOR']), console_rectangle)  # draw it

        screen.blit(text_object, text_location)
        text_object = font.render(text, False, p.Color(gui_draw_text['COLOR']))
        screen.blit(text_object, text_location.move(2, 2))  # 3D effect

    elif title:
        font = p.font.SysFont(gui_draw_text['GUI_FONT'], gui_draw_text['FONT_SIZE'], True, True)
        text_object = font.render(text, False, p.Color(gui_draw_text['3D_COLOR']))
        text_location = p.Rect(0, 0, json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT']).move(json_data['BOARD_WIDTH'] / 2 - text_object.get_width() / 2,
                                                                                               json_data['BOARD_HEIGHT'] / 2 - 150 - text_object.get_height() / 2)
        screen.blit(text_object, text_location)
        text_object = font.render(text, False, p.Color(gui_draw_text['COLOR']))
        screen.blit(text_object, text_location.move(5, 2))  # 3D effect


def change_settings(screen, text):
    """
    Method for changing sound volume settings.
    :param screen:
    :param text:
    :return:
    """
    audio = json_data["AUDIO"]
    json_data['SETTINGS']["SOUND"] = text
    Json.write_to_json(json_data)

    """dummy sound test"""
    sound = p.mixer.Sound(audio["CHECK"])
    #sound = p.mixer.Sound(audio["CAPTURE"])
    #sound = p.mixer.Sound(audio["MOVE"])
    #sound = p.mixer.Sound(audio["CASTLE"])
    
    sound.set_volume(set_volume(json_data['SETTINGS']["SOUND"], audio))
    sound.play()
    sound_menu(screen)


def get_color(color, settings, sound_choices):
    """
    Method for creating color for sound settings buttons. Active setting will be in different color than the rest of buttons.
    :param color:
    :param settings:
    :param sound_choices:
    :return:
    """
    return p.Color(color['HOVER']) if settings['SOUND'] == sound_choices else p.Color(color['INITIAL'])


def set_volume(settings, audio):
    """
    Method for changing volume based on settings.
    :param settings:
    :param audio:
    :return:
    """
    for key, value in audio['SOUND'].items():
        if settings == value['NAME']:
            return value['VOLUME']
