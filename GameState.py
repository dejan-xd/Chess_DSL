"""
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible
for determining the valid moves at the current state. It will also keep a move log.
"""
import Move


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

        self.move_function = {'p': self.get_pawn_moves, 'R': self.get_rock_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.game_over = False
        self.moveLog = []

        self.player_one = False  # play as white
        self.player_two = False  # play as black

        self.checkMate = True
        self.staleMate = True

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.enpassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]

    def make_move(self, move):
        """
        Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant).
        :param move:
        :return:
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if needed
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # en passant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the en passant pawn

        # if pawn moves twice, next move can capture en passant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only on 2 square pawn move
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # update en passant log
        self.enpassantPossibleLog.append(self.enpassantPossible)

    def undo_move(self):
        """
        Undo the last move made.
        :return:
        """
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back

            # update the king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

    def get_all_possible_moves(self):
        """
        All moves without considering checks.
        :return:
        """
        moves = []
        for row in range(len(self.board)):  # number of rows
            for col in range(len(self.board[row])):  # number of cols in given row
                turn = self.board[row][col][0]  # taking first char from an element determining which turn it is
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]  # taking the piece type from element
                    self.move_function[piece](row, col, moves)  # calls move function based on piece type
        return moves

    def square_under_attack(self, row, col):
        """
        Determine if the enemy can attack the square (row,col)
        :param row:
        :param col:
        :return:
        """
        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove  # switch back point of view
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False

    def in_check(self):
        """
        Determine if the current player is in check
        :return:
        """
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    def get_valid_moves(self):
        """
        Get all valid moves considering checks.
        :return:
        """
        temp_en_passant_possible = self.enpassantPossible  # temporary store the value of the en passant square

        # 1. generate all possible moves
        moves = self.get_all_possible_moves()
        # 2. for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list go backwards through that list
            self.make_move(moves[i])  # making one of the moves -> it's opponent's turn
            # 3. generate all opponent's moves
            # 4. for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove  # switch back the turn so in_check() doesn't look the wrong color
            if self.in_check():
                moves.remove(moves[i])  # 5. if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undo_move()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.in_check():
                self.checkMate = True
                self.game_over = True
            else:
                self.staleMate = True

        self.enpassantPossible = temp_en_passant_possible  # return original value of the en passant square

        return moves

    def get_pawn_moves(self, row, col, moves):
        """
        Get all pawn moves for the pawn located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        if self.whiteToMove:  # white pawn moves
            if self.board[row - 1][col] == "--":  # 1 square pawn advance
                moves.append(Move.Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":  # 2 square pawn advance
                    moves.append(Move.Move((row, col), (row - 2, col), self.board))
            # captures
            if col - 1 >= 0:  # captures to the left
                if self.board[row - 1][col - 1][0] == 'b':  # there is an enemy piece to capture
                    moves.append(Move.Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassantPossible:  # en passant move to the left
                    moves.append(Move.Move((row, col), (row - 1, col - 1), self.board, is_en_passant_move=True))
            if col + 1 <= 7:  # captures to the right
                if self.board[row - 1][col + 1][0] == 'b':  # there is an enemy piece to capture
                    moves.append(Move.Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassantPossible:  # en passant move to the right
                    moves.append(Move.Move((row, col), (row - 1, col + 1), self.board, is_en_passant_move=True))

        else:  # black pawn moves
            if self.board[row + 1][col] == '--':  # 1 square move
                moves.append(Move.Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == '--':  # 2 square moves
                    moves.append(Move.Move((row, col), (row + 2, col), self.board))
            # captures
            if col - 1 >= 0:  # capture to the left
                if self.board[row + 1][col - 1][0] == 'w':  # there is an enemy piece to capture
                    moves.append(Move.Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassantPossible:  # en passant move to the left
                    moves.append(Move.Move((row, col), (row + 1, col - 1), self.board, is_en_passant_move=True))
            if col + 1 <= 7:  # capture to the right
                if self.board[row + 1][col + 1][0] == 'w':  # there is an enemy piece to capture
                    moves.append(Move.Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassantPossible:  # en passant move to the right
                    moves.append(Move.Move((row, col), (row + 1, col + 1), self.board, is_en_passant_move=True))

    def get_rock_moves(self, row, col, moves):
        """
        Get all rock moves for the rock located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1, 8):  # rock can move max of 7 squares
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # is it on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space valid
                        moves.append(Move.Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(Move.Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    def get_knight_moves(self, row, col, moves):
        """
        Get all knight moves for the rock located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # is it on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece (empty square or enemy piece)
                    moves.append(Move.Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        """
        Get all bishop moves for the rock located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # bishop can move max of 7 squares
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # is it on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space valid
                        moves.append(Move.Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(Move.Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    def get_queen_moves(self, row, col, moves):
        """
        Get all queen moves for the rock located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        # abstraction
        self.get_rock_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        """
        Get all king moves for the rock located at row, col and add these moves to the list 'moves'.
        :param row:
        :param col:
        :param moves:
        :return:
        """
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.whiteToMove else "b"
        # different for loop logic because of check
        for i in range(8):
            end_row = row + directions[i][0]
            end_col = col + directions[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # is it on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece (empty square or enemy piece)
                    moves.append(Move.Move((row, col), (end_row, end_col), self.board))
