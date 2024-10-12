"""
Tic Tac Toe Player
"""

import math
import copy 

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    if (9 - sum(row.count(EMPTY) for row in board)) % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i,j)) 
    return actions
    

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
       raise Exception("Invalid action.")
    
    i, j = action
    if board[i][j] != EMPTY:
        raise Exception("Invalid action.")
    
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    if (board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]) and board[1][1] != EMPTY:
        return board[1][1]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or sum(row.count(EMPTY) for row in board) == 0:
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    next_player = player(board)
    if next_player == X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]
    

def max_value(board):
    best_move = None
    if terminal(board):
        return utility(board), best_move
    
    max = float('-inf')
    for action in actions(board):
        v, _ = min_value(result(board, action))
        if v > max:
            max = v
            best_move = action

    return max, best_move


def min_value(board):
    best_move = None
    if terminal(board):
        return utility(board), best_move
    
    min = float('inf')
    for action in actions(board):
        v, _ = max_value(result(board, action))
        if v < min:
            min = v
            best_move = action

    return min, best_move

