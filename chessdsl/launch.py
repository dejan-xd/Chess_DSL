"""
MIT license

Authors:
Novica Nikolic - R2 39/2020
Jovan Popovic - R2 40/2020
Dejan Jovanovic - R2 45/2020

Domain-Specific Languages DSL, FTN 2021
"""

import pygame as p
from chessdsl.gui import Gui
from chessdsl.json_data import JsonData
from chessdsl.json_parser import JsonParser
import os


def init():
    """
    Method for running the project.
    :return:
    """
    json_parser = JsonParser()
    json_parser.read_json()

    json_data = JsonData.read_from_json()
    p.init()  # initializing the constructor
    icon_path = os.path.join(os.path.dirname(__file__), 'images', json_data['IMAGE'])
    p.display.set_caption(json_data['NAME'])
    icon = p.image.load(icon_path)
    p.display.set_icon(icon)
    screen = p.display.set_mode((json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT']))
    screen.fill((json_data['BACKGROUND_COLOR']['RED'], json_data['BACKGROUND_COLOR']['GREEN'], json_data['BACKGROUND_COLOR']['BLUE']))
    p.display.flip()

    gui = Gui()
    gui.main_menu(screen)


if __name__ == "__main__":
    init()
