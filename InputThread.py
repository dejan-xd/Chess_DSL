import threading
import Move
import ChessMain
from JsonParser import JsonParser
from textx import metamodel_from_file
from termcolor import colored


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
        self.multiple_moves = False
        self.json_parser = JsonParser()

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

    def piece_name(self, game_state, piece):
        """
        Method for creating English abbreviation name for each chess piece for each language.
        :param game_state:
        :param piece:
        :return:
        """
        if game_state.whiteToMove:
            PIECE_COLOR = 'w'
        else:
            PIECE_COLOR = 'b'

        if piece in self.json_parser.get_by_key('PION'):
            piece = PIECE_COLOR + 'p'

        elif piece in self.json_parser.get_by_key('KNIGHT'):
            piece = PIECE_COLOR + 'N'

        elif piece in self.json_parser.get_by_key('BISHOP'):
            piece = PIECE_COLOR + 'B'

        elif piece in self.json_parser.get_by_key('ROOK'):
            piece = PIECE_COLOR + 'R'

        elif piece in self.json_parser.get_by_key('QUEEN'):
            piece = PIECE_COLOR + 'Q'

        elif piece in self.json_parser.get_by_key('KING'):
            piece = PIECE_COLOR + 'K'

        return piece

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
        piece = self.piece_name(game_state, chess_model.commands[0].piece)
        input_split = self.input_command.split(' ')
        self.multiple_moves = False
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
                                break

            # in case multiple same pieces can go to that square
            if nbr_of_multi_moves > 1:
                self.move_from = None
                self.multiple_moves = True

            # in case user wants only to select the piece
            if game_state.board[self.move_to[0]][self.move_to[1]] == piece:
                self.move_from = self.move_to

        # if user input is in form of "piece move from move to" (rock a1 a5)
        elif len(input_split) == 3:
            self.move_from = chess_model.commands[0].move_from.col + str(chess_model.commands[0].move_from.row)
            self.move_to = chess_model.commands[0].move_to.col + str(chess_model.commands[0].move_to.row)
            self.move_from = tuple(map(int, self.input_notation(self.move_from)))
            self.move_to = tuple(map(int, self.input_notation(self.move_to)))

        else:
            return

        if not self.multiple_moves:
            if self.move_from != self.move_to:
                move = Move.Move(self.move_from, self.move_to, game_state.board)
                for i in range(len(valid_moves)):
                    if move == valid_moves[i]:
                        print(colored(">>> OK", "green"))
                        break

                if move not in valid_moves:
                    print(colored(">>> Info: That move is not in the list of valid moves.", "yellow"))

        else:
            print(colored(">>> Info: Possible multiple moves for: " + self.input_command, "yellow"))

    def run(self):
        """
        User input function. Contains two parts.
        First part handles with user handler commands such as undo, castling (short and long), new game, restart and exit.
        Second part handles piece movement.
        :return: True or False depending if the thread is alive or not
        """
        chess_mm = metamodel_from_file('textX/chess_rules.tx', ignore_case=True)
        while True:
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
                    pass
                else:
                    self.move_command(chess_model, game_state, valid_moves)
                    print(self.move_from)
