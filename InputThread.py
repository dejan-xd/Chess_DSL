import threading

class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread, self).__init__()
        self.daemon = True  # for exiting on X, don't delete
        self.last_user_input = None

    def run(self):
        """
        User input function. Contains two parts.
        First part handles with user handler commands such as undo, castling (short and long), new game, restart and exit.
        Second part handles piece movement.
        :return: True or False depending if the thread is alive or not
        """

        while True:
            if self.last_user_input != None:
                exec(self.last_user_input, globals())
                self.last_user_input = None