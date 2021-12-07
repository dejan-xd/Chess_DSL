"""
Starting point of the project.
"""

import pygame as p
import GUI
import Json


def init():
    """
    Method for running the project.
    :return:
    """
    json_data = Json.read_from_json()
    p.init()  # initializing the constructor
    p.display.set_caption(json_data['NAME'])
    icon = p.image.load(json_data['IMAGE'])
    p.display.set_icon(icon)
    screen = p.display.set_mode((json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT']))
    screen.fill((json_data['BACKGROUND_COLOR']['RED'], json_data['BACKGROUND_COLOR']['GREEN'], json_data['BACKGROUND_COLOR']['BLUE']))
    p.display.flip()

    GUI.main_menu(screen)


if __name__ == "__main__":
    init()
