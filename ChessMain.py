"""
main driver file.
Responsible for handling user input and displaying current gamestate
"""

import pygame as p
import ChessEngine

p.init()
WIDTH = HEIGHT = 512  # size of our board
DIMENSION = 8  # Dimension of our chess board is 8x8
SQ_SIZE = WIDTH // DIMENSION  # size of each square
MAX_FPS = 30

# initialize global directory of images .This will be called exactly once in the main
IMAGES = {}


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

    loadImages()

    sqSelected = ()  # stores  last click of user as tuple (x,y)
    playerClicks = []  # keeps track of player clicks ( 2 Tuples : ex, (6,4)->(4,4))

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:  # exits the game
                running = False
                break
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # x, y coordinate of mouse click
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                # determining which square user clicked

                if sqSelected == (row, col):
                    # user clicked on same square twice, i.e. it needed to be unselected
                    sqSelected = ()
                    playerClicks = []

                elif gs.board[row, col] != '--' or len(playerClicks) == 1:
                    # not allowing user to selected empty square
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    # once 2 clicks are made to move the piece, move the piece
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())  # print notation
                    gs.makeMove(move)
                    sqSelected = ()
                    playerClicks = []  # empty both variables for next use
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # if key entered is "z", undo moves
                    gs.undo()
        drawGameState(screen, gs)  # draw the board
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    # responsible for all  graphics with current game state

    drawBoard(screen)  # draw pieces on the screen
    drawPieces(screen, gs.board)


def drawBoard(screen):
    # Draw the board, top left cell is always white

    colors = [p.Color("white"), p.Color("grey")]
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


if __name__ == "__main__":
    main()