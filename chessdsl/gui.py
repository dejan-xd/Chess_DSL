"""
For creating the GUI view.
"""

import sys
import pygame as p
import pygame_widgets as pw
from chessdsl.json_data import JsonData
from chessdsl.json_parser import JsonParser
from chessdsl.chess_main import ChessMain

json_data = JsonData.read_from_json()


class Gui:
    def __init__(self):
        self.json_parser = JsonParser()
        self.color = p.Color(self.json_parser.get_by_key('COLORS', 'INITIAL'))
        self.white = "w"
        self.black = "b"
        self.name, self.board_width, self.board_height, self.settings = self.json_parser.get_json_data()

    def draw_button(self, screen, width, height, button_text, colors=None):
        """
        Method for drawing button objects inside GUI window.
        :param screen:
        :param width:
        :param height:
        :param button_text:
        :param colors:
        :return:
        """
        hover = self.json_parser.get_by_key('COLORS', 'HOVER')
        shadow = self.json_parser.get_by_key('SHADOW_COLOR')
        gui_font = self.json_parser.get_by_key('GUI_FONT', 'FONT')
        gui_font_size = self.json_parser.get_by_key('GUI_FONT', 'SIZE')
        use_color = colors if colors is not None else self.color

        button = pw.Button(screen, width // 2 - 100, height, 200, 30, text=button_text, font=p.font.SysFont(gui_font, gui_font_size),
                           inactiveColour=use_color, hoverColour=p.Color(hover), shadowDistance=-3, shadowColour=p.Color(shadow), radius=5)
        return button

    def draw_text(self, screen, text):
        """
        Draw and render text on screen.
        :param screen:
        :param text:
        :return:
        """
        gui_draw_text = self.json_parser.get_by_key('GUI_DRAW_TEXT')
        board_with = self.json_parser.get_by_key('BOARD_WIDTH')
        board_height = self.json_parser.get_by_key('BOARD_HEIGHT')
        font_size = gui_draw_text['FONT_SIZE']
        three_d_color = gui_draw_text['3D_COLOR']
        color = gui_draw_text['COLOR']
        gui_font = gui_draw_text['GUI_FONT']

        font = p.font.SysFont(gui_font, font_size, True, True)
        text_object = font.render(text, False, p.Color(three_d_color))
        text_location = p.Rect(0, 0, board_with, board_height).move(board_with / 2 - text_object.get_width() / 2,
                                                                    board_height / 2 - 150 - text_object.get_height() / 2)
        screen.blit(text_object, text_location)
        text_object = font.render(text, False, p.Color(color))
        screen.blit(text_object, text_location.move(5, 2))  # 3D effect

    def draw_state(self, screen, name, buttons):
        """
        Method for creating and rendering current shown state.
        :param screen:
        :param name:
        :param buttons:
        :return:
        """
        background_color_red = self.json_parser.get_by_key('BACKGROUND_COLOR', 'RED')
        background_color_green = self.json_parser.get_by_key('BACKGROUND_COLOR', 'GREEN')
        background_color_blue = self.json_parser.get_by_key('BACKGROUND_COLOR', 'BLUE')

        while True:
            try:
                events = p.event.get()
                for event in events:
                    if event.type == p.QUIT:
                        sys.exit()
                screen.fill((background_color_red, background_color_green, background_color_blue))
                self.draw_text(screen, name)
                for button in buttons:
                    button.listen(events)
                    button.draw()
                p.display.update()
            except KeyboardInterrupt:
                sys.exit()

    @staticmethod
    def get_color(color, settings, sound_choices):
        """
        Method for creating color for sound settings buttons. Active setting will be in different color than the rest of buttons.
        :param color:
        :param settings:
        :param sound_choices:
        :return:
        """
        hover = color['HOVER']
        initial = color['INITIAL']
        sound = settings['SOUND']

        return p.Color(hover) if sound == sound_choices else p.Color(initial)

    def change_settings(self, screen, text):
        """
        Method for changing sound volume settings.
        :param screen:
        :param text:
        :return:
        """
        json_data['SETTINGS']["SOUND"] = text
        JsonData.write_to_json(json_data)
        self.settings = json_data['SETTINGS']

        self.sound_menu(screen)

    def sound_menu(self, screen):
        """
        Method for creating sound menu GUI window.
        :param screen:
        :return:
        """
        color = self.json_parser.get_by_key('COLORS')
        button_names = self.json_parser.get_by_key('SOUND_MENU')
        back_color = self.json_parser.get_by_key('BACK')
        main_menu_sound = self.json_parser.get_by_key('MAIN_MENU', 'SOUND')
        btn_off = button_names['OFF']
        btn_low = button_names['LOW']
        btn_medium = button_names['MEDIUM']
        btn_loud = button_names['LOUD']

        off = self.draw_button(screen, self.board_width, self.board_height // 2 - 75, btn_off, self.get_color(color, self.settings, btn_off))
        low = self.draw_button(screen, self.board_width, self.board_height // 2 - 35, btn_low, self.get_color(color, self.settings, btn_low))
        medium = self.draw_button(screen, self.board_width, self.board_height // 2 + 5, btn_medium, self.get_color(color, self.settings, btn_medium))
        loud = self.draw_button(screen, self.board_width, self.board_height // 2 + 45, btn_loud, self.get_color(color, self.settings, btn_loud))
        back = self.draw_button(screen, self.board_width, self.board_height // 2 + 120, back_color)

        off.onClick = lambda: self.change_settings(screen, off.string)
        low.onClick = lambda: self.change_settings(screen, low.string)
        medium.onClick = lambda: self.change_settings(screen, medium.string)
        loud.onClick = lambda: self.change_settings(screen, loud.string)

        off.onRelease = lambda: self.sound_menu(screen)
        low.onRelease = lambda: self.sound_menu(screen)
        medium.onRelease = lambda: self.sound_menu(screen)
        loud.onRelease = lambda: self.sound_menu(screen)
        back.onRelease = lambda: self.main_menu(screen)

        buttons = []
        buttons.extend([off, low, medium, loud, back])
        self.draw_state(screen, main_menu_sound, buttons)

    def main_menu(self, screen):
        """
        Method for creating main menu GUI window.
        :param screen:
        :return:
        """
        button_names = self.json_parser.get_by_key('MAIN_MENU')
        new_game = button_names['NEW_GAME']
        sound = button_names['SOUND']
        exits = button_names['EXIT']

        new_game = self.draw_button(screen, self.board_width, self.board_height // 2 - 50, new_game)
        volume = self.draw_button(screen, self.board_width, self.board_height // 2, sound)
        exit_game = self.draw_button(screen, self.board_width, self.board_height // 2 + 75, exits)

        new_game.onRelease = lambda: self.new_game_menu(screen)
        volume.onRelease = lambda: self.sound_menu(screen)
        exit_game.onRelease = lambda: sys.exit()

        buttons = []
        buttons.extend([new_game, volume, exit_game])
        self.draw_state(screen, self.name, buttons)

    @staticmethod
    def start_game(difficulty, play_as):
        json_data['SETTINGS']['PIECE_COLOR'] = play_as
        json_data['SETTINGS']['DIFFICULTY'] = difficulty
        JsonData.write_to_json(json_data)

        chess_main = ChessMain()
        chess_main.game(json_data['SETTINGS'])

    def white_or_black_menu(self, screen, difficulty):
        """
        Chose white or black pieces to play with.
        :param screen:
        :param difficulty:
        :return:
        """
        button_names = self.json_parser.get_by_key('PLAY_AS')
        black_white = self.json_parser.get_by_key('BLACK_WHITE')
        white = button_names['WHITE']
        black = button_names['BLACK']
        back = self.json_parser.get_by_key('BACK')

        white = self.draw_button(screen, self.board_width, self.board_height // 2 - 40, white)
        black = self.draw_button(screen, self.board_width, self.board_height // 2, black)
        back = self.draw_button(screen, self.board_width, self.board_height // 2 + 80, back)

        white.onRelease = lambda: self.start_game(difficulty, self.white)
        black.onRelease = lambda: self.start_game(difficulty, self.black)
        back.onRelease = lambda: self.new_game_menu(screen)

        buttons = []
        buttons.extend([white, black, back])
        self.draw_state(screen, black_white, buttons)

    def new_game_menu(self, screen):
        """
        Method for creating new game menu GUI window.
        :param screen:
        :return:
        """
        button_names = self.json_parser.get_by_key('NEW_GAME_MENU')
        difficulty = self.json_parser.get_by_key('DIFFICULTY')
        btn_black = self.json_parser.get_by_key('BACK')
        btn_easy = button_names['EASY']
        btn_medium = button_names['MEDIUM']
        btn_hard = button_names['HARD']

        easy = self.draw_button(screen, self.board_width, self.board_height // 2 - 75, btn_easy)
        medium = self.draw_button(screen, self.board_width, self.board_height // 2 - 35, btn_medium)
        hard = self.draw_button(screen, self.board_width, self.board_height // 2 + 5, btn_hard)
        back = self.draw_button(screen, self.board_width, self.board_height // 2 + 80, btn_black)

        easy.onRelease = lambda: self.white_or_black_menu(screen, 0)
        medium.onRelease = lambda: self.white_or_black_menu(screen, 1)
        hard.onRelease = lambda: self.white_or_black_menu(screen, 2)
        back.onRelease = lambda: self.main_menu(screen)

        buttons = []
        buttons.extend([easy, medium, hard, back])
        self.draw_state(screen, difficulty, buttons)
