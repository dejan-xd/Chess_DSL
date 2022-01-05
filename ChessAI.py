from JsonParser import JsonParser
import random


class ChessAI:
    def __init__(self):
        self.file_score = "score_material.json"
        self.json_parser_score = JsonParser(self.file_score)
        self.file_settings = "settings.json"
        self.json_parser_settings = JsonParser(self.file_settings)
        self.next_move = None
        self.depth = self.json_parser_settings.get_by_key('SETTINGS', 'DIFFICULTY')
        self.piece_scores = self.json_parser_score.get_by_key('PIECE_SCORES')
        self.checkmate = self.json_parser_score.get_by_key('CHECKMATE')
        self.stalemate = self.json_parser_score.get_by_key('STALEMATE')

        self.wp_scores = self.json_parser_score.get_by_key('WHITE_PAWN')
        self.wN_scores = self.json_parser_score.get_by_key('WHITE_KNIGHT')
        self.wB_scores = self.json_parser_score.get_by_key('WHITE_BISHOP')
        self.wR_scores = self.json_parser_score.get_by_key('WHITE_ROOK')
        self.wQ_scores = self.json_parser_score.get_by_key('WHITE_QUEEN')
        self.wK_scores = self.json_parser_score.get_by_key('WHITE_KING')

        self.bp_scores = self.wp_scores[::-1]
        self.bN_scores = self.wN_scores[::-1]
        self.bB_scores = self.wB_scores[::-1]
        self.bR_scores = self.wR_scores[::-1]
        self.bQ_scores = self.wQ_scores[::-1]
        self.bK_scores = self.wK_scores[::-1]

        self.piece_position_scores = {
            "wp": self.wp_scores,
            "bp": self.bp_scores,
            "wN": self.wN_scores,
            "bN": self.bN_scores,
            "wB": self.wB_scores,
            "bB": self.bB_scores,
            "wR": self.wR_scores,
            "bR": self.bR_scores,
            "wQ": self.wQ_scores,
            "bQ": self.bQ_scores,
            "wK": self.wK_scores,
            "bK": self.bK_scores
        }

    def score_board(self, game_state):
        """
        A positive score is good for white, a negative score is good for black.
        :param game_state:
        :return:
        """
        if game_state.checkMate:
            if game_state.whiteToMove:
                return -self.checkmate  # black wins
            else:
                return self.checkmate  # white wins
        elif game_state.staleMate:
            return self.stalemate

        score = 0
        for row in range(len(game_state.board)):
            for col in range(len(game_state.board[row])):
                square = game_state.board[row][col]
                if square != "--":
                    # score it positionally
                    piece_position_score = self.piece_position_scores[square][row][col]
                    if square[0] == 'w':
                        score += self.piece_scores[square[1]] + piece_position_score * .1
                    elif square[0] == 'b':
                        score -= self.piece_scores[square[1]] + piece_position_score * .1
        return score

    @staticmethod
    def find_random_move(valid_moves):
        """
        Picks and returns a random move.
        :param valid_moves:
        :return:
        """
        return valid_moves[random.randint(0, len(valid_moves) - 1)]

    def find_move_nega_max_alpha_beta_pruning(self, game_state, valid_moves, depth, alpha, beta, turn_multiplier):
        """
        Nega-Max Algorithm with alpha beta pruning.
        :param game_state:
        :param valid_moves:
        :param depth:
        :param alpha:
        :param beta:
        :param turn_multiplier:
        :return:
        """
        if depth == 0:
            return turn_multiplier * self.score_board(game_state)
        # move ordering - implement later
        max_score = -self.checkmate
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = -self.find_move_nega_max_alpha_beta_pruning(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
            if score > max_score:
                max_score = score
                if depth == self.depth:
                    self.next_move = move
            game_state.undo_move()
            # pruning happens
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break
        return max_score

    def find_best_move(self, game_state, valid_moves):
        """
        Helper method to make first recursive call.
        :param game_state:
        :param valid_moves:
        :return:
        """
        self.next_move = None
        random.shuffle(valid_moves)
        self.find_move_nega_max_alpha_beta_pruning(game_state, valid_moves, self.depth, -self.checkmate, self.checkmate, 1 if game_state.whiteToMove else -1)
        return self.next_move
