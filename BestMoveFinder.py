import random
import numpy as np

pieceScore = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
nextMove = None  # set a global variable to store the best possible move in current game state


def findBestMove(gs, validMoves):
    # helper method to make first recursive call
    global nextMove
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMax(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove


def findMoveNegaMax(gs, validMoves, depth, alpha, beta, turnMultiplier):
    # NegaMax with Alpha Beta Pruning
    global nextMove
    if depth == 0:
        return turnMultiplier * evaluate_board(gs.board)
    random.shuffle(validMoves)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
        if maxScore > alpha:  # pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    random.shuffle(validMoves)
    if whiteToMove:
        # white's turn, try to maximize the score
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        # black's turn, try to minimize the score
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def greedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)

        opponentMoves = gs.getValidMoves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreBoard(gs)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()

        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()

    return bestPlayerMove


def scoreBoard(gs):
    # function to check current state of board,  positive score is good for white and negative is good for black

    if gs.checkMate:  # if one player is already checkmated, need not check the whole board
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    if gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        # iterating through each square of the board, adding value of piece if white, else subtract
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score


def evaluate_board(board):
    # another way of evaluating board
    piece_values = {'p': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}  # Piece values
    piece_squares = {
        'p': np.array([
            [8, 8, 8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [5, 6, 6, 7, 7, 6, 6, 5],
            [2, 2, 3, 5, 5, 3, 2, 2],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]),
        'N': np.array([
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 1, 2, 2, 2, 2, 2, 1],
            [0, 1, 1, 1, 1, 1, 1, 0]
        ]),
        'B': np.array([
            [1, 2, 2, 1, 1, 2, 2, 1],
            [2, 4, 3, 2, 2, 3, 4, 2],
            [2, 3, 4, 3, 3, 4, 3, 2],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [2, 3, 4, 3, 3, 4, 3, 2],
            [2, 4, 3, 2, 2, 3, 4, 2],
            [1, 2, 2, 1, 1, 2, 2, 1]

        ]),
        'R': np.array([
            [0, 2, 2, 2, 2, 2, 2, 0],
            [3, 3, 3, 3, 3, 3, 3, 3],
            [1, 1, 2, 2, 2, 2, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 2, 2, 2, 2, 1, 1],
            [1, 1, 1, 3, 3, 1, 1, 1],
            [0, 2, 3, 4, 4, 3, 2, 0],
        ]),
        'Q': np.array([
            [0, 1, 1, 3, 1, 1, 1, 0],
            [1, 2, 3, 3, 3, 1, 1, 1],
            [1, 4, 3, 3, 3, 4, 2, 1],
            [1, 2, 3, 3, 3, 2, 2, 1],
            [1, 2, 3, 3, 3, 2, 2, 1],
            [1, 4, 3, 3, 3, 4, 2, 1],
            [1, 2, 3, 3, 3, 1, 1, 1],
            [0, 1, 1, 3, 1, 1, 1, 0]
        ]),
        'K': np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [4, 6, 4, 1, 1, 4, 6, 4],
            [6, 8, 6, 3, 3, 6, 8, 6],
        ])
    }

    # Initialize evaluation values
    material_eval = 0
    mobility_eval = 0
    king_safety_eval = 0
    pawn_structure_eval = 0
    piece_activity_eval = 0

    white_pawn_files = set()
    black_pawn_files = set()
    white_passed_pawns = 0
    black_passed_pawns = 0

    white_king_pos = None
    black_king_pos = None
    white_pawn_shelter = 0
    black_pawn_shelter = 0
    white_pawn_cover = 0
    black_pawn_cover = 0
    white_castled = False
    black_castled = False

    # Iterate over the board
    for row in range(8):
        for col in range(8):
            piece = board[row][col]

            # Evaluate material balance
            if piece[0] == 'w':
                material_eval += piece_values[piece[1]]
            elif piece[0] == 'b':
                material_eval -= piece_values[piece[1]]

            # Evaluate piece-square tables
            if piece[0] == 'w':
                piece_activity_eval += piece_squares[piece[1]][row][col]
            elif piece[0] == 'b':
                piece_activity_eval -= piece_squares[piece[1]][7 - row][col]

            # Evaluate pawn structure
            if piece == 'wp':
                # Check for doubled pawns
                if col in white_pawn_files:
                    pawn_structure_eval -= 5
                else:
                    white_pawn_files.add(col)

                # Check for isolated pawns
                if not (col - 1 in white_pawn_files or col + 1 in white_pawn_files):
                    pawn_structure_eval -= 10

                # Check for passed pawns
                if not np.any(board[r][col - 1:col + 2] == '--' for r in range(row + 1, 8)):
                    white_passed_pawns += 1

            elif piece == 'bp':
                # Check for doubled pawns
                if col in black_pawn_files:
                    pawn_structure_eval += 5
                else:
                    black_pawn_files.add(col)

                # Check for isolated pawns
                if not (col - 1 in black_pawn_files or col + 1 in black_pawn_files):
                    pawn_structure_eval += 10

                # Check for passed pawns
                if not np.any(board[r][col - 1:col + 2] == '--' for r in range(row - 1, -1, -1)):
                    black_passed_pawns += 1
            # Reward passed pawns and pawn majority
            pawn_structure_eval += 5 * (white_passed_pawns - black_passed_pawns)
            if len(white_pawn_files) > len(black_pawn_files):
                pawn_structure_eval += 10
            elif len(black_pawn_files) > len(white_pawn_files):
                pawn_structure_eval -= 10

            # Find king positions
            if piece == 'wK':
                white_king_pos = (row, col)
            elif piece == 'bK':
                black_king_pos = (row, col)

            # Evaluate pawn shelter and pawn cover
            if row in [6, 7]:  # White pawn rows
                if col in [5, 6]:  # Shelter squares: g2/h2 for White
                    white_pawn_shelter += 5
                if col in [4, 5, 6]:  # Cover squares: f2/g2/h2 for White
                    white_pawn_cover += 2
            elif row in [0, 1]:  # Black pawn rows
                if col in [5, 6]:  # Shelter squares: g7/h7 for Black
                    black_pawn_shelter += 5
                if col in [4, 5, 6]:  # Cover squares: f7/g7/h7 for Black
                    black_pawn_cover += 2

            # Check if kings have castled
            if white_king_pos:
                if white_king_pos[1] == 4 and white_king_pos[0] == 7:
                    white_castled = True
            if black_king_pos:
                if black_king_pos[1] == 4 and black_king_pos[0] == 0:
                    black_castled = True

            # Reward pawn shelter and pawn cover
            king_safety_eval += white_pawn_shelter - black_pawn_shelter + white_pawn_cover - black_pawn_cover

            # Penalize for not castling
            if not white_castled:
                king_safety_eval -= 10
            if not black_castled:
                king_safety_eval += 10

    # Combine the evaluation factors with appropriate weights and sign factor
    evaluation = (
            100 * material_eval +
            10 * mobility_eval +
            10 * king_safety_eval +
            5 * pawn_structure_eval +
            5 * piece_activity_eval
    )

    return evaluation
