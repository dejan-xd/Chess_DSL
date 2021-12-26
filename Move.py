class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

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
