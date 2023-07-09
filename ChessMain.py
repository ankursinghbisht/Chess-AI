"""
main driver file.
Responsible for handling user input and displaying current gamestate
"""

import pygame as p
import numpy as np
import ChessEngine

p.init()
WIDTH = HEIGHT = 512  # size of our board
DIMENSION = 8  # Dimension of our chess board is 8x8
SQ_SIZE = WIDTH // DIMENSION  # size of each square
MAX_FPS = 15

# initialize global directory of images .This will be called exactly once in the main
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
        # images can be accessed by IMAGES['wK']


# main driver function , handles inputs and graphics update
"""
def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))  # set up the screen
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages()

    dragging = False  # Flag to track if a piece is being dragged
    selected_piece = None  # Stores the selected piece being dragged
    selected_square = ()  # Stores the initial position of the selected piece
    playerClicks = []  # Keeps track of player clicks (2 Tuples: ex, (6, 4) -> (4, 4))

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not dragging:
                    location = p.mouse.get_pos()  # x, y coordinate of mouse click
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    selected_square = (row, col)
                    selected_piece = gs.board[row, col]
                    playerClicks.append(selected_square)
                    dragging = True
            elif e.type == p.MOUSEBUTTONUP:
                if dragging:
                    location = p.mouse.get_pos()  # x, y coordinate of mouse release
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if (row, col) != selected_square:
                        playerClicks.append((row, col))
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        gs.makeMove(move)
                    selected_piece = None
                    selected_square = ()
                    playerClicks = []
                    dragging = False

            if dragging:
                # Draw the piece being dragged at the current mouse position
                mouse_pos = p.mouse.get_pos()
                screen.blit(IMAGES[selected_piece], p.Rect(mouse_pos[0]- SQ_SIZE / 2, mouse_pos[1] - SQ_SIZE / 2, SQ_SIZE, SQ_SIZE))
            else:
                drawGameState(screen, gs)

        clock.tick(MAX_FPS)
        p.display.flip()

"""


def main():
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
            if e.type == p.QUIT:
                running = False
                break
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # x, y coordinate of mouse click
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                # determining which square user clicked

                if sqSelected == (row, col):  # user clicked on same square twice, ie. it needed to be unselected
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    gs.makeMove(move)
                    sqSelected = ()
                    playerClicks = []

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()




# responsible for all  graphics with current game state
def drawGameState(screen, gs):
    drawBoard(screen)  # draw pieces on the screen
    drawPieces(screen, gs.board)


# Draw the board, top left cell is always white
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draw the pieces using current gamestate
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r, c]
            if piece != '--':  # space is not empty
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
