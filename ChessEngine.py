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

        # variable for pins and checks
        self.inCheck = False
        self.pins = []  # pinned pieces to the king
        self.checks = []  # enemy square that gave the check
        self.checkMate = False
        self.staleMate = False

        self.enpassantPossible = ()  # coordinates of square, where enpassant is possible

        # variable to store castling rights
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightLog = [
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                         self.currentCastlingRight.bqs)]

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
            # piece moved was black king
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.pawnPromotion:
            self.board[move.endRow, move.endCol] = move.pieceMoved[0] + 'Q'

        # Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow, move.endCol] = '--'  # capturing the pawn

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle
                self.board[move.endRow, move.endCol - 1] = self.board[move.endRow, move.endCol + 1]  # moves the rook
                self.board[move.endRow, move.endCol + 1] = '--'  # removes duplicate rook
            else:
                # queen side castle
                self.board[move.endRow, move.endCol + 1] = self.board[move.endRow, move.endCol - 2]  # moves the rook
                self.board[move.endRow, move.endCol - 2] = '--'  # removes duplicate rook

        # update castling rights -whenever king or rook is moved
        self.updateCastleRights(move)
        self.castleRightLog.append(
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                         self.currentCastlingRight.bqs))

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

            if move.isEnpassantMove:
                # undo Enpassant
                self.board[move.endRow, move.endCol] = '--'
                self.board[move.startRow, move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # undo 2 pawn move
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castle rights
            self.castleRightLog.pop()  # removing last castle rights
            self.currentCastlingRight = self.castleRightLog[-1]
            # updating caste rights to the last castle rights before move

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    # king side castle
                    self.board[move.endRow, move.endCol + 1] = self.board[move.endRow, move.endCol - 1]
                    self.board[move.endRow, move.endCol - 1] = '--'
                else:  # queen side castle
                    self.board[move.endRow, move.endCol - 2] = self.board[move.endRow, move.endCol + 1]
                    self.board[move.endRow, move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':  # check if king was moved to remove all castling rights
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':  # check if king was moved to remove all castling rights
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        elif move.pieceMoved == 'wR':  # if rook was moved, which side castling is not possible
            if move.startRow == 7:
                if move.endRow == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                if move.endRow == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.endRow == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                if move.endRow == 7:  # right rook
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        # all moves considering checks, i.e.to check if the piece movement gets king a check.

        moves = self.getAllPossibleMoves()

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        # setting up  king's location to evaluate moves
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            # if king is in check
            if len(self.checks) == 1:  # only 1 piece is giving the checks,i.e. block check or move king
                moves = self.getAllPossibleMoves()
                # to block check, piece must be moved between king and attacking piece
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow, checkCol]  # finding piece checking the king
                validSquares = []

                # if knight gives a check, capture the knight or move the king, rest pieces' checks can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        # direction of attacking piece to block check
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            # once you get to piece & checks
                            break

                # get rid of all moves that don't move king or block check
                for i in range(len(moves) - 1, -1, -1):  # going backwards while deleting from list
                    if moves[i].pieceMoved[1] != 'K':
                        # if piece moved wasn't king, check must be blocked, or piece must be captured
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            # if move doesn't stop check, remove it from list
                            moves.remove(moves[i])

            else:
                # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            # if king isn't in check, then all moves are valid
            moves = self.getAllPossibleMoves()
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    def getAllPossibleMoves(self):
        # Get piece's all possible moves
        moves = []  # stores all possible moves
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

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):  # iterating through pins in reverse order
            if self.pins[i][0] == r and self.pins[i][1] == c:
                # checking if current piece is pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'

        pawnPromotion = False

        if self.board[r + moveAmount, c] == '--':  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r + moveAmount == backRow:  # if piece gets to back rank, it's a promotion
                    pawnPromotion = True
                moves.append(Move((r, c), (r + moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r + 2 * moveAmount, c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))

        if c - 1 >= 0:  # captures to the left , to check if piece don't go overboard
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount, c - 1][0] == enemyColor:  # enemy's piece to capture
                    if r + moveAmount == backRow:  # if piece gets to back rank, it's a promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))

        if c + 1 <= 7:  # captures to the right , to check if piece don't go overboard
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount, c + 1][0] == enemyColor:  # enemy's piece to capture
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        # gets all possible rook moves and append to moves variable

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):  # iterating through pins in reverse order
            if self.pins[i][0] == r and self.pins[i][1] == c:
                # checking if current piece is pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    # we use 2 function for finding valid moves for queen
                    # can't pin queen from pin on rook moves,only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # possible directions of rook move (up,left, down, right)

        enemyColor = 'b' if self.whiteToMove else 'w'  # sets enemy color regarding which player has the turn

        for d in directions:
            for i in range(1, 8):
                # sets total distance rook can travel, one step at a time
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        # to check if piece's mobility is compromised in both directions
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

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):  # iterating through pins in reverse order
            if self.pins[i][0] == r and self.pins[i][1] == c:
                # checking if current piece is pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # possible directions of bishop move (all diagonals)

        enemyColor = 'b' if self.whiteToMove else 'w'  # sets enemy color regarding which player has the turn

        for d in directions:
            for i in range(1, 8):
                # sets total distance bishop can travel, one step at a time
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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

        piecePinned = False

        for i in range(len(self.pins) - 1, -1, -1):  # iterating through pins in reverse order
            if self.pins[i][0] == r and self.pins[i][1] == c:
                # checking if current piece is pinned
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1),
                       (2, 1))  # possible directions of knight move (L-shaped)

        allyColor = 'w' if self.whiteToMove else 'b'  # sets ally color for 1 less if statement

        for k in knightMoves:
            # sets total cells knight can travel
            endRow = r + k[0]
            endCol = c + k[1]
            if 0 <= endCol < 8 and 0 <= endRow < 8:  # to confirm piece don't move out of board
                if not piecePinned:
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

                    # places king on end square to check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)

                    inCheck, pins, checks = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

                    # placing king on original square
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
            self.getCastleMoves(r, c, moves, allyColor)

    def checkForPinsAndChecks(self):
        pins = []  # pinned pieces to the king
        checks = []  # enemy square that gave the check
        inCheck = False

        # setting up ally and enemy color and which king's location to evaluate considering the turns
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # checking outwards from king in all direction for pins and checks, keeping track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            possiblePins = ()  # reset possible pins

            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # keeps possible cells within board limit
                    endPiece = self.board[endRow, endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePins == ():  # 1st allied piece could be pinned
                            possiblePins = (endRow, endCol, d[0], d[1])
                        else:
                            # 2nd allied piece is present, i.e. no piece is pinned
                            break
                    elif endPiece[0] == enemyColor:
                        # piece if of enemy, i.e. king is in direct check

                        typeOfPiece = endPiece[1]  # type of piece giving the check
                        # Here are 5 possibilities here:
                        # 1. Orthogonally away from king and piece is rook
                        # 2.Diagonally away from king and piece is bishop
                        # 3.One square diagonally away from king & piece is pawn
                        # 4.Any direction and piece is queen
                        # 5. Any direction 1 square away and piece is a king
                        # (to prevent king movement in square controlled by another king)
                        if ((0 <= j <= 3) and typeOfPiece == 'R') or (4 <= j <= 7 and typeOfPiece == 'B') or (
                                i == 1 and typeOfPiece == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (
                                enemyColor == 'b' and 4 <= j <= 5))) or typeOfPiece == 'Q' or (
                                i == 1 and typeOfPiece == "K"):
                            if possiblePins == ():
                                # no piece to prevent the check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                # piece blocking the check
                                pins.append(possiblePins)
                                break
                        else:
                            # enemy piece not applying check
                            break
                else:
                    # off board
                    break

        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                # check for off board movements
                endPiece = self.board[endRow, endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacks the king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def getCastleMoves(self, r, c, moves, allyColor):
        # gets all possible castle moves, & add item to moves list

        if self.inCheck:
            # can't castle if king is in check
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            # white/black king has king castling rights
            self.kingSideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            # white/black king has queen castling rights
            self.queenSideCastleMoves(r, c, moves, allyColor)

    def kingSideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r, c + 1] == '--' and self.board[r, c + 2] == '--':
            # both squares empty
            # places king on end square to check for checks
            if allyColor == 'w':
                self.whiteKingLocation = (r, c + 1)
            else:
                self.blackKingLocation = (r, c + 1)
            inCheck1, pins1, checks1 = self.checkForPinsAndChecks()
            if allyColor == 'w':
                self.whiteKingLocation = (r, c + 2)
            else:
                self.blackKingLocation = (r, c + 2)
            inCheck2, pins2, checks2 = self.checkForPinsAndChecks()
            if not inCheck1 and not inCheck2:
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

            if allyColor == 'w':
                # setting up king's location to its original one
                self.whiteKingLocation = (r, c)
            else:
                self.blackKingLocation = (r, c)

    def queenSideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r, c - 1] == '--' and self.board[r, c - 2] == '--' and self.board[r, c - 3] == '--':
            # both squares empty
            # places king on end square to check for checks
            if allyColor == 'w':
                self.whiteKingLocation = (r, c - 1)
            else:
                self.blackKingLocation = (r, c - 1)
            inCheck1, pins1, checks1 = self.checkForPinsAndChecks()

            if allyColor == 'w':
                self.whiteKingLocation = (r, c - 2)
            else:
                self.blackKingLocation = (r, c - 2)
            inCheck2, pins2, checks2 = self.checkForPinsAndChecks()

            if not inCheck1 and not inCheck2:
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

            if allyColor == 'w':
                # setting up king's location to its original one
                self.whiteKingLocation = (r, c)
            else:
                self.blackKingLocation = (r, c)


class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    # mapping ranks to their respective rows
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    # mapping  rows in board to their respective ranks
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # mapping files to their respective columns
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    # mapping column  to their respective files
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, pawnPromotion=False, isEnpassantMove=False, isCastleMove=False):
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

        # information about pawn promotion
        self.pawnPromotion = pawnPromotion

        # Enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        # castle move
        self.isCastleMove = isCastleMove

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
