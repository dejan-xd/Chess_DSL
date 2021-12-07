"""
This is main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""
import sys
import time

import pygame as p

import ChessAI
import GUI
import GameState
import InputThread
import Json
import Move
from tkinter import Tk

json_data = Json.read_from_json()  # global parameter that contains values from settings.json JSON file.
game_state = GameState.GameState()
valid_moves = game_state.get_valid_moves()

it = InputThread.InputThread()  # for user inputs
it.start()  # start user inputs thread

SQ_SIZE = json_data['BOARD_HEIGHT'] // json_data['DIMENSION']
board_colors = [p.Color(json_data['BOARD_COLORS']['WHITE']), p.Color(json_data['BOARD_COLORS']['BLACK'])]
user_text = ""  # for console

IMAGES = {}
move_list = []  # for highlighting last move made
move_log = []  # contains copy of game_state.moveLog
removing_ambiguity_list = []

notation_scroll_y = notation_text_height = 0  # for scrolling notation text
console_scroll_y = console_text_height = 0  # for scrolling console text


def load_images():
    """
    Initialize a global dictionary of chess images. This will be called exactly once in the main.
    :return:
    """
    pieces = json_data['PIECES']
    for key, value in pieces.items():
        IMAGES[value] = p.transform.scale(p.image.load("images/" + value + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image with 'IMAGES['wp']'


def game(settings):
    """
    The main driver for the code. This will handle user input and update the graphics.
    :return:
    """
    global game_state, valid_moves, user_text, notation_scroll_y, console_scroll_y
    clock = p.time.Clock()
    screen = p.display.set_mode((json_data['BOARD_WIDTH'] + json_data['MOVE_LOG_PANEL_WIDTH'],
                                 json_data['BOARD_HEIGHT'] + json_data['MOVE_INFORMATION_HEIGHT'] + json_data['CONSOLE_HEIGHT']))
    move_log_font = p.font.SysFont(json_data['MOVE_LOG_FONT']['FONT'], json_data['MOVE_LOG_FONT']['SIZE'], False, False)

    load_images()  # do this only once, before the while loop

    if settings['PIECE_COLOR'] == "w":
        game_state.player_one = True
    elif settings['PIECE_COLOR'] == "b":
        game_state.player_two = True

    move_from = move_to = None  # no square is selected, keep track of the last move of the user (tuple: (row, col))
    ai_move = []  # keep track of AI moves (two tuples: [(6,4), (4,4)])
    threefold_list = []  # keep track of all moves so we can check if threefold happened
    counter_list_storage = []  # store all counters in list
    move_made = animate = undo = False  # flags
    white_threefold_counter = black_threefold_counter = fifty_move_rule_counter = 0  # counter for threefold moves and fifty move draw rule

    move_log_rectangle = create_move_log_rectangle()  # get notation rectangle
    move_information_rectangle = create_move_information_rectangle()  # get console information rectangle

    while True:
        draw_game_state(screen, move_from, move_to, move_log_font, settings)
        draw_text_on_screen(screen, white_threefold_counter, black_threefold_counter, fifty_move_rule_counter)
        clock.tick(json_data['MAX_FPS'])  # refresh screen frame rate
        p.display.flip()  # draw the game

        human_turn = game_state.is_human_turn()
        game_state.isEnter = False

        for event in p.event.get():
            if event.type == p.QUIT:  # command to exit the game
                p.quit()
                sys.exit()

            elif event.type == p.MOUSEBUTTONDOWN:
                if move_log_rectangle.collidepoint(p.mouse.get_pos()):
                    scroll_panel_height = json_data['BOARD_HEIGHT'] - notation_text_height - 100
                    notation_scroll_y = scroll(event, notation_scroll_y, scroll_panel_height, notation_text_height)

                elif move_information_rectangle.collidepoint(p.mouse.get_pos()):
                    scroll_panel_height = json_data['MOVE_INFORMATION_HEIGHT'] - console_text_height - 50
                    console_scroll_y = scroll(event, console_scroll_y, scroll_panel_height, console_text_height)

            elif event.type == p.KEYDOWN:
                if event.key == p.K_BACKSPACE:
                    user_text = user_text[:-1]  # remove last char from input

                elif event.key == p.K_ESCAPE:
                    move_from = move_to = None

                elif event.key == p.K_v and p.key.get_mods() & p.KMOD_CTRL:
                    user_text = Tk().clipboard_get()

                elif event.key == p.K_RETURN:
                    move_from, move_to, move_made, animate = move_logic(move_from, move_to, move_made, animate, human_turn)  # move logic

                    scroll_panel_height_console = json_data['MOVE_INFORMATION_HEIGHT'] - console_text_height
                    if game_state.whiteToMove and scroll_panel_height_console < 20:
                        console_scroll_y -= 18

                    if it.last_user_input == json_data['COMMANDS']['UNDO'] and not game_state.game_over:
                        white_threefold_counter, black_threefold_counter, fifty_move_rule_counter = undo_logic(threefold_list, counter_list_storage)
                        undo = move_made = True
                        animate = False
                        it.last_user_input = it.move_from = it.move_to = None
                        counter_list_storage.append([white_threefold_counter, black_threefold_counter, fifty_move_rule_counter])

                    elif it.last_user_input == json_data['COMMANDS']['RESTART']:
                        restart_logic(settings)

                    elif it.last_user_input == json_data['COMMANDS']['NEW_GAME']:
                        new_game_logic(settings)

                    elif it.last_user_input == 'exit':
                        sys.exit()

                else:
                    if len(user_text) != 50:
                        user_text += event.unicode

        # AI move logic
        if not game_state.game_over and not human_turn:
            ai_move_logic(ai_move)
            move_made = animate = True
            move_from = None
            ai_move = []

        # logic when move has been made
        if move_made:
            if animate:  # for piece move animation
                animate_move(game_state.moveLog[-1], screen, game_state.board, clock, settings)

            threefold_list, black_threefold_counter, white_threefold_counter, fifty_move_rule_counter, counter_list_storage = move_made_logic(
                undo, threefold_list, black_threefold_counter, white_threefold_counter, fifty_move_rule_counter, counter_list_storage)

            move_made = animate = undo = False
            it.last_user_input = it.move_from = it.move_to = None
            valid_moves = game_state.get_valid_moves()  # generate new valid_moves

            scroll_panel_height_notation = json_data['BOARD_HEIGHT'] - notation_text_height
            if not game_state.whiteToMove and scroll_panel_height_notation < 50:
                notation_scroll_y -= 18

            scroll_panel_height_console = json_data['MOVE_INFORMATION_HEIGHT'] - console_text_height
            if not game_state.whiteToMove and scroll_panel_height_console < 20:
                console_scroll_y -= 18

            game_state.move_made = False


def draw_game_state(screen, move_from, move_to, move_log_font, settings):
    """
    Responsible for all the graphics within a current game state.
    :param screen:
    :param move_from:
    :param move_to:
    :param move_log_font:
    :param settings:
    :return:
    """
    draw_board(screen)  # draw squares on the board
    highlight_squares(screen, move_from, move_to)  # highlight squares
    draw_pieces(screen, game_state.board)  # draw pieces on top of squares
    draw_coordinates(screen)  # draw coordinates on board
    draw_move_information(screen, move_log_font)  # draw move information
    draw_console(screen, move_log_font)  # draw console for inputs
    draw_move_log(screen, move_log_font, settings)  # draw move log for chess notations


def draw_board(screen):
    """
    Draw the squares on the board. The top left square is always white.
    :param screen:
    :return:
    """
    global board_colors
    for row in range(json_data['DIMENSION']):
        for col in range(json_data['DIMENSION']):
            color = board_colors[((row + col) % 2)]  # pick color
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_coordinates(screen):
    """
    Draw the square coordinates on the chess board.
    :param screen:
    :return:
    """
    row_list = json_data['BOARD_COORDINATES']['ROWS']
    col_list = json_data['BOARD_COORDINATES']['COLUMNS']
    font = p.font.SysFont(json_data['BOARD_COORDINATES']['FONT'], json_data['BOARD_COORDINATES']['SIZE'], False, False)
    for row in row_list:
        for col in col_list:
            text_object = font.render(" " + row + col, False, p.Color(json_data['BOARD_COORDINATES']['COLOR']))
            text_location = p.Rect(row_list.index(row) * SQ_SIZE, col_list.index(col) * SQ_SIZE, json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT'])
            screen.blit(text_object, text_location)


def draw_pieces(screen, board):
    """
    Draw the pieces on the board using the current GameState.board.
    :param screen:
    :param board:
    :return:
    """
    for row in range(json_data['DIMENSION']):
        for col in range(json_data['DIMENSION']):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
        scroll_y = min(scroll_y + 18, 0)

    elif event.button == 5:
        if text_height > scroll_panel_height:
            while not scroll_panel_height % 18 == 0:
                scroll_panel_height += 1
            scroll_y = max(scroll_y - 18, scroll_panel_height)

    return scroll_y


def move_logic(move_from, move_to, move_made, animate, human_turn):
    """
    Logic for pasting/reading the move from game console and executing player's move.
    :param move_from:
    :param move_to:
    :param move_made:
    :param animate:
    :param human_turn:
    :return:
    """
    global user_text
    game_state.isEnter = True
    it.last_user_input = "print('" + user_text.lower() + "')"
    time.sleep(0.1)  # wait for another thread to get all information

    if not game_state.game_over and human_turn:
        move_from, move_to, is_castle = castling_move_logic()

        if move_from is not None and move_to is not None:
            move = Move.Move(move_from, move_to, game_state.board)
            for i in range(len(valid_moves)):  # list of moves generated by the chess engine
                if move == valid_moves[i]:
                    game_state.make_move(valid_moves[i])
                    move_log.append(move)
                    move_list.append([move_from, move_to])  # append start and end move square
                    move_made = animate = True
            if not move_made and is_castle:
                key = len(it.information) - 1
                it.information[key] = [it.information[key][0] + " >>> ERROR", "brown1"]

    user_text = ""
    return move_from, move_to, move_made, animate


def castling_move_logic():
    """
    Checking if the move was castling move first. If not return move_from and move_to so the move can be made.
    :return:
    """
    is_castle = False
    if it.last_user_input == json_data['COMMANDS']['CASTLE_SHORT']:
        if game_state.whiteToMove:
            move_from = game_state.whiteKingLocation  # (7, 4)
            move_to = game_state.whiteKingCastleLocationKingSide  # (7, 6)
        else:
            move_from = game_state.blackKingLocation  # (0, 4)
            move_to = game_state.blackKingCastleLocationKingSide  # (0, 6)

        is_castle = True

    elif it.last_user_input == json_data['COMMANDS']['CASTLE_LONG']:
        if game_state.whiteToMove:
            move_from = game_state.whiteKingLocation  # (7, 4)
            move_to = game_state.whiteKingCastleLocationQueenSide  # (7, 2)
        else:
            move_from = game_state.blackKingLocation  # (0, 4)
            move_to = game_state.blackKingCastleLocationQueenSide  # (0, 2)

        is_castle = True

    else:
        move_from = it.move_from  # if it's any other move
        move_to = it.move_to

    return move_from, move_to, is_castle


def undo_logic(threefold_list, counter_list_storage):
    """
    Method for executing the undo move logic.
    :param threefold_list:
    :param counter_list_storage:
    :return:
    """
    for i in range(2):  # check twice for both human and AI move
        current_board = []
        game_state.undo_move(move_log)

        for board in game_state.board:
            current_board += ''.join(map(str, board))  # convert to string and store current board state
        if current_board in threefold_list:
            threefold_list.remove(current_board)
        if len(move_list) != 0:  # remove last two played moves from move list (both human's and AI move)
            move_list.pop()
        if len(move_log) != 0:
            move_log.pop()

    try:  # try catch block to prevent IndexError
        white_threefold_counter = counter_list_storage[-3][0]
        black_threefold_counter = counter_list_storage[-3][1]
        fifty_move_rule_counter = counter_list_storage[-3][2]
        del counter_list_storage[-2:]  # remove two last elements from counter_list_storage
    except IndexError:
        threefold_list.clear()
        counter_list_storage.clear()
        white_threefold_counter = black_threefold_counter = fifty_move_rule_counter = 0  # restart counter values

    return white_threefold_counter, black_threefold_counter, fifty_move_rule_counter


def restart_logic(settings):
    """
    Method for restarting the game.
    :param settings:
    :return:
    """
    global game_state, valid_moves, json_data, user_text
    json_data = Json.read_from_json()  # global parameter that contains values from settings.json JSON file.
    game_state = GameState.GameState()  # make new game_state
    valid_moves = game_state.get_valid_moves()  # generate new valid_moves
    move_list.clear()
    removing_ambiguity_list.clear()
    user_text = ""
    it.last_user_input = it.move_from = it.move_to = None  # restart console inputs
    game(settings)  # run game method


def new_game_logic(settings):
    """
    Logic for starting a new game. If the game is over take a note is was the winner.
    :param settings:
    :return:
    """
    if game_state.game_over:
        if game_state.checkMate:
            if not game_state.whiteToMove:
                settings['WHITE_WINS'] = float(settings['WHITE_WINS']) + 1  # white wins
            else:
                settings['BLACK_WINS'] = float(settings['BLACK_WINS']) + 1  # black wins
        else:
            settings['WHITE_WINS'] = float(settings['WHITE_WINS']) + 1 / 2  # 1/2 points for white
            settings['BLACK_WINS'] = float(settings['BLACK_WINS']) + 1 / 2  # 1/2 points for black

        json_data['SETTINGS'] = settings
        Json.write_to_json(json_data)

    restart_logic(settings)


def ai_move_logic(ai_move):
    """
    Logic for executing AI's move.
    :param ai_move:
    :return:
    """
    ai = ChessAI.find_best_move(game_state, valid_moves)  # find best move
    if ai is None:
        ai = ChessAI.find_random_move(valid_moves)
    game_state.make_move(ai)
    move_log.append(ai)
    move = game_state.moveLog[-1]  # take last move from move log so it can be used to find move_from and move_to square
    move_from = (move.startRow, move.startCol)
    move_to = (move.endRow, move.endCol)
    ai_move.extend([move_from, move_to])  # extend ai_move list with two tuples: move_from and move_to
    move_list.append(ai_move)  # append start and end move square


def move_made_logic(undo, threefold_list, black_threefold_counter, white_threefold_counter, fifty_move_rule_counter, counter_list_storage):
    """
    Logic if the move is made. Check if three fold or fifty move rule happened.
    :param undo:
    :param threefold_list:
    :param black_threefold_counter:
    :param white_threefold_counter:
    :param fifty_move_rule_counter:
    :param counter_list_storage:
    :return:
    """
    if not undo:
        current_board = []
        for board in game_state.board:
            current_board += ''.join(map(str, board))

        if current_board in threefold_list:  # if current board happened
            if game_state.whiteToMove:
                black_threefold_counter += 1
            else:
                white_threefold_counter += 1

            threefold_list.append(current_board)

        move = game_state.moveLog[-1]  # take last move from move log
        if move.pieceMoved[1] != 'p':  # check for fifty move draw rule
            if move.pieceCaptured == '--':
                fifty_move_rule_counter += 1
            else:
                fifty_move_rule_counter = 0
        else:
            fifty_move_rule_counter = 0

        counter_list_storage.append([white_threefold_counter, black_threefold_counter, fifty_move_rule_counter])

    return threefold_list, black_threefold_counter, white_threefold_counter, fifty_move_rule_counter, counter_list_storage


def draw_text_on_screen(screen, white_threefold_counter, black_threefold_counter, fifty_move_rule_counter):
    """
    Draw end game text on the screen (checkmate, stalemate, three fold rule, fifty move rule).
    :param screen:
    :param white_threefold_counter:
    :param black_threefold_counter:
    :param fifty_move_rule_counter:
    :return:
    """
    text = None

    if game_state.checkMate:  # draw text if checkmate or stalemate
        text = json_data['DRAW_TEXT']['BLACK_CHECKMATE'] if game_state.whiteToMove else json_data['DRAW_TEXT']['WHITE_CHECKMATE']

    elif game_state.staleMate:
        text = json_data['DRAW_TEXT']['STALEMATE']

    elif white_threefold_counter > 2 or black_threefold_counter > 2:  # check if it is threefold rule
        text = json_data['DRAW_TEXT']['THREEFOLD_RULE']

    elif fifty_move_rule_counter > 100:  # check for fifty move rule
        text = json_data['DRAW_TEXT']['FIFTY_MOVE_RULE']

    if text is not None:
        game_state.game_over = True
        GUI.draw_text(screen, text)


def draw_move_information(screen, font):
    """
    Method for drawing panel which will display move information.
    :param screen:
    :param font:
    :return:
    """
    global console_text_height
    console_panel = json_data['CONSOLE_PANEL']
    move_information_rectangle = create_move_information_rectangle()

    p.draw.rect(screen, p.Color(console_panel['PANEL_COLOR']), move_information_rectangle)
    p.draw.rect(screen, p.Color(console_panel['BORDER_COLOR']), move_information_rectangle, 1)

    text_y = 5

    for i in range(len(it.information)):
        text_position = console_scroll_y + text_y

        if text_position < 5:  # first row
            text_position = -1000  # remove from screen

        text_object = font.render(it.information[i][0], True, p.Color(it.information[i][1]))
        text_location = move_information_rectangle.move(5, text_position)
        screen.blit(text_object, text_location)

        text_y += text_object.get_height() + 5  # draw text one under another

    console_text_height = text_y


def create_move_information_rectangle():
    """
    Method for creating console information rectangle object.
    :return:
    """
    move_information_rectangle = p.Rect(0, json_data['BOARD_HEIGHT'], json_data['BOARD_WIDTH'] + json_data['MOVE_LOG_PANEL_WIDTH'], json_data['MOVE_INFORMATION_HEIGHT'])
    return move_information_rectangle


def draw_console(screen, font):
    """
    Logic for creating input console and handling input strings.
    :param screen:
    :param font:
    :return:
    """
    global user_text

    console_panel = json_data['CONSOLE_PANEL']
    console_rectangle = p.Rect(0, json_data['BOARD_HEIGHT'] + json_data['MOVE_INFORMATION_HEIGHT'],
                               json_data['BOARD_WIDTH'] + json_data['MOVE_LOG_PANEL_WIDTH'], json_data['CONSOLE_HEIGHT'])

    p.draw.rect(screen, p.Color(console_panel['PANEL_COLOR']), console_rectangle)
    p.draw.rect(screen, p.Color(console_panel['BORDER_COLOR']), console_rectangle, 1)

    text_object = font.render(">>> " + user_text, True, p.Color(console_panel['INPUT_TEXT_COLOR']))
    text_location = console_rectangle.move(5, 5)

    screen.blit(text_object, text_location)


def draw_move_log(screen, font, settings):
    """
    Draws the move log for chess notations.
    :param screen:
    :param font:
    :param settings:
    :return:
    """
    global notation_scroll_y, notation_text_height
    move_log_panel = json_data['MOVE_LOG_PANEL']
    move_log_rectangle = create_move_log_rectangle()

    move_log_panel_lines_and_text(screen, move_log_panel, move_log_rectangle, font, settings)
    create_chess_notation()

    notation_text = []
    for row in range(0, len(game_state.moveLog), 2):
        move_string = str(row // 2 + 1) + ". " + game_state.moveLog[row].notation + "\t"  # make move_string
        if row + 1 < len(game_state.moveLog):  # black made a move
            move_string += game_state.moveLog[row + 1].notation  # add black move to the move_string, example (1. d4 d5)
        notation_text.append(move_string)

    draw_text_move_log_panel(screen, move_log_panel, move_log_rectangle, font, notation_text)


def create_move_log_rectangle():
    """
    Method for creating move log rectangle object.
    :return:
    """
    move_log_rectangle = p.Rect(json_data['BOARD_WIDTH'], 0, json_data['MOVE_LOG_PANEL_WIDTH'], json_data['MOVE_LOG_PANEL_HEIGHT'])
    return move_log_rectangle


def move_log_panel_lines_and_text(screen, move_log_panel, move_log_rectangle, font, settings):
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

    p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (json_data['BOARD_WIDTH'], 17), (json_data['BOARD_WIDTH'] + json_data['MOVE_LOG_PANEL_WIDTH'], 17))
    p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (json_data['BOARD_WIDTH'], json_data['BOARD_HEIGHT'] - 15),
                (json_data['BOARD_WIDTH'] + json_data['MOVE_LOG_PANEL_WIDTH'], json_data['BOARD_HEIGHT'] - 15))
    p.draw.line(screen, p.Color(move_log_panel['LINE_COLOR']), (json_data['BOARD_WIDTH'] + (json_data['MOVE_LOG_PANEL_WIDTH'] / 2), 0),
                (json_data['BOARD_WIDTH'] + (json_data['MOVE_LOG_PANEL_WIDTH'] / 2), json_data['BOARD_HEIGHT']))

    text = "White\tBlack"
    text = text.replace('\t', ' ' * 30)
    text_object = font.render(text, True, p.Color(move_log_panel['FONT_COLOR']))
    text_location = move_log_rectangle.move((json_data['MOVE_LOG_PANEL_WIDTH'] - text_object.get_width()) / 2, 3)
    screen.blit(text_object, text_location)

    text = "White: " + str(settings['WHITE_WINS']) + "\tBlack: " + str(settings['BLACK_WINS'])
    text = text.replace('\t', ' ' * 20)
    text_object = font.render(text, True, p.Color(move_log_panel['FONT_COLOR']))
    text_location = move_log_rectangle.move((json_data['MOVE_LOG_PANEL_WIDTH'] - text_object.get_width()) / 2, json_data['BOARD_HEIGHT'] - text_object.get_height())
    screen.blit(text_object, text_location)


def create_chess_notation():
    """
    Method for editing notations for moves from move log. If the notation is None edit it. If the move is checkmate or check, edit it's notation.
    :return:
    """
    for i in range(0, len(game_state.moveLog)):
        if game_state.moveLog[i].notation is None:
            game_state.moveLog[i].notation = str(game_state.moveLog[i])

    if game_state.multiple_moves:
        game_state.multiple_moves = False
        start_square = game_state.moveLog[-1].colsToFiles[game_state.moveLog[-1].startCol] + game_state.moveLog[-1].rowsToRanks[game_state.moveLog[-1].startRow]
        game_state.moveLog[-1].notation = str(game_state.moveLog[-1])[:1] + start_square[0] + str(game_state.moveLog[-1])[1:]

    if game_state.checkMate:
        game_state.moveLog[-1].notation = str(game_state.moveLog[-1]) + json_data['CHESS_NOTATION']['CHECKMATE']

    elif game_state.in_check():
        game_state.moveLog[-1].notation = str(game_state.moveLog[-1]) + json_data['CHESS_NOTATION']['CHECK']


def draw_text_move_log_panel(screen, move_log_panel, move_log_rectangle, font, notation_text):
    """
    Method for drawing notation list on move log panel. Also contains logic for creating scroll up/down feature.
    :param screen:
    :param move_log_panel:
    :param move_log_rectangle:
    :param font:
    :param notation_text:
    :return:
    """
    global notation_scroll_y, notation_text_height
    text_positioning = move_log_panel['TEXT_POSITIONING']
    text_y = text_positioning['TEXT_HEIGHT_PADDING']

    for i in range(len(notation_text)):
        parts = notation_text[i].split("\t")  # split by tab
        text_position = text_y + notation_scroll_y

        if text_position < text_positioning['TEXT_HEIGHT_PADDING']:  # first row
            text_position = -1000  # remove from screen
        elif text_position > json_data['BOARD_HEIGHT'] - text_positioning['TEXT_HEIGHT_PADDING']:  # last row
            text_position = 1000  # remove from screen

        text_object = font.render(parts[0], True, p.Color(move_log_panel['FONT_COLOR']))  # white column
        text_location = move_log_rectangle.move(text_positioning['WHITE_WIDTH_PADDING'], text_position)
        screen.blit(text_object, text_location)

        text_object = font.render(parts[1], True, p.Color(move_log_panel['FONT_COLOR']))  # black column
        text_location = move_log_rectangle.move(text_positioning['BLACK_WIDTH_PADDING'], text_position)
        screen.blit(text_object, text_location)

        text_y += text_object.get_height() + text_positioning['LINE_SPACING']  # draw text one under another

    notation_text_height = text_y


def highlight_squares(screen, move_from, move_to):
    """
    Method for highlighting squares on the board.
    :param screen:
    :param move_from:
    :param move_to:
    :return:
    """
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    colors_palette = json_data['HIGHLIGHT_COLORS']

    # last move coloring
    if len(move_list) != 0:
        highlight_squares_move_colors(screen, s, colors_palette)

    # is check coloring
    if game_state.in_check():
        s.fill(p.Color(colors_palette['IN_CHECK']))
        if game_state.whiteToMove:
            screen.blit(s, (game_state.whiteKingLocation[1] * SQ_SIZE, game_state.whiteKingLocation[0] * SQ_SIZE))
        else:
            screen.blit(s, (game_state.blackKingLocation[1] * SQ_SIZE, game_state.blackKingLocation[0] * SQ_SIZE))

    # rest colorings
    if move_from == move_to and (move_from is not None or move_to is not None):
        highlight_squares_moves(screen, s, colors_palette, move_from)


def highlight_squares_move_colors(screen, surface, colors_palette):
    """
    Color last move squares to green.
    :param screen:
    :param surface:
    :param colors_palette:
    :return:
    """
    start_row, start_col = move_list[-1][0]
    end_row, end_col = move_list[-1][1]

    if (start_row + start_col) % 2 == 0:
        surface.fill(p.Color(colors_palette['LAST_MOVE_BRIGHT']))
    else:
        surface.fill(p.Color(colors_palette['LAST_MOVE_DARK']))

    if game_state.moveLog[-1].isCastleMove:
        surface.fill(p.Color(colors_palette['CASTLE']))
    screen.blit(surface, (start_col * SQ_SIZE, start_row * SQ_SIZE))

    if (end_row + end_col) % 2 == 0:
        surface.fill(p.Color(colors_palette['LAST_MOVE_BRIGHT']))
    else:
        surface.fill(p.Color(colors_palette['LAST_MOVE_DARK']))

    if game_state.moveLog[-1].isCastleMove:
        surface.fill(p.Color(colors_palette['CASTLE']))
    screen.blit(surface, (end_col * SQ_SIZE, end_row * SQ_SIZE))


def highlight_squares_moves(screen, s, colors_palette, move_from):
    """
    For the rest of square moves highlighting.
    :param screen:
    :param s:
    :param colors_palette:
    :param move_from:
    :return:
    """
    row, col = move_from

    if game_state.board[row][col][0] == ('w' if game_state.whiteToMove else 'b'):

        # selected square coloring
        if game_state.in_check() and move_from == game_state.whiteKingLocation:
            pass
        else:
            s.fill(p.Color(colors_palette['SELECTED_SQUARE']))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

        for move in valid_moves:
            if move.startRow == row and move.startCol == col:

                # possible moves from selected square
                if (move.endRow + move.endCol) % 2 == 0:
                    s.fill(p.Color(colors_palette['MOVE_TO_BRIGHT']))
                else:
                    s.fill(p.Color(colors_palette['MOVE_TO_DARK']))
                screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

                # possible captures coloring
                if game_state.board[move.endRow][move.endCol][0] == ('b' if game_state.whiteToMove else 'w') or move.isEnPassantMove:
                    if (move.endRow + move.endCol) % 2 == 0:
                        s.fill(p.Color(colors_palette['CAPTURE_BRIGHT']))
                    else:
                        s.fill(p.Color(colors_palette['CAPTURE_DARK']))
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def animate_move(move, screen, board, clock, settings):
    """
    Method for animating a move on the chess board.
    :param move:
    :param screen:
    :param board:
    :param clock:
    :param settings:
    :return:
    """
    global board_colors

    delta_row = move.endRow - move.startRow
    delta_col = move.endCol - move.startCol
    frames_per_square = json_data['FRAMES_PER_SQUARE']  # frames to move one square
    frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

    for frame in range(frame_count + 1):
        row, col = (move.startRow + delta_row * frame / frame_count, move.startCol + delta_col * frame / frame_count)
        rock_row = rock_col = castle_color = rock_end_square = rock_piece = None  # for assignments before reference

        # animation castle move
        if move.isCastleMove:
            rock_piece, rock_row, rock_col, castle_color, rock_end_square = animate_castle_move(move, delta_col, frame, frame_count)

        # redraw
        draw_board(screen)
        draw_pieces(screen, board)
        draw_coordinates(screen)

        # erase rock piece after redraw
        if move.isCastleMove:
            p.draw.rect(screen, castle_color, rock_end_square)

        # erase the piece moved from it's ending square
        color = board_colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)

        # draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.isEnPassantMove:  # if is en passant move make en passant row where it happened
                en_passant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                end_square = p.Rect(move.endCol * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.pieceCaptured], end_square)

        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.isCastleMove:  # draw rock piece after castling
            screen.blit(IMAGES[rock_piece], p.Rect(rock_col * SQ_SIZE, rock_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(json_data['MAX_FPS'])

    # call audio function after animation
    game_audio(move, settings)


def animate_castle_move(move, delta_col, frame, frame_count):
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
        rock_piece = json_data['PIECES']['WR']

        # king side castle
        if delta_col == 2:
            rock_piece, rock_row, rock_col, castle_color, rock_end_square = animate_castle_move_logic(frame, frame_count, rock_piece, 7, 7, 2, 5, is_short=True)
            return rock_piece, rock_row, rock_col, castle_color, rock_end_square

        # queen side castle
        elif delta_col == -2:
            rock_piece, rock_row, rock_col, castle_color, rock_end_square = animate_castle_move_logic(frame, frame_count, rock_piece, 7, 0, 3, 3, is_short=False)
            return rock_piece, rock_row, rock_col, castle_color, rock_end_square

    # black castling
    elif move.startRow == 0:
        rock_piece = json_data['PIECES']['BR']

        # black king side castle
        if delta_col == 2:
            rock_piece, rock_row, rock_col, castle_color, rock_end_square = animate_castle_move_logic(frame, frame_count, rock_piece, 0, 7, 2, 5, is_short=True)
            return rock_piece, rock_row, rock_col, castle_color, rock_end_square

        elif delta_col == -2:  # black queen side castle
            rock_piece, rock_row, rock_col, castle_color, rock_end_square = animate_castle_move_logic(frame, frame_count, rock_piece, 0, 0, 3, 3, is_short=False)
            return rock_piece, rock_row, rock_col, castle_color, rock_end_square


def animate_castle_move_logic(frame, frame_count, rock_piece, rock_start_end_row, rock_start_col, rock_move_col, rock_end_col, is_short):
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

    rock_end_square = p.Rect(rock_end_col * SQ_SIZE, rock_start_end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
    castle_color = board_colors[(rock_start_end_row + rock_end_col) % 2]

    return rock_piece, rock_row, rock_col, castle_color, rock_end_square


def game_audio(move, settings):
    """
    Audio function for playing move, capture and check sounds.
    :param move:
    :param settings:
    :return:
    """
    audio = json_data['AUDIO']
    if game_state.in_check():
        sound = p.mixer.Sound(audio['CHECK'])  # check
    elif move.isCastleMove:
        sound = p.mixer.Sound(audio['CASTLE'])  # castle
    elif move.pieceCaptured != "--":
        sound = p.mixer.Sound(audio['CAPTURE'])  # capture
    else:
        sound = p.mixer.Sound(audio['MOVE'])  # move

    sound.set_volume(set_volume(settings['SOUND'], audio))  # read default settings from list
    sound.play()


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
