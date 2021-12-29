"""
MIT license

Authors:
Novica Nikolic - R2 39/2020
Jovan Popovic - R2 40/2020
Dejan Jovanovic - R2 45/2020

Domain-Specific Languages DSL, FTN 2021
"""

import GUI
import Json
import pygame as p
from JsonParser import JsonParser


def init():
    """
    Method for running the project.
    :return:
    """
    json_parser = JsonParser()
    json_parser.read_json()

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
