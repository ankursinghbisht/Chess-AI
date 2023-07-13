"""
Responsible for :
-storing all information about current state of chess game.
-determining valid moves at current state.
-keep move log
"""

import numpy as np

DIMENSION = 8


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

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        # maps each function to its respective piece character

        self.whiteToMove = True
        self.moveLog = []

        # variable to store king's location
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # checks for checkmate or stalemate
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        # Takes move as parameter & executes it, doesn't include Castling & en-passant

        self.board[move.startRow, move.startCol] = '--'  # empties the cell from where piece moved
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move to be able to undo it later
        self.whiteToMove = not self.whiteToMove  # swapping the player turn

        if move.pieceMoved == 'wK':
            # piece moved was white king
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            # piece moved was white king
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        # undo last move

        if len(self.moveLog):  # checks if move log isn't empty
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switches the turn

            if move.pieceMoved == 'wK':
                # piece moved was white king
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                # piece moved was white king
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        # all moves considering checks, i.e.to check if the piece movement gets king a check.
        """
        Naive Methods for checking king checks:
        -generate all possible moves
        -for each move, make a move
        -generate all possible opponent move
        -for each move, check if any opponent move attack the king
        -if they do attack the king, it's not a valid move
        """

        moves = self.getAllPossibleMoves()

        for i in range(len(moves) - 1, -1, -1):  # when removing items from list, go backwards for potential bugs
            self.makeMove(moves[i])
            oppoMoves = self.getAllPossibleMoves()

            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            # if there is no valid moves, there might be a checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    def inCheck(self):
        # checks if current player is in check

        if self.whiteToMove:
            return self.isUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.isUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def isUnderAttack(self, r, c):
        # determines if enemy can attack the square

        self.whiteToMove = not self.whiteToMove  # switch to opponent's POV
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            # checks if any move attacks cell (r,c)
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        # Get piece's all possible moves
        moves = [Move([6, 4], [4, 4], self.board)]  # stores all possible moves
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                turn = self.board[r, c][0]  # gets first character of the pieces ( eg, bR -> b, wK -> w)
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # checks if white player chose the white piece and similar for black.
                    piece = self.board[r, c][1]
                    self.moveFunctions[piece](r, c, moves)  # calls the appropriate move function based on piece type
        return moves

    def getPawnMoves(self, r, c, moves):
        # gets all possible pawn moves and append it to moves
        if self.whiteToMove:  # white's turn
            if self.board[r - 1, c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2, c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures to the left , to check if piece don't go overboard
                if self.board[r - 1, c - 1][0] == 'b':  # enemy's piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # captures to the right , to check if piece don't go overboard
                if self.board[r - 1, c + 1][0] == 'b':  # enemy's piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:
            # black's turn
            if self.board[r + 1, c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2, c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # captures to the left , to check if piece don't go overboard
                if self.board[r + 1, c - 1][0] == 'w':  # enemy's piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # captures to the right , to check if piece don't go overboard
                if self.board[r + 1, c + 1][0] == 'w':  # enemy's piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def getRookMoves(self, r, c, moves):
        # gets all possible rook moves and append to moves variable

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # possible directions of rook move (up,left, down, right)

        enemyColor = 'b' if self.whiteToMove else 'w'  # sets enemy color regarding which player has the turn

        for d in directions:
            for i in range(1, 8):
                # sets total distance rook can travel, one step at a time
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                    endPiece = self.board[endRow, endCol]  # find piece at the possible location of rook
                    if endPiece == '--':
                        # if space is empty
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        # if piece is of enemy,append it and close the loop as rook can't jump over pieces
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        # friendly piece is at location, skip further search
                        break
                else:
                    # piece is off board
                    break

    def getBishopMoves(self, r, c, moves):
        # gets all possible bishop moves and append to moves variable
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # possible directions of bishop move (all diagonals)

        enemyColor = 'b' if self.whiteToMove else 'w'  # sets enemy color regarding which player has the turn

        for d in directions:
            for i in range(1, 8):
                # sets total distance bishop can travel, one step at a time
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                    endPiece = self.board[endRow, endCol]  # find piece at the possible location of bishop
                    if endPiece == '--':
                        # if space is empty
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        # if piece is of enemy,append it and close the loop as bishop can't jump over pieces
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        # friendly piece is at location, skip further search
                        break
                else:
                    # piece is off board
                    break

    def getKnightMoves(self, r, c, moves):
        # gets all possible knight moves and append to moves variable

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1),
                       (2, 1))  # possible directions of knight move (L-shaped)

        allyColor = 'w' if self.whiteToMove else 'b'  # sets ally color for 1 less if statement

        for k in knightMoves:
            # sets total cells knight can travel
            endRow = r + k[0]
            endCol = c + k[1]
            if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                endPiece = self.board[endRow, endCol]  # find piece at the possible location of knight
                if endPiece[0] != allyColor:
                    # if piece is of an ally, don't append , as knight can jump over pieces
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        # gets all possible queen moves and append to moves variable
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
        # as queen movement is combination of bishop and rook

    def getKingMoves(self, r, c, moves):
        # gets all possible king moves and append to moves variable

        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        # all possible king movement directions

        allyColor = 'w' if self.whiteToMove else 'b'  # sets ally color
        for i in range(8):  # total king movement possibilities
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # piece is on the board , even after moving
                endPiece = self.board[endRow, endCol]  # fetching the piece on potential king move
                if endPiece[0] != allyColor:
                    # piece isn't an ally ( i.e. space is empty or an enemy piece )
                    moves.append(Move((r, c), (endRow, endCol), self.board))


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

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # unique move-id for each move

        # storing piece moved and piece captured(if any), for undoing if needed
        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]

    def __eq__(self, other):
        # defining comparison operator for moves comparison
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # returns chess notation for particular move
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        # returns rank/file using row and columns
        return self.colsToFiles[col] + self.rowsToRanks[row]
