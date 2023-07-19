import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
nextMove = None  # set a global variable to store the best possible move in current game state


def findBestMove(gs, validMoves):
    # helper method to make first recursive call
    global nextMove
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else 0)
    return nextMove


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    random.shuffle(validMoves)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
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
