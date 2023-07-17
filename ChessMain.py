"""
main driver file.
Responsible for handling user input and displaying current gamestate
"""
import time

import pygame as p
import ChessEngine
import BestMoveFinder

p.init()
WIDTH = HEIGHT = 512  # size of our board
DIMENSION = 8  # Dimension of our chess board is 8x8
SQ_SIZE = WIDTH // DIMENSION  # size of each square
MAX_FPS = 30

# initialize global directory of images .This will be called exactly once in the main
IMAGES = {}

colors = [p.Color("white"), p.Color("grey")]


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
        # images can be accessed by IMAGES['wK']


def main():
    # main driver function , handles inputs and graphics update
    screen = p.display.set_mode((WIDTH, HEIGHT))  # set up the screen
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()  # gets valid move for current state
    moveMade = False  # flag variable to check if move is made for update of valid moves
    animate = False  # flag variable to check when to animate piece movement
    gameOver = False  # keeps track of game state, if game is over or not
    loadImages()
    sqSelected = ()  # stores  last click of user as tuple (x,y)
    playerClicks = []  # keeps track of player clicks ( 2 Tuples : ex, (6,4)->(4,4))

    # if a human is playing white,it'll be true, else if bot is playing, it'll be false
    playerOne = True
    playerTwo = False

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        if gs.checkMate:  # restart the game, once check mate or stalemate
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Win by CheckMate")
            else:
                drawText(screen, "Black Win by CheckMate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")

        for e in p.event.get():
            if e.type == p.QUIT:  # exits the game
                running = False
                break
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn:
                    location = p.mouse.get_pos()  # x, y coordinate of mouse click
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    # determining which square user clicked

                    if sqSelected == (row, col):
                        # user clicked on same square twice, i.e. it needed to be unselected
                        sqSelected = ()
                        playerClicks = []

                    elif gs.board[row, col] != '--' or len(playerClicks) == 1:
                        # not allowing user to select empty square
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        # once 2 clicks are made to move the piece, move the piece
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:  # if move is valid, make a move
                                print(move.getChessNotation())  # print notation
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []  # empty both variables for next use
                                break
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # if key entered is "z", undo moves
                    gs.undoMove()
                    animate = False
                    moveMade = True

                if e.key == p.K_r:
                    # if key entered is "r", undo moves
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if gameOver:  # if game is over, restart
            time.sleep(2)
            gs = ChessEngine.GameState()
            validMoves = gs.getValidMoves()
            sqSelected = ()
            playerClicks = []
            moveMade = False
            animate = False
        # AI move finder
        if not humanTurn:
            AIMove = BestMoveFinder.GreedyMove(gs, validMoves)
            if AIMove is None:
                AIMove = BestMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)  # draw the board
        clock.tick(MAX_FPS)
        p.display.flip()


def highlightSquares(screen, gs, validMoves, sqSelected):
    # highlighting the possible moves of a piece
    if sqSelected != ():
        # empty square is not selected
        row, column = sqSelected
        if gs.board[row, column][0] == ('w' if gs.whiteToMove else 'b'):  # sq selected is a piece of current player

            # highlight the selected square
            surface = p.Surface((SQ_SIZE, SQ_SIZE))  # setting up the surface
            surface.set_alpha(150)  # setting transparency ,0 = transparent, 255=opaque
            surface.fill((0, 0, 128))
            screen.blit(surface, (column * SQ_SIZE, row * SQ_SIZE))

            # highlight potential moves
            surface.fill((135, 206, 250))
            for move in validMoves:
                if move.startRow == row and move.startCol == column:
                    # all potential moves of selected piece
                    screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    # responsible for all  graphics with current game state

    drawBoard(screen)  # draw pieces on the screen
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    # Draw the board, top left cell is always white

    global colors

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            # every other cell has same color, i.e. sum of row and column will be even/ odd for each color
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    # draw the pieces using current gamestate

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r, c]
            if piece != '--':  # space is not empty
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    distanceRow = move.endRow - move.startRow
    distanceCol = move.endCol - move.startCol
    frameCount = 10  # frames per square

    for frame in range(frameCount + 1):
        r, c = (move.startRow + distanceRow * frame / frameCount, move.startCol + distanceCol * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase piece from ending square, which is being moved, as it is already moved in makeMove function
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw piece being captured into the square (if any)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece
        if move.pieceMoved in IMAGES:
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.Font(None, 36)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation)
    p.display.flip()


if __name__ == "__main__":
    main()
