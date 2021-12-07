import random
import Json

piece_scores = {"K": 20000, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}

wp_scores = [[100, 100, 100, 100, 105, 100, 100, 100],
             [78, 83, 86, 73, 102, 82, 85, 90],
             [7, 29, 21, 44, 40, 31, 44, 7],
             [-17, 16, -2, 15, 14, 0, 15, -13],
             [-26, 3, 10, 9, 6, 1, 0, -23],
             [-22, 9, 5, -11, -10, -2, 3, -19],
             [-31, 8, -7, -37, -36, -14, 3, -31],
             [0, 0, 0, 0, 0, 0, 0, 0]]

wp_scores1 = [[0, 0, 0, 0, 0, 0, 0, 0],
              [50, 50, 50, 50, 50, 50, 50, 50],
              [10, 10, 20, 30, 30, 20, 10, 10],
              [5, 5, 10, 25, 25, 10, 5, 5],
              [0, 0, 0, 20, 20, 0, 0, 0],
              [5, -5, -10, 0, 0, -10, -5, 5],
              [5, 10, 10, -20, -20, 10, 10, 5],
              [0, 0, 0, 0, 0, 0, 0, 0]]

wN_scores = [[-66, -53, -75, -75, -10, -55, -58, -70],
             [-3, -6, 100, -36, 4, 62, -4, -14],
             [10, 67, 1, 74, 73, 27, 62, -2],
             [24, 24, 45, 37, 33, 41, 25, 17],
             [-1, 5, 31, 21, 22, 35, 2, 0],
             [-18, 10, 13, 22, 18, 15, 11, -14],
             [-23, -15, 2, 0, 2, 0, -23, -20],
             [-74, -23, -26, -24, -19, -35, -22, -69]]

wN_scores1 = [[-50, -40, -30, -30, -30, -30, -40, -50],
              [-40, -20, 0, 0, 0, 0, -20, -40],
              [-30, 0, 10, 15, 15, 10, 0, -30],
              [-30, 5, 15, 20, 20, 15, 5, -30],
              [-30, 0, 15, 20, 20, 15, 0, -30],
              [-30, 5, 10, 15, 15, 10, 5, -30],
              [-40, -20, 0, 5, 5, 0, -20, -40],
              [-50, -40, -30, -30, -30, -30, -40, -50]]

wB_scores = [[-59, -78, -82, -76, -23, -107, -37, -50],
             [-11, 20, 35, -42, -39, 31, 2, -22],
             [-9, 39, -32, 41, 52, -10, 28, -14],
             [25, 17, 20, 34, 26, 25, 15, 10],
             [13, 10, 17, 23, 17, 16, 0, 7],
             [14, 25, 24, 15, 8, 25, 20, 15],
             [19, 20, 11, 6, 7, 6, 20, 16],
             [-7, 2, -15, -12, -14, -15, -10, -10]]

wB_scores1 = [[-20, -10, -10, -10, -10, -10, -10, -20],
              [-10, 0, 0, 0, 0, 0, 0, -10],
              [-10, 0, 5, 10, 10, 5, 0, -10],
              [-10, 5, 5, 10, 10, 5, 5, -10],
              [-10, 0, 10, 10, 10, 10, 0, -10],
              [-10, 10, 10, 10, 10, 10, 10, -10],
              [-10, 5, 0, 0, 0, 0, 5, -10],
              [-20, -10, -10, -10, -10, -10, -10, -20]]

wR_scores = [[35, 29, 33, 4, 37, 33, 56, 50],
             [55, 29, 56, 67, 55, 62, 34, 60],
             [19, 35, 28, 33, 45, 27, 25, 15],
             [0, 5, 16, 13, 18, -4, -9, -6],
             [-28, -35, -16, -21, -13, -29, -46, -30],
             [-42, -28, -42, -25, -25, -35, -26, -46],
             [-53, -38, -31, -26, -29, -43, -44, -53],
             [-30, -24, -18, 5, -2, -18, -31, -32]]

wR_scores1 = [[0, 0, 0, 0, 0, 0, 0, 0, ],
              [5, 10, 10, 10, 10, 10, 10, 5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [0, 0, 0, 5, 5, 0, 0, 0]]

wQ_scores = [[6, 1, -8, -104, 69, 24, 88, 26],
             [14, 32, 60, -10, 20, 76, 57, 24],
             [-2, 43, 32, 60, 72, 63, 43, 2],
             [1, -16, 22, 17, 25, 20, -13, -6],
             [-14, -15, -2, -5, -1, -10, -20, -22],
             [-30, -6, -13, -11, -16, -11, -16, -27],
             [-36, -18, 0, -19, -15, -15, -21, -38],
             [-39, -30, -31, -13, -31, -36, -34, -42]]

wQ_scores1 = [[-20, -10, -10, -5, -5, -10, -10, -20],
              [-10, 0, 0, 0, 0, 0, 0, -10],
              [-10, 0, 5, 5, 5, 5, 0, -10],
              [-5, 0, 5, 5, 5, 5, 0, -5],
              [0, 0, 5, 5, 5, 5, 0, -5],
              [-10, 5, 5, 5, 5, 5, 0, -10],
              [-10, 0, 5, 0, 0, 0, 0, -10],
              [-20, -10, -10, -5, -5, -10, -10, -20]]

wK_scores = [[4, 54, 47, -99, -99, 60, 83, -62],
             [-32, 10, 55, 56, 56, 55, 10, 3],
             [-62, 12, -57, 44, -67, 28, 37, -31],
             [-55, 50, 11, -4, -19, 13, 0, -49],
             [-55, -43, -52, -28, -51, -47, -8, -50],
             [-47, -42, -43, -79, -64, -32, -29, -32],
             [-4, 3, -14, -50, -57, -18, 13, 4],
             [17, 30, -3, -14, 6, -1, 40, 18]]

wK_scores1 = [[-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-20, -30, -30, -40, -40, -30, -30, -20],
              [-10, -20, -20, -20, -20, -20, -20, -10],
              [20, 20, 0, 0, 0, 0, 20, 20],
              [20, 30, 10, 0, 0, 10, 30, 20]]

bp_scores = wp_scores[::-1]
bN_scores = wN_scores[::-1]
bB_scores = wB_scores[::-1]
bR_scores = wR_scores[::-1]
bQ_scores = wQ_scores[::-1]
bK_scores = wK_scores[::-1]

piece_position_scores = {"wp": wp_scores, "bp": bp_scores, "wN": wN_scores, "bN": bN_scores, "wB": wB_scores,
                         "bB": bB_scores,
                         "wR": wR_scores, "bR": bR_scores, "wQ": wQ_scores, "bQ": bQ_scores, "wK": wK_scores,
                         "bK": bK_scores}

json_data = Json.read_from_json()  # global parameter that contains values from settings.json JSON file.
CHECKMATE = 1000000
STALEMATE = 0
DEPTH = json_data['SETTINGS']['DIFFICULTY']
next_move = None
counter = None


def find_random_move(valid_moves):
    """
    Picks and returns a random move.
    :param valid_moves:
    :return:
    """
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def greedy_algorithm(game_state, valid_moves):
    """
    Greedy Algorithm -> MinMax without recursion.
    Find the best move based on material alone.
    :param game_state:
    :param valid_moves:
    :return:
    """
    turn_multiplier = 1 if game_state.whiteToMove else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponents_moves = game_state.get_valid_moves()
        if game_state.staleMate:
            opponent_max_score = STALEMATE
        elif game_state.checkMate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponents_move in opponents_moves:
                game_state.make_move(opponents_move)
                # game_state.get_valid_moves()
                if game_state.checkMate:
                    score = CHECKMATE
                elif game_state.staleMate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(game_state.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                game_state.undo_move()
        if opponent_max_score < opponent_minmax_score:
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()
    return best_player_move


def find_best_move(game_state, valid_moves):
    """
    Helper method to make first recursive call.
    :param game_state:
    :param valid_moves:
    :return:
    """
    global next_move, counter, DEPTH, json_data
    json_data = Json.read_from_json()  # global parameter that contains values from settings.json JSON file.
    DEPTH = json_data['SETTINGS']['DIFFICULTY']
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    # find_move_min_max(game_state, valid_moves, DEPTH, game_state.whiteToMove)
    # find_move_nega_max(game_state, valid_moves, DEPTH, 1 if game_state.whiteToMove else -1)
    find_move_nega_max_alpha_beta_pruning(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
    # (counter)
    return next_move


def find_move_min_max(game_state, valid_moves, depth, white_to_move):
    """
    Min-Max Algorithm with recursion.
    :param game_state:
    :param valid_moves:
    :param depth:
    :param white_to_move:
    :return:
    """
    global next_move
    if depth == 0:
        return score_material(game_state.board)
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return min_score


def find_move_nega_max(game_state, valid_moves, depth, turn_multiplier):
    """
    Nega-Max Algorithm with recursion. Works the same as Min-Max Algorithm.
    :param game_state:
    :param valid_moves:
    :param depth:
    :param turn_multiplier:
    :return:
    """
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(game_state)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_nega_max(game_state, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undo_move()
    return max_score


def find_move_nega_max_alpha_beta_pruning(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
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
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(game_state)
    # move ordering - implement later
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_nega_max_alpha_beta_pruning(game_state, next_moves, depth - 1, -beta, -alpha,
                                                       -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                # print(move, score)
        game_state.undo_move()
        # pruning happens
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(game_state, ):
    """
    A positive score is good for white, a negative score is good for black.
    :param game_state:
    :return:
    """
    if game_state.checkMate:
        if game_state.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif game_state.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            square = game_state.board[row][col]
            if square != "--":
                # score it positionally
                piece_position_score = piece_position_scores[square][row][col]
                if square[0] == 'w':
                    score += piece_scores[square[1]] + piece_position_score * .1
                elif square[0] == 'b':
                    score -= piece_scores[square[1]] + piece_position_score * .1
    return score


def score_material(board):
    """
    Score the board based on material.
    :param board:
    :return:
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_scores[square[1]]
            elif square[0] == 'b':
                score -= piece_scores[square[1]]
    return score
