# helper method for reading user inputs for several languages (English, Serbian, Spanish, German, French
# also reads piece names and commands for each language
import Json


def piece_name(piece):
    """
    Method for creating English abbreviation name for each chess piece for each language.
    :param piece:
    :return:
    """
    json_data = Json.read_from_json()

    if piece in json_data['PION']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'p'

    elif piece in json_data['KNIGHT']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'N'

    elif piece in json_data['BISHOP']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'B'

    elif piece in json_data['ROOK']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'R'

    elif piece in json_data['QUEEN']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'Q'

    elif piece in json_data['KING']:
        piece = json_data['SETTINGS']['PIECE_COLOR'] + 'K'

    return piece


def get_game_command(command):
    """
    Method for creating English word for each handler command for each language.
    :param command:
    :return:
    """

    json_data = Json.read_from_json()

    if command in json_data['UNDO']:
        command = json_data['COMMANDS']['UNDO']

    elif command in json_data['RESTART']:
        command = json_data['COMMANDS']['RESTART']

    elif command in json_data['EXIT']:
        command = json_data['COMMANDS']['EXIT']

    elif command in json_data['CASTLING_SHORT']:
        command = json_data['COMMANDS']['CASTLE_SHORT']

    elif command in json_data['CASTLING_LONG']:
        command = json_data['COMMANDS']['CASTLE_LONG']

    elif command in json_data['NEW_GAME']:
        command = json_data['COMMANDS']['NEW_GAME']

    return command


def print_command(game_state, cm):
    """
    Method for creating print command for each language. Also checks if there is anything to undo or if the castling is already called.
    :param game_state:
    :param cm:
    :return:
    """
    pr_cm = undo_print = castle_used_print = None
    json_data = Json.read_from_json()

    if cm in json_data['LANGUAGE_COMMANDS']['SERBIAN']['COMMANDS']:
        pr_cm = json_data['LANGUAGE_COMMANDS']['SERBIAN']['PRINT_COMMAND']
        undo_print = json_data['LANGUAGE_COMMANDS']['SERBIAN']['UNDO_PRINT']
        if game_state.castleUsed:
            castle_used_print = json_data['LANGUAGE_COMMANDS']['SERBIAN']['CASTLE_PRINT']

    elif cm in json_data['LANGUAGE_COMMANDS']['ENGLISH']['COMMANDS']:
        pr_cm = json_data['LANGUAGE_COMMANDS']['ENGLISH']['PRINT_COMMAND']
        undo_print = json_data['LANGUAGE_COMMANDS']['ENGLISH']['UNDO_PRINT']
        if game_state.castleUsed:
            castle_used_print = json_data['LANGUAGE_COMMANDS']['ENGLISH']['CASTLE_PRINT']

    elif cm in json_data['LANGUAGE_COMMANDS']['SPANISH']['COMMANDS']:
        pr_cm = json_data['LANGUAGE_COMMANDS']['SPANISH']['PRINT_COMMAND']
        undo_print = json_data['LANGUAGE_COMMANDS']['SPANISH']['UNDO_PRINT']
        if game_state.castleUsed:
            castle_used_print = json_data['LANGUAGE_COMMANDS']['SPANISH']['CASTLE_PRINT']

    elif cm in json_data['LANGUAGE_COMMANDS']['GERMAN']['COMMANDS']:
        pr_cm = json_data['LANGUAGE_COMMANDS']['GERMAN']['PRINT_COMMAND']
        undo_print = json_data['LANGUAGE_COMMANDS']['GERMAN']['UNDO_PRINT']
        if game_state.castleUsed:
            castle_used_print = json_data['LANGUAGE_COMMANDS']['GERMAN']['CASTLE_PRINT']

    elif cm in json_data['LANGUAGE_COMMANDS']['FRENCH']['COMMANDS']:
        pr_cm = json_data['LANGUAGE_COMMANDS']['FRENCH']['PRINT_COMMAND']
        undo_print = json_data['LANGUAGE_COMMANDS']['FRENCH']['UNDO_PRINT']
        if game_state.castleUsed:
            castle_used_print = json_data['LANGUAGE_COMMANDS']['FRENCH']['CASTLE_PRINT']

    return pr_cm, undo_print, castle_used_print
