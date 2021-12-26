import threading
import Move


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

    def run(self):
        """
        User input function. Contains two parts.
        First part handles with user handler commands such as undo, castling (short and long), new game, restart and exit.
        Second part handles piece movement.
        :return: True or False depending if the thread is alive or not
        """
        while True:
            if self.enter:
                self.move_from = self.move_to = None
                self.enter = False

                exec(self.input_command, globals())

                input_command_split = self.input_command.split("'")
                self.input_command = input_command_split[1]

                if self.input_command == 'undo':
                    pass
                else:
                    split_command = self.input_command.split(' ')
                    self.move_from = tuple(map(int, self.input_notation(split_command[0])))
                    self.move_to = tuple(map(int, self.input_notation(split_command[1])))
