"""
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible
for determining the valid moves at the current state. It will also keep a move log.
"""


class GameState:
    def __init__(self):
        """
        Board is an 8x8 2D list.
        Each element of the list has 2 characters.
        The 1st character represents the color of the piece: 'b' for black or 'w' for white.
        The 2nd character represents the type of the piece:
            'K' for the King,
            'Q' for the Queen,
            'R' for the Rock,
            'B' for the Bishop,
            'N' for the Knight, or
            'P' for the Peon.
        '--' - represents an empty space on the board with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.player_one = False  # play as white
        self.player_two = False  # play as black

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.whiteToMove = True

        self.game_over = False

    def make_move(self, move):
        """
        Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant).
        :param move:
        :return:
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if needed
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
