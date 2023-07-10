"""
Responsible for :
-storing all information about current state of chess game.
-determining valid moves at current state.
-keep move log
"""

import numpy as np


class GameState:
    def __init__(self):
        """
        board of 8x8 space, with each piece having 2 attributes,
        -it's color ( b or w for black or white )
        - type of piece ( K- king , Q-Queen , R- Rook, B- Bishop, N-Knight, or p-pawn)
        &  "--" represents empty space
        """
        # Create an empty chess board
        self.board = np.empty((8, 8), dtype=object)
        self.board.fill('--')

        # Place the chess pieces on the board
        self.board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']  # Black back row
        self.board[1] = ['bp'] * 8  # Black pawns
        self.board[6] = ['wp'] * 8  # White pawns
        self.board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']  # White back row

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        # Takes move as parameter & executes it, doesn't include Castling & en-passant

        self.board[move.startRow, move.startCol] = '--'  # empties the cell from where piece moved
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move to be able to undo it later
        self.whiteToMove = not self.whiteToMove  # swapping the player turn

    def undo(self):
        # undo last move

        if len(self.moveLog):  # checks if move log isn't empty
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switches the turn


class Move:
    # mapping ranks to their respective rows
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    # mapping  rows in board to their respective ranks
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # mapping files to their respective columns
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    # mapping column  to their respective files
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        # extracting starting and end position of piece to be moved
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        # storing piece moved and piece captured(if any), for undoing if needed
        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]

    def getChessNotation(self):
        # returns chess notation for particular move
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        # returns rank/file using row and columns
        return self.colsToFiles[col] + self.rowsToRanks[row]
