import sys
import Json
import pygame as p
from tkinter import Tk
from InputThread import InputThread
import time
from GameState import GameState
import Move
from JsonParser import JsonParser

class ChessMain:
    def __init__(self):
        self.json_parser = JsonParser()
        # Izbaciti kad vise se ne bude koristilo
        self.json_data = Json.read_from_json()
        self.user_text = ""
        self.IMAGES = {}
        self.SQ_SIZE = self.json_data['BOARD_HEIGHT'] // self.json_data['DIMENSION']
        self.board_colors = [p.Color(self.json_data['BOARD_COLORS']['WHITE']), p.Color(self.json_data['BOARD_COLORS']['BLACK'])]
        self.game_state = GameState()
        self.it = InputThread()  # user inputs
        self.move_from = self.move_to = None

    def load_images(self):
        """
        Initialize a global dictionary of chess images. This will be called exactly once in the main.
        :return:
        """
        pieces = self.json_data['PIECES']
        for key, value in pieces.items():
            self.IMAGES[value] = p.transform.scale(p.image.load("images/" + value + ".png"), (self.SQ_SIZE, self.SQ_SIZE))

    def create_move_log_rectangle(self):
        """
        Method for creating move log rectangle object.
        :return:
        """
        move_log_rectangle = p.Rect(self.json_data['BOARD_WIDTH'], 0, self.json_data['MOVE_LOG_PANEL_WIDTH'], self.json_data['MOVE_LOG_PANEL_HEIGHT'])
        return move_log_rectangle

    def create_move_information_rectangle(self):
        """
        Method for creating console information rectangle object.
        :return:
        """
        move_information_rectangle = p.Rect(0, self.json_data['BOARD_HEIGHT'],
                                            self.json_data['BOARD_WIDTH'] + self.json_data['MOVE_LOG_PANEL_WIDTH'],
                                            self.json_data['MOVE_INFORMATION_HEIGHT'])
        return move_information_rectangle

    def draw_board(self, screen):
        """
        Draw the squares on the board. The top left square is always white.
        :param screen:
        :return:
        """

        for row in range(self.json_data['DIMENSION']):
            for col in range(self.json_data['DIMENSION']):
                color = self.board_colors[((row + col) % 2)]  # pick color
                p.draw.rect(screen, color, p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

    def draw_pieces(self, screen, board):
        """
        Draw the pieces on the board using the current GameState.board.
        :param screen:
        :param board:
        :return:
        """
        for row in range(self.json_data['DIMENSION']):
            for col in range(self.json_data['DIMENSION']):
                piece = board[row][col]
                if piece != "--":
                    screen.blit(self.IMAGES[piece], p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

    def draw_coordinates(self, screen):
        """
        Draw the square coordinates on the chess board.
        :param screen:
        :return:
        """
        row_list = self.json_data['BOARD_COORDINATES']['ROWS']
        col_list = self.json_data['BOARD_COORDINATES']['COLUMNS']
        font = p.font.SysFont(self.json_data['BOARD_COORDINATES']['FONT'], self.json_data['BOARD_COORDINATES']['SIZE'], False, False)
        for row in row_list:
            for col in col_list:
                text_object = font.render(" " + row + col, False, p.Color(self.json_data['BOARD_COORDINATES']['COLOR']))
                text_location = p.Rect(row_list.index(row) * self.SQ_SIZE, col_list.index(col) * self.SQ_SIZE, self.json_data['BOARD_WIDTH'], self.json_data['BOARD_HEIGHT'])
                screen.blit(text_object, text_location)

    def draw_move_information(self, screen):
        """
        Method for drawing panel which will display move information.
        :param screen:
        :return:
        """

        console_panel = self.json_data['CONSOLE_PANEL']
        move_information_rectangle = self.create_move_information_rectangle()

        p.draw.rect(screen, p.Color(console_panel['PANEL_COLOR']), move_information_rectangle)
        p.draw.rect(screen, p.Color(console_panel['BORDER_COLOR']), move_information_rectangle, 1)

    def draw_console(self, screen, font):
        """
        Logic for creating input console and handling input strings.
        :param screen:
        :param font:
        :return:
        """

        console_panel = self.json_data['CONSOLE_PANEL']
        console_rectangle = p.Rect(0, self.json_data['BOARD_HEIGHT'] + self.json_data['MOVE_INFORMATION_HEIGHT'],
                                   self.json_data['BOARD_WIDTH'] + self.json_data['MOVE_LOG_PANEL_WIDTH'], self.json_data['CONSOLE_HEIGHT'])

        p.draw.rect(screen, p.Color(console_panel['PANEL_COLOR']), console_rectangle)
        p.draw.rect(screen, p.Color(console_panel['BORDER_COLOR']), console_rectangle, 1)

        text_object = font.render(">>> " + self.user_text, True, p.Color(console_panel['INPUT_TEXT_COLOR']))
        text_location = console_rectangle.move(5, 5)

        screen.blit(text_object, text_location)

    def move_log_panel_lines_and_text(self, screen, move_log_panel, move_log_rectangle, font, settings):
        """
        Method for preparing move log panel. Drawing border, lines and starting text (white, black column and number of wins).
        :param screen:
        :param move_log_panel:
        :param move_log_rectangle:
        :param font:
        :param settings:
        :return:
        """
        p.draw.rect(screen, p.Color(move_log_panel['PANEL_COLOR']), move_log_rectangle)
        p.draw.rect(screen, p.Color(move_log_panel['BORDER_COLOR']), move_log_rectangle, move_log_panel['BORDER_SIZE'])

        p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (self.json_data['BOARD_WIDTH'], 17),
                    (self.json_data['BOARD_WIDTH'] + self.json_data['MOVE_LOG_PANEL_WIDTH'], 17))
        p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (self.json_data['BOARD_WIDTH'], self.json_data['BOARD_HEIGHT'] - 15),
                    (self.json_data['BOARD_WIDTH'] + self.json_data['MOVE_LOG_PANEL_WIDTH'], self.json_data['BOARD_HEIGHT'] - 15))
        p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (self.json_data['BOARD_WIDTH'] + (self.json_data['MOVE_LOG_PANEL_WIDTH'] / 2), 0),
                    (self.json_data['BOARD_WIDTH'] + (self.json_data['MOVE_LOG_PANEL_WIDTH'] / 2), self.json_data['BOARD_HEIGHT']))

        text = "White\tBlack"
        text = text.replace('\t', ' ' * 30)
        text_object = font.render(text, True, p.Color(move_log_panel['FONT_COLOR']))
        text_location = move_log_rectangle.move((self.json_data['MOVE_LOG_PANEL_WIDTH'] - text_object.get_width()) / 2, 3)
        screen.blit(text_object, text_location)

        text = "White: " + str(settings['WHITE_WINS']) + "\tBlack: " + str(settings['BLACK_WINS'])
        text = text.replace('\t', ' ' * 20)
        text_object = font.render(text, True, p.Color(move_log_panel['FONT_COLOR']))
        text_location = move_log_rectangle.move((self.json_data['MOVE_LOG_PANEL_WIDTH'] - text_object.get_width()) / 2, self.json_data['BOARD_HEIGHT'] - text_object.get_height())
        screen.blit(text_object, text_location)

    def draw_move_log(self, screen, font, settings):
        """
        Draws the move log for chess notations.
        :param screen:
        :param font:
        :param settings:
        :return:
        """

        move_log_panel = self.json_data['MOVE_LOG_PANEL']
        move_log_rectangle = self.create_move_log_rectangle()

        self.move_log_panel_lines_and_text(screen, move_log_panel, move_log_rectangle, font, settings)

    def draw_game_state(self, screen, move_log_font, settings):
        """
        Responsible for all the graphics within a current game state.
        :param screen:
        :param move_log_font:
        :param settings:
        :return:
        """
        self.draw_board(screen)  # draw squares on the board
        self.draw_pieces(screen, self.game_state.board)  # draw pieces on top of squares
        self.draw_coordinates(screen)  # draw coordinates on board
        self.draw_move_information(screen)  # draw move information
        self.draw_console(screen, move_log_font)  # draw console for inputs
        self.draw_move_log(screen, move_log_font, settings)  # draw move log for chess notations

    def move_logic(self, move_made, animate):
        """
        Logic for pasting/reading the move from game console and executing player's move.
        :param move_made:
        :return:
        """
        self.it.enter = True
        self.it.input_command = "print('" + self.user_text.lower() + "')"
        time.sleep(0.1)  # wait for another thread to get all information

        if not self.game_state.game_over:
            move_from = self.it.move_from
            move_to = self.it.move_to

            if move_from is not None and move_to is not None:

                move = Move.Move(move_from, move_to, self.game_state.board)
                self.game_state.make_move(move)
                move_made = animate = True

        return move_made, animate

    def animate_move(self, move, screen, board, clock):
        """
        Method for animating a move on the chess board.
        :param move:
        :param screen:
        :param board:
        :param clock:
        :return:
        """
        delta_row = move.endRow - move.startRow
        delta_col = move.endCol - move.startCol
        frames_per_square = self.json_parser.get_by_key('FRAMES_PER_SQUARE')  # frames to move one square
        frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

        for frame in range(frame_count + 1):
            row, col = (move.startRow + delta_row * frame / frame_count, move.startCol + delta_col * frame / frame_count)

            # redraw
            self.draw_board(screen)
            self.draw_pieces(screen, board)
            self.draw_coordinates(screen)

            # erase the piece moved from it's ending square
            color = self.board_colors[(move.endRow + move.endCol) % 2]
            end_square = p.Rect(move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
            p.draw.rect(screen, color, end_square)

            # draw captured piece onto rectangle
            if move.pieceCaptured != "--":
                screen.blit(self.IMAGES[move.pieceCaptured], end_square)

            # draw moving piece
            screen.blit(self.IMAGES[move.pieceMoved], p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

            p.display.flip()
            clock.tick(self.json_parser.get_by_key('MAX_FPS'))

    def game(self, settings):
        """
        The main driver for the code. This will handle user input and update the graphics.
        :return:
        """

        self.it.start()  # start thread

        clock = p.time.Clock()
        screen = p.display.set_mode((self.json_parser.get_by_key('BOARD_WIDTH') + self.json_parser.get_by_key('MOVE_LOG_PANEL_WIDTH'),
                                     self.json_parser.get_by_key('BOARD_HEIGHT') + self.json_parser.get_by_key('MOVE_INFORMATION_HEIGHT') + self.json_parser.get_by_key('CONSOLE_HEIGHT')))
        move_log_font = p.font.SysFont(self.json_parser.get_by_key('MOVE_LOG_FONT', 'FONT'), self.json_parser.get_by_key('MOVE_LOG_FONT', 'SIZE'), False, False)

        self.load_images()  # do this only once, before the while loop

        if settings['PIECE_COLOR'] == "w":
            self.game_state.player_one = True
        elif settings['PIECE_COLOR'] == "b":
            self.game_state.player_two = True

        move_made = animate = False  # flags

        while True:
            self.draw_game_state(screen, move_log_font, settings)
            clock.tick(self.json_data['MAX_FPS'])  # refresh screen frame rate
            p.display.flip()  # draw the game

            for event in p.event.get():
                if event.type == p.QUIT:  # command to exit the game
                    p.quit()
                    sys.exit()

                elif event.type == p.KEYDOWN:
                    if event.key == p.K_BACKSPACE:
                        self.user_text = self.user_text[:-1]

                    elif event.key == p.K_v and p.key.get_mods() & p.KMOD_CTRL:
                        self.user_text = Tk().clipboard_get()

                    elif event.key == p.K_RETURN:
                        move_made = animate = self.move_logic(move_made, animate)  # move logic

                        if self.it.input_command == self.json_parser.get_by_key('COMMANDS', 'UNDO') and not self.game_state.game_over:
                            self.game_state.undo_move()
                            move_made = animate = True
                            self.it.input_command = self.it.move_from = self.it.move_to = None

                        if self.user_text == 'exit':
                            sys.exit()

                        self.user_text = ""

                    else:
                        if len(self.user_text) != 50:
                            self.user_text += event.unicode

            # logic when move has been made
            if move_made:
                # For piece move animation
                if animate:
                    self.animate_move(self.game_state.moveLog[-1], screen, self.game_state.board, clock)
                move_made = animate = False
                self.it.input_command = self.it.move_from = self.it.move_to = None
