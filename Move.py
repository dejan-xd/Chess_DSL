class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant_move=False, is_castle_move=False):
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.notation = None

        # castle move
        self.isCastleMove = is_castle_move

        # pawn promotion
        self.isPawnPromotion = self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7)

        # en passant move
        self.isEnPassantMove = is_en_passant_move
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'  # en passant captures opposite colored pawn

        # check if piece is captured (check after possible en passant move)
        self.isCapture = self.pieceCaptured != '--'

    def __eq__(self, other):
        """
        Overriding the equals method.
        :param other:
        :return:
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        """
        Combine get rank file to make real chess notation from start row/col and end row/col. For example: (e2 e4)
        :return:
        """
        return self.get_rank_file(self.startRow, self.startCol) + " " + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, row, col):
        """
        Function to make part of chess notation. For example: (col+row) -> (e2)
        :param row:
        :param col:
        :return:
        """
        return self.colsToFiles[col] + self.rowsToRanks[row]

    def __str__(self):
        """
        Overriding the str() function.
        :return:
        """

        end_square = self.get_rank_file(self.endRow, self.endCol)

        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture and self.isPawnPromotion:
                return self.colsToFiles[self.startCol] + "x" + end_square + "=Q"  # queen promotion
            elif self.isCapture:
                if self.isEnPassantMove:
                    return self.colsToFiles[self.startCol] + "x" + end_square + " e.p."  # en passant
                return self.colsToFiles[self.startCol] + "x" + end_square  # capture
            elif self.isPawnPromotion:
                return end_square + "=Q"  # queen promotion
            else:
                return end_square

        # piece moves
        move_string = self.pieceMoved[1]
        if self.isCapture:
            move_string += 'x'
            if self.isEnPassantMove:
                return move_string + end_square + 'e.p.'  # en passant

        return move_string + end_square
