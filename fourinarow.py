# Four-In-A-Row, by Al Sweigart al@inventwithpython.com
# (Pygame) Play against the computer, dropping tiles to connect four.

import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7   # how many spaces wide the board is
BOARDHEIGHT = 6  # how many spaces tall the board is
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

DIFFICULTY = 2   # how many moves to look ahead. (>2 is usually too much)

SPACESIZE = 50   # size of the tokens and board spaces in pixels

FPS = 30         # frames per second to update the screen
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE      = (255, 255, 255)

BGCOLOR   = BRIGHTBLUE
TEXTCOLOR = WHITE

RED    = 'red'
BLACK  = 'black'
EMPTY  = None
HUMAN  = 'human'
COMPUTER = 'computer'

# Current turn indicator
CURRENTTURN = None

def main():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT
    global REDTOKENIMG, BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT
    global HUMANWINNERIMG, COMPUTERWINNERIMG, TIEWINNERIMG, WINNERRECT, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Four in a Row')

    REDPILERECT = pygame.Rect(int(SPACESIZE/2), WINDOWHEIGHT - int(3*SPACESIZE/2), SPACESIZE, SPACESIZE)
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3*SPACESIZE/2), WINDOWHEIGHT - int(3*SPACESIZE/2), SPACESIZE, SPACESIZE)

    REDTOKENIMG = pygame.image.load('4row_red.png')
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load('4row_black.png')
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load('4row_board.png')
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load('4row_humanwinner.png')
    COMPUTERWINNERIMG = pygame.image.load('4row_computerwinner.png')
    TIEWINNERIMG = pygame.image.load('4row_tie.png')
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH/2), int(WINDOWHEIGHT/2))

    ARROWIMG = pygame.image.load('4row_arrow.png')
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery

    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)

    isFirstGame = True
    while True:
        runGame(isFirstGame)
        isFirstGame = False

def runGame(isFirstGame):
    global CURRENTTURN

    if isFirstGame:
        turn = COMPUTER
        showHelp = True
    else:
        if random.randint(0, 1) == 0:
            turn = COMPUTER
        else:
            turn = HUMAN
        showHelp = False

    mainBoard = getNewBoard()

    while True:  # main game loop
        CURRENTTURN = turn

        if turn == HUMAN:
            getHumanMove(mainBoard, showHelp)
            if showHelp:
                showHelp = False
            if isWinner(mainBoard, RED):
                winnerImg = HUMANWINNERIMG
                break
            turn = COMPUTER
        else:
            column = getComputerMove(mainBoard)
            animateComputerMoving(mainBoard, column)
            makeMove(mainBoard, BLACK, column)
            if isWinner(mainBoard, BLACK):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = HUMAN

        if isBoardFull(mainBoard):
            winnerImg = TIEWINNERIMG
            break

    while True:
        drawBoard(mainBoard)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return

def makeMove(board, player, column):
    lowest = getLowestEmptySpace(board, column)
    if lowest != -1:
        board[column][lowest] = player

def drawBoard(board, extraToken=None):
    DISPLAYSURF.fill(BGCOLOR)

    # Display current player's turn
    if CURRENTTURN is not None:
        turnText = 'Player' if CURRENTTURN == HUMAN else 'Computer'
        turnSurf = BASICFONT.render('Turn: ' + turnText, True, TEXTCOLOR)
        turnRect = turnSurf.get_rect()
        turnRect.topleft = (10, 10)
        DISPLAYSURF.blit(turnSurf, turnRect)

    # draw existing tokens
    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + x*SPACESIZE, YMARGIN + y*SPACESIZE)
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    # draw the token being dropped or dragged
    if extraToken:
        if extraToken['color'] == RED:
            DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
        elif extraToken['color'] == BLACK:
            DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    # draw the board overlay
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + x*SPACESIZE, YMARGIN + y*SPACESIZE)
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    # draw token piles
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT)
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT)

def getNewBoard():
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY] * BOARDHEIGHT)
    return board

def getHumanMove(board, isFirstMove):
    draggingToken = False
    tokenx = tokeny = None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                draggingToken = True
                tokenx, tokeny = event.pos
            elif event.type == MOUSEMOTION and draggingToken:
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, column):
                        animateDroppingToken(board, column, RED)
                        board[column][getLowestEmptySpace(board, column)] = RED
                        drawBoard(board)
                        pygame.display.update()
                        return
                tokenx = tokeny = None
                draggingToken = False
        if tokenx is not None and tokeny is not None:
            drawBoard(board, {'x': tokenx - SPACESIZE//2,
                              'y': tokeny - SPACESIZE//2,
                              'color': RED})
        else:
            drawBoard(board)

        if isFirstMove:
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

        pygame.display.update()
        FPSCLOCK.tick()

def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 1.0
    targetRow = getLowestEmptySpace(board, column)
    while True:
        y += int(dropSpeed)
        dropSpeed += 0.5
        if int((y - YMARGIN) / SPACESIZE) >= targetRow:
            return
        drawBoard(board, {'x': x, 'y': y, 'color': color})
        pygame.display.update()
        FPSCLOCK.tick()

def animateComputerMoving(board, column):
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    speed = 1.0
    while y > YMARGIN - SPACESIZE:
        y -= int(speed)
        speed += 0.5
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    y = YMARGIN - SPACESIZE
    speed = 1.0
    while x > XMARGIN + column * SPACESIZE:
        x -= int(speed)
        speed += 0.5
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)

def getComputerMove(board):
    potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)
    bestFitness = -1
    for i in range(BOARDWIDTH):
        if potentialMoves[i] > bestFitness and isValidMove(board, i):
            bestFitness = potentialMoves[i]
    bestCols = [i for i in range(BOARDWIDTH)
                if potentialMoves[i] == bestFitness and isValidMove(board, i)]
    return random.choice(bestCols)

def getPotentialMoves(board, tile, lookAhead):
    if lookAhead == 0 or isBoardFull(board):
        return [0] * BOARDWIDTH
    enemy = RED if tile == BLACK else BLACK
    scores = [0] * BOARDWIDTH
    for move in range(BOARDWIDTH):
        dupe = copy.deepcopy(board)
        if not isValidMove(dupe, move):
            continue
        makeMove(dupe, tile, move)
        if isWinner(dupe, tile):
            scores[move] = 1
            break
        if isBoardFull(dupe):
            scores[move] = 0
        else:
            for cm in range(BOARDWIDTH):
                dupe2 = copy.deepcopy(dupe)
                if not isValidMove(dupe2, cm):
                    continue
                makeMove(dupe2, enemy, cm)
                if isWinner(dupe2, enemy):
                    scores[move] = -1
                    break
                else:
                    results = getPotentialMoves(dupe2, tile, lookAhead - 1)
                    scores[move] += sum(results) / BOARDWIDTH**2
    return scores

def getLowestEmptySpace(board, column):
    for y in range(BOARDHEIGHT-1, -1, -1):
        if board[column][y] is EMPTY:
            return y
    return -1

def isValidMove(board, column):
    return 0 <= column < BOARDWIDTH and board[column][0] is EMPTY

def isBoardFull(board):
    return all(board[x][y] is not EMPTY for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT))

def isWinner(board, tile):
    # horizontal
    for x in range(BOARDWIDTH-3):
        for y in range(BOARDHEIGHT):
            if all(board[x+i][y] == tile for i in range(4)):
                return True
    # vertical
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT-3):
            if all(board[x][y+i] == tile for i in range(4)):
                return True
    # diag /
    for x in range(BOARDWIDTH-3):
        for y in range(3, BOARDHEIGHT):
            if all(board[x+i][y-i] == tile for i in range(4)):
                return True
    # diag \
    for x in range(BOARDWIDTH-3):
        for y in range(BOARDHEIGHT-3):
            if all(board[x+i][y+i] == tile for i in range(4)):
                return True
    return False

if __name__ == '__main__':
    main()
