import threading
import Move
import ChessMain
from JsonParser import JsonParser
from textx import metamodel_from_file, TextXError
from termcolor import colored
from Utils import Utils


class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread, self).__init__()
        self.daemon = True  # for exiting on X, don't delete
        self.input_command = None
        self.move_from = None
        self.move_to = None
        self.rowsToRanks = {v: k for v, k in Move.Move.ranksToRows.items()}
        self.colsToFiles = {v: k for v, k in Move.Move.filesToCols.items()}
        self.enter = False
        self.disambiguating_moves = False
        self.disambiguating_moves_list = []
        self.file = "settings.json"
        self.json_parser = JsonParser(self.file)
        self.information = {}
        self.select_square = False

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

    def add_to_information_dict(self, text, color):
        """
        Method for adding into dictionary where key is text and value is color. This method is used for text outputs into console.
        :param text:
        :param color:
        :return:
        """
        key = len(self.information)
        self.information[key] = [text, color]

        return self.information

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

    def handler_commands(self, chess_model, game_state):
        """
        Read user input and determine which handler command is called and determine what kind of print_text() function should be called.
        :param chess_model: textx model
        :param game_state: current game state
        :return: command name as last user input so GameState can work with it
        """
        command = chess_model.commands[0].handler
        game_command = Utils().get_game_command(command)
        pr_command, undo_print, castle_used_print = Utils().print_command(game_state, command)

        if game_command == 'undo':
            if game_state.game_over:
                pass
            elif len(game_state.moveLog) != 0:
                self.print_text(pr_command, self.input_command, "dodgerblue")
            else:
                self.print_text(pr_command, self.input_command + "' - " + undo_print, "gold")

        elif game_command == 'castling short' or game_command == 'castling long':
            if castle_used_print is None:
                self.print_text(pr_command, self.input_command, "dodgerblue")
            else:
                self.print_text(pr_command, castle_used_print, "gold")

        elif game_command == 'restart' or game_command == 'new' or game_command == 'exit':
            self.print_text(pr_command, self.input_command, "dodgerblue")

        self.input_command = game_command
        return self.input_command

    def move_command(self, chess_model, game_state, valid_moves):
        """
        Method for generating move_from, move_to and possible multiple moves based from user inputs. Inputs can be in two ways:
            1. "piece type" "move to" (pawn e4)
            2. "piece type" "move from" "move to" (rock a5) - used in cases where multiple same piece types can move to the same square
        :param chess_model:
        :param game_state:
        :param valid_moves:
        :return:
        """
        piece = Utils().piece_name(game_state, chess_model.commands[0].piece)
        input_split = self.input_command.split(' ')
        self.disambiguating_moves = False
        self.select_square = False
        nbr_of_multi_moves = 0

        # if user input is in form of "piece move to" (pawn e4)
        if len(input_split) == 2:
            self.move_to = chess_model.commands[0].move_from.col + str(chess_model.commands[0].move_from.row)
            self.move_to = tuple(map(int, self.input_notation(self.move_to)))

            # searching through the board for provided move
            for row in range(8):
                for col in range(8):
                    if game_state.board[row][col] == piece:
                        move = Move.Move((row, col), self.move_to, game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                self.move_from = (row, col)
                                nbr_of_multi_moves += 1
                                # TODO multiple moves chess notation
                                break

            # in case multiple same pieces can go to that square
            if nbr_of_multi_moves > 1:
                self.move_from = None
                self.disambiguating_moves = True

            # in case user wants only to select the piece
            if game_state.board[self.move_to[0]][self.move_to[1]] == piece:
                self.move_from = self.move_to
                self.select_square = True

        # if user input is in form of "piece move from move to" (rock a1 a5)
        elif len(input_split) == 3:
            self.move_from = chess_model.commands[0].move_from.col + str(chess_model.commands[0].move_from.row)
            self.move_to = chess_model.commands[0].move_to.col + str(chess_model.commands[0].move_to.row)
            self.move_from = tuple(map(int, self.input_notation(self.move_from)))
            self.move_to = tuple(map(int, self.input_notation(self.move_to)))
            self.disambiguating_moves_list = []

            for row in range(8):
                for col in range(8):
                    if game_state.board[row][col] == piece:
                        move = Move.Move((row, col), self.move_to, game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                nbr_of_multi_moves += 1
                                self.disambiguating_moves_list.append((row, col))
                                break

            if nbr_of_multi_moves > 1:
                game_state.multiple_moves = True

        else:
            return

        if not self.disambiguating_moves:
            if self.move_from != self.move_to:
                move = Move.Move(self.move_from, self.move_to, game_state.board)
                for i in range(len(valid_moves)):
                    if move == valid_moves[i]:
                        print(colored(">>> OK", "green"))
                        self.add_to_information_dict("MOVE: " + self.input_command.lower() + " >>> OK", "olivedrab3")
                        break

                if move not in valid_moves:
                    print(colored(">>> Info: That move is not in the list of valid moves.", "yellow"))
                    self.add_to_information_dict(">>> Info: That move is not in the list of valid moves.", "gold")

        else:
            print(colored(">>> Info: Possible multiple moves for: " + self.input_command, "yellow"))
            self.add_to_information_dict(">>> Info: Possible multiple moves for: " + self.input_command, "gold")

    def run(self):
        """
        User input function. Contains two parts.
        First part handles with user handler commands such as undo, castling (short and long), new game, restart and exit.
        Second part handles piece movement.
        :return: True or False depending if the thread is alive or not
        """
        chess_mm = metamodel_from_file('textX/chess_rules.tx', ignore_case=True)
        while True:
            try:
                game_state = ChessMain.ChessMain().game_state
                if self.enter:
                    self.move_from = self.move_to = None
                    self.enter = False

                    exec(self.input_command, globals())

                    input_command_split = self.input_command.split("'")
                    self.input_command = input_command_split[1]

                    chess_model = chess_mm.model_from_str(self.input_command)
                    valid_moves = ChessMain.ChessMain().valid_moves

                    if hasattr(chess_model.commands[0], "handler"):
                        self.handler_commands(chess_model, game_state)
                    else:
                        self.move_command(chess_model, game_state, valid_moves)
                        print(self.move_from)
            except TypeError:
                if self.move_to is None:
                    print(colored(">>> TypeError: an invalid reference was made!", "red"))
                    self.add_to_information_dict("TypeError: an invalid reference was made! -- " + self.input_command.lower(), "brown1")
                else:
                    print(colored(">>> Info: That move is not in the list of valid moves.", "yellow"))
                    self.add_to_information_dict(">>> Info: That move is not in the list of valid moves.", "gold")

            except AttributeError:
                print(colored(">>> AttributeError: invalid attribute!", "red"))
                self.add_to_information_dict("AttributeError: invalid attribute! -- " + self.input_command.lower(), "brown1")

            except TextXError:
                print(colored(">>> textXError: error while parsing string!", "red"))
                self.add_to_information_dict("textXError: error while parsing input! -- " + self.input_command.lower(), "brown1")
