import sys
import Json
import pygame as p
from tkinter import Tk
from InputThread import InputThread
import time
import GameState
import Move
from JsonParser import JsonParser
import ChessAI
import GUI

game_state = GameState.GameState()


class ChessMain:
    def __init__(self):
        self.file = "settings.json"
        self.json_parser = JsonParser(self.file)
        # Izbaciti kad vise se ne bude koristilo
        self.json_data = Json.read_from_json()
        self.user_text = ""
        self.IMAGES = {}
        self.SQ_SIZE = self.json_data['BOARD_HEIGHT'] // self.json_data['DIMENSION']
        self.board_colors = [p.Color(self.json_data['BOARD_COLORS']['WHITE']), p.Color(self.json_data['BOARD_COLORS']['BLACK'])]
        self.game_state = game_state
        self.valid_moves = self.game_state.get_valid_moves()
        self.it = InputThread()  # user inputs
        self.notation_scroll_y = self.notation_text_height = 0  # for scrolling notation text
        self.console_scroll_y = self.console_text_height = 0  # for scrolling console text
        self.white_threefold_counter = self.black_threefold_counter = self.fifty_move_rule_counter = 0  # counter for threefold moves and fifty move draw rule
        self.counter_list_storage = []  # store all counters in list
        self.threefold_list = []  # keep track of all moves so we can check if threefold happened

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

    def draw_move_information(self, screen, font):
        """
        Method for drawing panel which will display move information.
        :param screen:
        :param font:
        :return:
        """
        console_panel = self.json_parser.get_by_key('CONSOLE_PANEL')
        move_information_rectangle = self.create_move_information_rectangle()

        p.draw.rect(screen, p.Color(console_panel['PANEL_COLOR']), move_information_rectangle)
        p.draw.rect(screen, p.Color(console_panel['BORDER_COLOR']), move_information_rectangle, 1)

        text_y = 5
        for i in range(len(self.it.information)):
            text_position = self.console_scroll_y + text_y

            if text_position < 5:  # first row
                text_position = -1000  # remove from screen

            text_object = font.render(self.it.information[i][0], True, p.Color(self.it.information[i][1]))
            text_location = move_information_rectangle.move(5, text_position)
            screen.blit(text_object, text_location)

            text_y += 15 + 5  # draw text one under another

        self.console_text_height = text_y

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
        BORDER_COLOR = move_log_panel['BORDER_COLOR']
        BOARD_HEIGHT = self.json_parser.get_by_key('BOARD_HEIGHT')
        BORDER_SIZE = move_log_panel['BORDER_SIZE']
        BOARD_WIDTH = self.json_parser.get_by_key('BOARD_WIDTH')
        PANEL_COLOR = move_log_panel['PANEL_COLOR']
        LINE_COLOR = move_log_panel['LINE_COLOR']
        MOVE_LOG_PANEL_WIDTH = self.json_parser.get_by_key('MOVE_LOG_PANEL_WIDTH')
        FONT_COLOR = move_log_panel['FONT_COLOR']
        WHITE_WINS = settings['WHITE_WINS']
        BLACK_WINS = settings['BLACK_WINS']

        p.draw.rect(screen, p.Color(PANEL_COLOR), move_log_rectangle)
        p.draw.rect(screen, p.Color(BORDER_COLOR), move_log_rectangle, BORDER_SIZE)

        p.draw.line(screen, p.Color(LINE_COLOR), (BOARD_WIDTH, 17), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, 17))
        p.draw.line(screen, p.Color(LINE_COLOR), (BOARD_WIDTH, BOARD_HEIGHT - 15), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT - 15))
        p.draw.line(screen, p.Color(LINE_COLOR), (BOARD_WIDTH + (MOVE_LOG_PANEL_WIDTH / 2), 0), (BOARD_WIDTH + (MOVE_LOG_PANEL_WIDTH / 2), BOARD_HEIGHT))

        text = "White\tBlack"
        text = text.replace('\t', ' ' * 30)
        text_object = font.render(text, True, p.Color(FONT_COLOR))
        text_location = move_log_rectangle.move((MOVE_LOG_PANEL_WIDTH - text_object.get_width()) / 2, 3)
        screen.blit(text_object, text_location)

        text = "White: " + str(WHITE_WINS) + "\tBlack: " + str(BLACK_WINS)
        text = text.replace('\t', ' ' * 20)
        text_object = font.render(text, True, p.Color(FONT_COLOR))
        text_location = move_log_rectangle.move((MOVE_LOG_PANEL_WIDTH - text_object.get_width()) / 2, BOARD_HEIGHT - text_object.get_height())
        screen.blit(text_object, text_location)

    def create_chess_notation(self):
        """
        Method for editing notations for moves from move log. If the notation is None edit it. If the move is checkmate or check, edit it's notation.
        :return:
        """
        for i in range(0, len(self.game_state.moveLog)):
            if self.game_state.moveLog[i].notation is None:
                self.game_state.moveLog[i].notation = str(self.game_state.moveLog[i])

        if self.game_state.multiple_moves:
            self.disambiguating_moves_notations()

        if (self.game_state.in_check() and not self.game_state.checkMate) and self.game_state.moveLog[-1].notation[-1] != self.json_parser.get_by_key('CHESS_NOTATION', 'CHECK'):
            self.game_state.moveLog[-1].notation = str(self.game_state.moveLog[-1].notation) + self.json_parser.get_by_key('CHESS_NOTATION', 'CHECK')

        elif self.game_state.checkMate and self.game_state.moveLog[-1].notation[-1] != self.json_parser.get_by_key('CHESS_NOTATION', 'CHECKMATE'):
            self.game_state.moveLog[-1].notation = str(self.game_state.moveLog[-1].notation) + self.json_parser.get_by_key('CHESS_NOTATION', 'CHECKMATE')

    def disambiguating_moves_notations(self):
        """
        Function for creating notations if there is disambiguating moves. Disambiguating moves happens when two (or more) identical pieces can move to the same square,
        the moving piece is uniquely identified by specifying the piece's letter, followed by (in descending order of preference):
            1. the file of departure (if they differ); or
            2. the rank of departure (if the files are the same but the ranks differ); or
            3. both the file and rank of departure (if neither alone is sufficient to identify the piece, 
                which occurs only in rare cases where a player has three or more identical pieces able to reach the same square,
                as a result of one or more pawns having promoted).
        :return:
        """
        self.game_state.multiple_moves = False
        start_square = self.game_state.moveLog[-1].colsToFiles[self.game_state.moveLog[-1].startCol] + self.game_state.moveLog[-1].rowsToRanks[self.game_state.moveLog[-1].startRow]

        # disambiguating for two moves
        if len(self.it.disambiguating_moves_list) == 2:
            # if row is the same
            if self.it.disambiguating_moves_list[0][0] == self.it.disambiguating_moves_list[1][0]:
                self.game_state.moveLog[-1].notation = str(self.game_state.moveLog[-1])[:1] + start_square[0] + str(self.game_state.moveLog[-1])[1:]
            # if column is the same
            if self.it.disambiguating_moves_list[0][1] == self.it.disambiguating_moves_list[1][1]:
                self.game_state.moveLog[-1].notation = str(self.game_state.moveLog[-1])[:1] + start_square[1] + str(self.game_state.moveLog[-1])[1:]
        # disambiguating for three moves (three pawn promotions)
        if len(self.it.disambiguating_moves_list) == 3:
            self.game_state.moveLog[-1].notation = str(self.game_state.moveLog[-1])[:1] + start_square + str(self.game_state.moveLog[-1])[1:]

    def draw_text_move_log_panel(self, screen, move_log_panel, move_log_rectangle, font, notation_text):
        """
        Method for drawing notation list on move log panel. Also contains logic for creating scroll up/down feature.
        :param screen:
        :param move_log_panel:
        :param move_log_rectangle:
        :param font:
        :param notation_text:
        :return:
        """
        FONT_COLOR = move_log_panel['FONT_COLOR']
        TEXT_POSITIONING = move_log_panel['TEXT_POSITIONING']
        TEXT_Y = TEXT_POSITIONING['TEXT_HEIGHT_PADDING']
        WHITE_WIDTH_PADDING = TEXT_POSITIONING['WHITE_WIDTH_PADDING']
        BLACK_WIDTH_PADDING = TEXT_POSITIONING['BLACK_WIDTH_PADDING']
        LINE_SPACING = TEXT_POSITIONING['LINE_SPACING']

        for i in range(len(notation_text)):
            parts = notation_text[i].split("\t")  # split by tab
            text_position = TEXT_Y + self.notation_scroll_y

            if text_position < TEXT_POSITIONING['TEXT_HEIGHT_PADDING']:  # first row
                text_position = -1000  # remove from screen
            elif text_position > self.json_parser.get_by_key('BOARD_HEIGHT') - TEXT_POSITIONING['TEXT_HEIGHT_PADDING']:  # last row
                text_position = 1000  # remove from screen

            text_object = font.render(parts[0], True, p.Color(FONT_COLOR))  # white column
            text_location = move_log_rectangle.move(WHITE_WIDTH_PADDING, text_position)
            screen.blit(text_object, text_location)

            text_object = font.render(parts[1], True, p.Color(FONT_COLOR))  # black column
            text_location = move_log_rectangle.move(BLACK_WIDTH_PADDING, text_position)
            screen.blit(text_object, text_location)

            TEXT_Y += text_object.get_height() + LINE_SPACING  # draw text one under another

        self.notation_text_height = TEXT_Y

    def draw_move_log(self, screen, font, settings):
        """
        Draws the move log for chess notations.
        :param screen:
        :param font:
        :param settings:
        :return:
        """

        move_log_panel = self.json_parser.get_by_key('MOVE_LOG_PANEL')
        move_log_rectangle = self.create_move_log_rectangle()

        self.move_log_panel_lines_and_text(screen, move_log_panel, move_log_rectangle, font, settings)
        self.create_chess_notation()

        notation_text = []
        for row in range(0, len(self.game_state.moveLog), 2):
            move_string = str(row // 2 + 1) + ". " + self.game_state.moveLog[row].notation + "\t"  # make move_string
            if row + 1 < len(self.game_state.moveLog):  # black made a move
                move_string += self.game_state.moveLog[row + 1].notation  # add black move to the move_string, example (1. d4 d5)
            notation_text.append(move_string)

        self.draw_text_move_log_panel(screen, move_log_panel, move_log_rectangle, font, notation_text)

    def highlight_squares(self, screen, move_from, move_to):
        """
        Method for highlighting squares on the board.
        :param screen:
        :param move_from:
        :param move_to:
        :return:
        """
        s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
        colors_palette = self.json_parser.get_by_key('HIGHLIGHT_COLORS')

        # last move coloring
        if len(self.game_state.moveLog) != 0:
            self.highlight_squares_move_colors(screen, s, colors_palette)

        # is check coloring
        if self.game_state.in_check():
            s.fill(p.Color(colors_palette['IN_CHECK']))
            if self.game_state.whiteToMove:
                screen.blit(s, (self.game_state.whiteKingLocation[1] * self.SQ_SIZE, self.game_state.whiteKingLocation[0] * self.SQ_SIZE))
            else:
                screen.blit(s, (self.game_state.blackKingLocation[1] * self.SQ_SIZE, self.game_state.blackKingLocation[0] * self.SQ_SIZE))

        # rest colorings
        if move_from == move_to and (move_from is not None or move_to is not None):
            self.highlight_squares_moves(screen, s, colors_palette, move_from)

    def highlight_squares_moves(self, screen, s, colors_palette, move_from):
        """
        For the rest of square moves highlighting.
        :param screen:
        :param s:
        :param colors_palette:
        :param move_from:
        :return:
        """
        row, col = move_from

        if self.game_state.board[row][col][0] == ('w' if self.game_state.whiteToMove else 'b'):

            # selected square coloring
            if self.game_state.in_check() and move_from == self.game_state.whiteKingLocation:
                pass
            else:
                s.fill(p.Color(colors_palette['SELECTED_SQUARE']))
                screen.blit(s, (col * self.SQ_SIZE, row * self.SQ_SIZE))

            for move in self.valid_moves:
                if move.startRow == row and move.startCol == col:

                    # possible moves from selected square
                    if (move.endRow + move.endCol) % 2 == 0:
                        s.fill(p.Color(colors_palette['MOVE_TO_BRIGHT']))
                    else:
                        s.fill(p.Color(colors_palette['MOVE_TO_DARK']))
                    screen.blit(s, (move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE))

                    # possible captures coloring
                    if self.game_state.board[move.endRow][move.endCol][0] == ('b' if self.game_state.whiteToMove else 'w') or move.isEnPassantMove:
                        if (move.endRow + move.endCol) % 2 == 0:
                            s.fill(p.Color(colors_palette['CAPTURE_BRIGHT']))
                        else:
                            s.fill(p.Color(colors_palette['CAPTURE_DARK']))
                        screen.blit(s, (move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE))

    def highlight_squares_move_colors(self, screen, surface, colors_palette):
        """
        Color last move squares to green.
        :param screen:
        :param surface:
        :param colors_palette:
        :return:
        """
        start_row = self.game_state.moveLog[-1].startRow
        start_col = self.game_state.moveLog[-1].startCol
        end_row = self.game_state.moveLog[-1].endRow
        end_col = self.game_state.moveLog[-1].endCol

        if (start_row + start_col) % 2 == 0:
            surface.fill(p.Color(colors_palette['LAST_MOVE_BRIGHT']))
        else:
            surface.fill(p.Color(colors_palette['LAST_MOVE_DARK']))

        if self.game_state.moveLog[-1].isCastleMove:
            surface.fill(p.Color(colors_palette['CASTLE']))
        screen.blit(surface, (start_col * self.SQ_SIZE, start_row * self.SQ_SIZE))

        if (end_row + end_col) % 2 == 0:
            surface.fill(p.Color(colors_palette['LAST_MOVE_BRIGHT']))
        else:
            surface.fill(p.Color(colors_palette['LAST_MOVE_DARK']))

        if self.game_state.moveLog[-1].isCastleMove:
            surface.fill(p.Color(colors_palette['CASTLE']))
        screen.blit(surface, (end_col * self.SQ_SIZE, end_row * self.SQ_SIZE))

    def draw_game_state(self, screen, move_log_font, settings):
        """
        Responsible for all the graphics within a current game state.
        :param screen:
        :param move_log_font:
        :param settings:
        :return:
        """
        self.draw_board(screen)  # draw squares on the board
        self.highlight_squares(screen, self.it.move_from, self.it.move_to)  # highlight squares
        self.draw_pieces(screen, self.game_state.board)  # draw pieces on top of squares
        self.draw_coordinates(screen)  # draw coordinates on board
        self.draw_move_information(screen, move_log_font)  # draw move information
        self.draw_console(screen, move_log_font)  # draw console for inputs
        self.draw_move_log(screen, move_log_font, settings)  # draw move log for chess notations

    def get_move(self):
        """
        Checking if the move was castling move first. If not return move_from and move_to so the move can be made.
        :return:
        """
        is_castle = False
        if self.it.input_command == self.json_parser.get_by_key('COMMANDS', 'CASTLE_SHORT'):
            if self.game_state.whiteToMove:
                move_from = self.game_state.whiteKingLocation  # (7, 4)
                move_to = self.game_state.whiteKingCastleLocationKingSide  # (7, 6)
            else:
                move_from = self.game_state.blackKingLocation  # (0, 4)
                move_to = self.game_state.blackKingCastleLocationKingSide  # (0, 6)
            is_castle = True

        elif self.it.input_command == self.json_parser.get_by_key('COMMANDS', 'CASTLE_LONG'):
            if self.game_state.whiteToMove:
                move_from = self.game_state.whiteKingLocation  # (7, 4)
                move_to = self.game_state.whiteKingCastleLocationQueenSide  # (7, 2)
            else:
                move_from = self.game_state.blackKingLocation  # (0, 4)
                move_to = self.game_state.blackKingCastleLocationQueenSide  # (0, 2)
            is_castle = True

        else:
            move_from = self.it.move_from  # if it's any other move
            move_to = self.it.move_to

        return move_from, move_to, is_castle

    def move_logic(self, move_made, animate):
        """
        Logic for pasting/reading the move from game console and executing player's move.

        :param move_made:
        :param animate:
        :return:
        """
        self.it.enter = True
        self.it.input_command = "print('" + self.user_text.lower() + "')"
        time.sleep(0.1)  # wait for another thread to get all information

        if not self.game_state.game_over and self.game_state.player_turn:
            move_from, move_to, is_castle = self.get_move()

            if move_from is not None and move_to is not None:
                move = Move.Move(move_from, move_to, self.game_state.board)
                for i in range(len(self.valid_moves)):  # list of moves generated by the chess engine
                    if move == self.valid_moves[i]:
                        self.game_state.make_move(self.valid_moves[i])
                        move_made = animate = True

                if not move_made and is_castle:
                    key = len(self.it.information) - 1
                    self.it.information[key] = [self.it.information[key][0] + " >>> ERROR", "brown1"]

        return move_made, animate

    def animate_castle_move_logic(self, frame, frame_count, rock_piece, rock_start_end_row, rock_start_col, rock_move_col, rock_end_col, is_short):
        """
        Logic behind animating castle move. Creates smooth piece sliding for top piece.
        :param frame:
        :param frame_count:
        :param rock_piece:
        :param rock_start_end_row:
        :param rock_start_col:
        :param rock_move_col:
        :param rock_end_col:
        :param is_short:
        :return:
        """
        if is_short:
            rock_row, rock_col = (rock_start_end_row - 0 * frame / frame_count, rock_start_col - rock_move_col * frame / frame_count)
        else:
            rock_row, rock_col = (rock_start_end_row - 0 * frame / frame_count, rock_start_col + rock_move_col * frame / frame_count)

        rock_end_square = p.Rect(rock_end_col * self.SQ_SIZE, rock_start_end_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
        castle_color = self.board_colors[(rock_start_end_row + rock_end_col) % 2]

        return rock_piece, rock_row, rock_col, castle_color, rock_end_square

    def animate_castle_move(self, move, delta_col, frame, frame_count):
        """
        Method for animating castle move.
        :param move:
        :param delta_col:
        :param frame:
        :param frame_count:
        :return:
        """
        # white castling
        if move.startRow == 7:
            rock_piece = self.json_parser.get_by_key('PIECES', 'WR')

            # king side castle
            if delta_col == 2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 7, 7, 2, 5, is_short=True)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

            # queen side castle
            elif delta_col == -2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 7, 0, 3, 3, is_short=False)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

        # black castling
        elif move.startRow == 0:
            rock_piece = self.json_parser.get_by_key('PIECES', 'BR')

            # black king side castle
            if delta_col == 2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 0, 7, 2, 5, is_short=True)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

            elif delta_col == -2:  # black queen side castle
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 0, 0, 3, 3, is_short=False)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

    def animate_move(self, move, screen, board, clock, settings):
        """
        Method for animating a move on the chess board.
        :param move:
        :param screen:
        :param board:
        :param clock:
        :param settings:
        :return:
        """
        delta_row = move.endRow - move.startRow
        delta_col = move.endCol - move.startCol
        frames_per_square = self.json_parser.get_by_key('FRAMES_PER_SQUARE')  # frames to move one square
        frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

        for frame in range(frame_count + 1):
            row, col = (move.startRow + delta_row * frame / frame_count, move.startCol + delta_col * frame / frame_count)
            rock_row = rock_col = castle_color = rock_end_square = rock_piece = None  # for assignments before reference

            # animation castle move
            if move.isCastleMove:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_animation(move, delta_col, frame, frame_count)

            # redraw
            self.draw_board(screen)
            self.draw_pieces(screen, board)
            self.draw_coordinates(screen)

            # erase rock piece after redraw
            if move.isCastleMove:
                p.draw.rect(screen, castle_color, rock_end_square)

            # erase the piece moved from it's ending square
            color = self.board_colors[(move.endRow + move.endCol) % 2]
            end_square = p.Rect(move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
            p.draw.rect(screen, color, end_square)

            # draw captured piece onto rectangle
            if move.pieceCaptured != "--":
                if move.isEnPassantMove:  # if is en passant move make en passant row where it happened
                    en_passant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                    end_square = p.Rect(move.endCol * self.SQ_SIZE, en_passant_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)

                screen.blit(self.IMAGES[move.pieceCaptured], end_square)

            # draw moving piece
            screen.blit(self.IMAGES[move.pieceMoved], p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

            # draw rock piece after castling
            if move.isCastleMove:
                screen.blit(self.IMAGES[rock_piece], p.Rect(rock_col * self.SQ_SIZE, rock_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

            p.display.flip()
            clock.tick(self.json_parser.get_by_key('MAX_FPS'))

        # call audio function after animation
        self.game_audio(move, settings)

    def ai_move_logic(self):
        """
        Logic for executing AI's move.
        :return:
        """
        ai = ChessAI.ChessAI().find_best_move(self.game_state, self.valid_moves)  # find best move
        if ai is None:
            ai = ChessAI.ChessAI().find_random_move(self.valid_moves)
        game_state.make_move(ai)

    @staticmethod
    def scroll(event, scroll_y, scroll_panel_height, text_height):
        """
        Method for scrolling notation and move information text in panels.
        :param event:
        :param scroll_y:
        :param scroll_panel_height:
        :param text_height:
        :return:
        """
        if event.button == 4:
            scroll_y = min(scroll_y + 20, 0)

        elif event.button == 5:
            if text_height > scroll_panel_height:
                while not scroll_panel_height % 20 == 0:
                    scroll_panel_height += 1
                scroll_y = max(scroll_y - 20, scroll_panel_height)

        return scroll_y

    def move_console_text(self):
        """
        Method for moving console text once enter is pressed.
        :return:
        """
        scroll_panel_height_notation = self.json_parser.get_by_key('BOARD_HEIGHT') - self.notation_text_height
        if self.game_state.player_turn and scroll_panel_height_notation < 50:
            self.notation_scroll_y -= 20

        scroll_panel_height_console = self.json_parser.get_by_key('MOVE_INFORMATION_HEIGHT') - self.console_text_height
        if self.game_state.player_turn and scroll_panel_height_console < 20:
            self.console_scroll_y -= 20

    def undo_logic(self):
        """
        Method for executing the undo move logic.
        :return:
        """
        for i in range(2):  # check twice for both human and AI move
            current_board = []
            self.game_state.undo_move()

            for board in self.game_state.board:
                current_board += ''.join(map(str, board))  # convert to string and store current board state
            if current_board in self.threefold_list:
                self.threefold_list.remove(current_board)

        try:  # try catch block to prevent IndexError
            self.white_threefold_counter = self.counter_list_storage[-3][0]
            self.black_threefold_counter = self.counter_list_storage[-3][1]
            self.fifty_move_rule_counter = self.counter_list_storage[-3][2]
            del self.counter_list_storage[-2:]  # remove two last elements from counter_list_storage
        except IndexError:
            self.threefold_list.clear()
            self.counter_list_storage.clear()
            self.white_threefold_counter = self.black_threefold_counter = self.fifty_move_rule_counter = 0  # restart counter values

    def move_made_logic(self, undo):
        """
        Logic if the move is made. Check if three fold or fifty move rule happened.
        :param undo:
        :return:
        """
        if not undo:
            current_board = []
            for board in self.game_state.board:
                current_board += ''.join(map(str, board))

            # add castling rights to the current board state
            current_board += str(self.game_state.currentCastlingRights.wks) + str(self.game_state.currentCastlingRights.wqs) + \
                str(self.game_state.currentCastlingRights.bks) + str(self.game_state.currentCastlingRights.bqs)

            # if current board state happened
            if current_board in self.threefold_list:
                if self.game_state.whiteToMove:
                    self.black_threefold_counter += 1
                else:
                    self.white_threefold_counter += 1
            else:
                self.threefold_list.append(current_board)

            # take last move from move log
            move = self.game_state.moveLog[-1]

            # check for fifty move draw rule
            if move.pieceMoved[1] != 'p':
                if move.pieceCaptured == '--':
                    self.fifty_move_rule_counter += 1
                else:
                    self.fifty_move_rule_counter = 0
            else:
                self.fifty_move_rule_counter = 0

            self.counter_list_storage.append([self.white_threefold_counter, self.black_threefold_counter, self.fifty_move_rule_counter])

    def draw_text_on_screen(self, screen):
        """
        Draw end game text on the screen (checkmate, stalemate, three fold rule, fifty move rule).
        :param screen:
        :return:
        """
        text = None

        # draw text if checkmate or stalemate
        if self.game_state.checkMate:
            text = self.json_parser.get_by_key('DRAW_TEXT', 'BLACK_CHECKMATE') if self.game_state.whiteToMove else self.json_parser.get_by_key('DRAW_TEXT', 'WHITE_CHECKMATE')

        elif self.game_state.staleMate:
            text = self.json_parser.get_by_key('DRAW_TEXT', 'STALEMATE')

        # check if it is threefold rule
        elif self.white_threefold_counter > 2 or self.black_threefold_counter > 2:
            text = self.json_parser.get_by_key('DRAW_TEXT', 'THREEFOLD_RULE')

        # check for fifty move rule
        elif self.fifty_move_rule_counter > 100:
            text = self.json_parser.get_by_key('DRAW_TEXT', 'FIFTY_MOVE_RULE')

        if text is not None:
            self.game_state.game_over = True
            GUI.GUI().draw_text(screen, text)

    def game(self, settings):
        """
        The main driver for the code. This will handle user input and update the graphics.
        :return:
        """

        self.it.start()  # start thread

        clock = p.time.Clock()
        screen = p.display.set_mode((self.json_parser.get_by_key('BOARD_WIDTH') + self.json_parser.get_by_key('MOVE_LOG_PANEL_WIDTH'),
                                     self.json_parser.get_by_key('BOARD_HEIGHT') + self.json_parser.get_by_key('MOVE_INFORMATION_HEIGHT') + self.json_parser.get_by_key(
                                         'CONSOLE_HEIGHT')))

        self.load_images()  # do this only once, before the while loop

        move_log_rectangle = self.create_move_log_rectangle()  # get notation rectangle
        move_information_rectangle = self.create_move_information_rectangle()  # get console information rectangle

        move_log_font = p.font.SysFont(self.json_parser.get_by_key('MOVE_LOG_FONT', 'FONT'), self.json_parser.get_by_key('MOVE_LOG_FONT', 'SIZE'), False, False)

        if settings['PIECE_COLOR'] == "w":
            self.game_state.player_one = True
            self.game_state.player_turn = True
        elif settings['PIECE_COLOR'] == "b":
            self.game_state.player_two = True
            self.game_state.player_turn = False

        move_made = animate = undo = False  # flags

        while True:
            self.draw_game_state(screen, move_log_font, settings)
            self.draw_text_on_screen(screen)
            clock.tick(self.json_parser.get_by_key('MAX_FPS'))  # refresh screen frame rate
            p.display.flip()  # draw the game

            for event in p.event.get():
                if event.type == p.QUIT:  # command to exit the game
                    p.quit()
                    sys.exit()

                elif event.type == p.MOUSEBUTTONDOWN:
                    if move_log_rectangle.collidepoint(p.mouse.get_pos()):
                        scroll_panel_height = self.json_parser.get_by_key('BOARD_HEIGHT') - self.notation_text_height - 100
                        self.notation_scroll_y = self.scroll(event, self.notation_scroll_y, scroll_panel_height, self.notation_text_height)

                    elif move_information_rectangle.collidepoint(p.mouse.get_pos()):
                        scroll_panel_height = self.json_parser.get_by_key('MOVE_INFORMATION_HEIGHT') - self.console_text_height - 50
                        self.console_scroll_y = self.scroll(event, self.console_scroll_y, scroll_panel_height, self.console_text_height)

                elif event.type == p.KEYDOWN:
                    if event.key == p.K_BACKSPACE:
                        self.user_text = self.user_text[:-1]

                    elif event.key == p.K_v and p.key.get_mods() & p.KMOD_CTRL:
                        self.user_text = Tk().clipboard_get()

                    elif event.key == p.K_RETURN:
                        move_made, animate = self.move_logic(move_made, animate)  # move logic

                        if self.it.input_command == self.json_parser.get_by_key('COMMANDS', 'UNDO') and not self.game_state.game_over:
                            self.undo_logic()
                            move_made = animate = undo = False
                            self.it.input_command = self.it.move_from = self.it.move_to = None
                            self.valid_moves = self.game_state.get_valid_moves()  # generate new valid_moves

                        if self.user_text == 'exit':
                            sys.exit()

                        self.user_text = ""
                        if not self.it.select_square:
                            self.move_console_text()

                    else:
                        if len(self.user_text) != 50:
                            self.user_text += event.unicode

            # AI move logic
            if not game_state.game_over and not self.game_state.player_turn:
                self.ai_move_logic()
                move_made = animate = True

            # logic when move has been made
            if move_made:
                # For piece move animation
                if animate:
                    self.move_animation(self.game_state.moveLog[-1], screen, self.game_state.board, clock, settings)

                self.move_made_logic(undo)
                move_made = animate = undo = False
                self.game_state.player_turn = not self.game_state.player_turn
                self.it.input_command = self.it.move_from = self.it.move_to = None

                self.valid_moves = self.game_state.get_valid_moves()  # generate new valid_moves

    @staticmethod
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

    def game_audio(self, move, settings):
        """
        Audio function for playing move, capture and check sounds.
        :param move:
        :param settings:
        :return:
        """
        if self.game_state.in_check():
            sound = p.mixer.Sound(self.json_parser.get_by_key('AUDIO', 'CHECK'))  # check
        elif move.isCastleMove:
            sound = p.mixer.Sound(self.json_parser.get_by_key('AUDIO', 'CASTLE'))  # castle
        elif move.pieceCaptured != "--":
            sound = p.mixer.Sound(self.json_parser.get_by_key('AUDIO', 'CAPTURE'))  # capture
        else:
            sound = p.mixer.Sound(self.json_parser.get_by_key('AUDIO', 'MOVE'))  # move

        sound.set_volume(self.set_volume(settings['SOUND'], self.json_parser.get_by_key('AUDIO')))  # read default settings from list
        sound.play()

    def castle_move_logic_animation(self, frame, frame_count, rock_piece, rock_start_end_row, rock_start_col, rock_move_col, rock_end_col, is_short):
        """
        Logic behind animating castle move. Creates smooth piece sliding for top piece.
        :param frame:
        :param frame_count:
        :param rock_piece:
        :param rock_start_end_row:
        :param rock_start_col:
        :param rock_move_col:
        :param rock_end_col:
        :param is_short:
        :return:
        """
        if is_short:
            rock_row, rock_col = (rock_start_end_row - 0 * frame / frame_count, rock_start_col - rock_move_col * frame / frame_count)
        else:
            rock_row, rock_col = (rock_start_end_row - 0 * frame / frame_count, rock_start_col + rock_move_col * frame / frame_count)

        rock_end_square = p.Rect(rock_end_col * self.SQ_SIZE, rock_start_end_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
        castle_color = self.board_colors[(rock_start_end_row + rock_end_col) % 2]

        return rock_piece, rock_row, rock_col, castle_color, rock_end_square

    def castle_move_animation(self, move, delta_col, frame, frame_count):
        """
        Method for animating castle move.
        :param move:
        :param delta_col:
        :param frame:
        :param frame_count:
        :return:
        """
        # white castling
        if move.startRow == 7:
            rock_piece = self.json_parser.get_by_key('PIECES', 'WR')

            # king side castle
            if delta_col == 2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 7, 7, 2, 5, is_short=True)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

            # queen side castle
            elif delta_col == -2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 7, 0, 3, 3, is_short=False)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

        # black castling
        elif move.startRow == 0:
            rock_piece = self.json_parser.get_by_key('PIECES', 'BR')

            # black king side castle
            if delta_col == 2:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 0, 7, 2, 5, is_short=True)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

            elif delta_col == -2:  # black queen side castle
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_logic_animation(frame, frame_count, rock_piece, 0, 0, 3, 3, is_short=False)
                return rock_piece, rock_row, rock_col, castle_color, rock_end_square

    def move_animation(self, move, screen, board, clock, settings):
        """
        Method for animating a move on the chess board.
        :param move:
        :param screen:
        :param board:
        :param clock:
        :param settings:
        :return:
        """
        delta_row = move.endRow - move.startRow
        delta_col = move.endCol - move.startCol
        frames_per_square = self.json_parser.get_by_key('FRAMES_PER_SQUARE')  # frames to move one square
        frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

        for frame in range(frame_count + 1):
            row, col = (move.startRow + delta_row * frame / frame_count, move.startCol + delta_col * frame / frame_count)
            rock_row = rock_col = castle_color = rock_end_square = rock_piece = None  # for assignments before reference

            # animation castle move
            if move.isCastleMove:
                rock_piece, rock_row, rock_col, castle_color, rock_end_square = self.castle_move_animation(move, delta_col, frame, frame_count)

            # redraw
            self.draw_board(screen)
            self.draw_pieces(screen, board)
            self.draw_coordinates(screen)

            # erase rock piece after redraw
            if move.isCastleMove:
                p.draw.rect(screen, castle_color, rock_end_square)

            # erase the piece moved from it's ending square
            color = self.board_colors[(move.endRow + move.endCol) % 2]
            end_square = p.Rect(move.endCol * self.SQ_SIZE, move.endRow * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
            p.draw.rect(screen, color, end_square)
            # draw captured piece onto rectangle
            if move.pieceCaptured != "--":
                if move.isEnPassantMove:  # if is en passant move make en passant row where it happened
                    en_passant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                    end_square = p.Rect(move.endCol * self.SQ_SIZE, en_passant_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)

                screen.blit(self.IMAGES[move.pieceCaptured], end_square)

            # draw moving piece
            screen.blit(self.IMAGES[move.pieceMoved], p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

            # draw rock piece after castling
            if move.isCastleMove:
                screen.blit(self.IMAGES[rock_piece], p.Rect(rock_col * self.SQ_SIZE, rock_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

            p.display.flip()
            clock.tick(self.json_parser.get_by_key('MAX_FPS'))

        # call audio function after animation
        self.game_audio(move, settings)
