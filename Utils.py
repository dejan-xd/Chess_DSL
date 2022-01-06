from JsonParser import JsonParser


class Utils:
    def __init__(self):
        self.json_parser = JsonParser()

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

    def get_game_command(self, command):
        """
        Method for creating English word for each handler command for each language.
        :param command:
        :return:
        """
        if command in self.json_parser.get_by_key('UNDO'):
            command = self.json_parser.get_by_key('COMMANDS', 'UNDO')

        elif command in self.json_parser.get_by_key('RESTART'):
            command = self.json_parser.get_by_key('COMMANDS', 'RESTART')

        elif command in self.json_parser.get_by_key('EXIT'):
            command = self.json_parser.get_by_key('COMMANDS', 'EXIT')

        elif command in self.json_parser.get_by_key('CASTLING_SHORT'):
            command = self.json_parser.get_by_key('COMMANDS', 'CASTLE_SHORT')

        elif command in self.json_parser.get_by_key('CASTLING_LONG'):
            command = self.json_parser.get_by_key('COMMANDS', 'CASTLE_LONG')

        elif command in self.json_parser.get_by_key('NEW_GAME'):
            command = self.json_parser.get_by_key('COMMANDS', 'NEW_GAME')

        return command

    def print_command(self, game_state, cm):
        """
        Method for creating print command for each language. Also checks if there is anything to undo or if the castling is already called.
        :param game_state:
        :param cm:
        :return:
        """
        pr_cm = undo_print = castle_used_print = None

        if cm in self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SERBIAN', 'COMMANDS'):
            pr_cm = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SERBIAN', 'PRINT_COMMAND')
            undo_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SERBIAN', 'UNDO_PRINT')
            if game_state.castleUsed:
                castle_used_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SERBIAN', 'CASTLE_PRINT')

        elif cm in self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'ENGLISH', 'COMMANDS'):
            pr_cm = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'ENGLISH', 'PRINT_COMMAND')
            undo_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'ENGLISH', 'UNDO_PRINT')
            if game_state.castleUsed:
                castle_used_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'ENGLISH', 'CASTLE_PRINT')

        elif cm in self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SPANISH', 'COMMANDS'):
            pr_cm = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SPANISH', 'PRINT_COMMAND')
            undo_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SPANISH', 'UNDO_PRINT')
            if game_state.castleUsed:
                castle_used_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'SPANISH', 'CASTLE_PRINT')

        elif cm in self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'GERMAN', 'COMMANDS'):
            pr_cm = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'GERMAN', 'PRINT_COMMAND')
            undo_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'GERMAN', 'UNDO_PRINT')
            if game_state.castleUsed:
                castle_used_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'GERMAN', 'CASTLE_PRINT')

        elif cm in self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'FRENCH', 'COMMANDS'):
            pr_cm = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'FRENCH', 'PRINT_COMMAND')
            undo_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'FRENCH', 'UNDO_PRINT')
            if game_state.castleUsed:
                castle_used_print = self.json_parser.get_by_key('LANGUAGE_COMMANDS', 'FRENCH', 'CASTLE_PRINT')

        return pr_cm, undo_print, castle_used_print
