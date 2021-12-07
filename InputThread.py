# define a thread which takes user input
import threading
import time

from termcolor import colored
from textx import metamodel_from_file, TextXError

import ChessMain
import Utils
import Move


class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread, self).__init__()
        self.daemon = True  # for exiting on X, don't delete
        self.last_user_input = None
        self.move_from = None
        self.move_to = None
        self.rowsToRanks = {v: k for v, k in Move.Move.ranksToRows.items()}
        self.colsToFiles = {v: k for v, k in Move.Move.filesToCols.items()}
        self.multiple_moves = False
        self.information = {}

    def print_text(self, command, print_command, color):
        """
        Print function for console writing.
        :param command:
        :param print_command:
        :param color:
        :return:
        """
        color_print = None
        if color == "gold":
            color_print = "yellow"
        elif color == "dodgerblue":
            color_print = "blue"

        print(colored(">>> " + command.upper() + ": '" + print_command.upper() + "'", color_print))
        self.add_to_information_dict(command.upper() + ": '" + print_command.upper(), color)

    def input_notation(self, coordination):
        """
        Transferring user input chess notation into tuple which engine can understand.
        :param coordination: user intuitive coordination of the piece (ex. d1)
        :return: tuple of provided coordination converted to col and row
        """
        try:
            if len(list(coordination)) == 2:
                col = str(self.colsToFiles[list(coordination)[0]])
                row = str(self.rowsToRanks[list(coordination)[1]])
                engine_notation = (row, col)
                return engine_notation
        except KeyError:
            pass

    def handler_commands(self, chess_model, game_state):
        """
        Read user input and determine which handler command is called and determine what kind of print_text() function should be called.
        :param chess_model: textx model
        :param game_state: current game state
        :return: command name as last user input so GameState can work with it
        """
        command = chess_model.commands[0].handler
        game_command = Utils.get_game_command(command)
        pr_command, undo_print, castle_used_print = Utils.print_command(game_state, command)

        if game_command == 'undo':
            if game_state.game_over:
                pass
            elif len(game_state.moveLog) != 0:
                self.print_text(pr_command, self.last_user_input, "dodgerblue")
            else:
                self.print_text(pr_command, self.last_user_input + "' - " + undo_print, "gold")

        elif game_command == 'castling short' or game_command == 'castling long':
            if not game_state.castleUsed:
                self.print_text(pr_command, self.last_user_input, "dodgerblue")
            else:
                self.print_text(pr_command, castle_used_print, "gold")

        elif game_command == 'restart' or game_command == 'new' or game_command == 'exit':
            self.print_text(pr_command, self.last_user_input, "dodgerblue")

        self.last_user_input = game_command
        return self.last_user_input

    def move_command(self, chess_model, game_state, valid_moves):
        piece = Utils.piece_name(chess_model.commands[0].piece)
        input_split = self.last_user_input.split(' ')
        move_from = None
        nbr_of_multi_moves = 0
        self.multiple_moves = False

        if len(input_split) == 2:
            move_to = chess_model.commands[0].move_from.col + str(chess_model.commands[0].move_from.row)
            move_to = tuple(map(int, self.input_notation(move_to)))

            for row in range(8):
                for col in range(8):
                    if game_state.board[row][col] == piece:
                        move = Move.Move((row, col), move_to, game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                move_from = (row, col)
                                nbr_of_multi_moves += 1
                                break

            if nbr_of_multi_moves > 1:
                move_from = None
                self.multiple_moves = True

            if game_state.board[move_to[0]][move_to[1]] == piece:
                move_from = move_to

        elif len(input_split) == 3:
            move_from = chess_model.commands[0].move_from.col + str(chess_model.commands[0].move_from.row)
            move_to = chess_model.commands[0].move_to.col + str(chess_model.commands[0].move_to.row)
            move_from = tuple(map(int, self.input_notation(move_from)))
            move_to = tuple(map(int, self.input_notation(move_to)))

            for row in range(8):
                for col in range(8):
                    if game_state.board[row][col] == piece:
                        move = Move.Move((row, col), move_to, game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                nbr_of_multi_moves += 1
                                break

            if nbr_of_multi_moves > 1:
                game_state.multiple_moves = True

        else:
            return

        if not self.multiple_moves:
            if move_from != move_to:
                self.move_from = move_from
                self.move_to = move_to
                move = Move.Move(move_from, move_to, game_state.board)
                for i in range(len(valid_moves)):
                    if move == valid_moves[i]:
                        print(colored(">>> OK", "green"))
                        self.add_to_information_dict("MOVE: " + ChessMain.user_text.lower() + " >>> OK", "olivedrab3")
                        break

                if move not in valid_moves:
                    print(colored(">>> Info: That move is not in the list of valid moves.", "yellow"))
                    self.add_to_information_dict(">>> Info: That move is not in the list of valid moves.", "gold")

        else:
            print(colored(">>> Info: Possible multiple moves for: " + self.last_user_input, "yellow"))
            self.add_to_information_dict(">>> Info: Possible multiple moves for: " + self.last_user_input, "gold")

        return move_from, move_to

    def add_to_information_dict(self, text, color):
        key = len(self.information)
        self.information[key] = [text, color]

        return self.information

    def run(self):
        """
        User input function. Contains two parts.
        First part handles with user handler commands such as undo, castling (short and long), new game, restart and exit.
        Second part handles piece movement.
        :return: True or False depending if the thread is alive or not
        """
        time.sleep(1)  # so ChessMain thread manages to create on time
        chess_mm = metamodel_from_file('textX/chess.tx', ignore_case=True)
        while True:
            try:
                game_state = ChessMain.game_state
                if game_state.isEnter:
                    self.move_from = None
                    self.move_to = None

                    game_state.isEnter = False
                    exec(self.last_user_input, globals())

                    input_split = self.last_user_input.split("'")
                    self.last_user_input = input_split[1]

                    valid_moves = ChessMain.valid_moves

                    chess_model = chess_mm.model_from_str(self.last_user_input)
                    if hasattr(chess_model.commands[0], "handler"):
                        self.last_user_input = self.handler_commands(chess_model, game_state)
                    else:
                        move_from, move_to = self.move_command(chess_model, game_state, valid_moves)

                        if move_from is not None:
                            self.move_from = move_from
                            self.move_to = move_to
            except TypeError:
                if self.move_to is None:
                    print(colored(">>> TypeError: an invalid reference was made!", "red"))
                    self.add_to_information_dict("TypeError: an invalid reference was made! -- " + ChessMain.user_text, "brown1")
                else:
                    print(colored(">>> Info: That move is not in the list of valid moves.", "yellow"))
                    self.add_to_information_dict(">>> Info: That move is not in the list of valid moves.", "gold")

            except AttributeError:
                print(colored(">>> AttributeError: invalid attribute!", "red"))
                self.add_to_information_dict("AttributeError: invalid attribute! -- " + ChessMain.user_text, "brown1")
            except TextXError:
                print(colored(">>> textXError: error while parsing string!", "red"))
                self.add_to_information_dict("textXError: error while parsing input! -- " + ChessMain.user_text, "brown1")
