# Wormy, by Al Sweigart al@inventwithpython.com
# (Pygame) Lead the green snake around the screen eating red apples.

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR   = BLACK

UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'

HEAD = 0  # index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

def runGame():
    # start state
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [
        {'x': startx,     'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty}
    ]
    direction = RIGHT
    apple = getRandomLocation()
    paused = False

    while True:  # main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                elif not paused:
                    if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                        direction = LEFT
                    elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                        direction = RIGHT
                    elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                        direction = UP
                    elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                        direction = DOWN
                    elif event.key == K_ESCAPE:
                        terminate()

        if paused:
            drawPauseScreen()
            continue

        # check for collisions
        head = wormCoords[HEAD]
        if head['x'] == -1 or head['x'] == CELLWIDTH or head['y'] == -1 or head['y'] == CELLHEIGHT:
            return
        for segment in wormCoords[1:]:
            if segment['x'] == head['x'] and segment['y'] == head['y']:
                return

        # check for apple eaten
        if head['x'] == apple['x'] and head['y'] == apple['y']:
            apple = getRandomLocation()
        else:
            del wormCoords[-1]

        # move worm
        if direction == UP:
            newHead = {'x': head['x'], 'y': head['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': head['x'], 'y': head['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': head['x'] - 1, 'y': head['y']}
        elif direction == RIGHT:
            newHead = {'x': head['x'] + 1, 'y': head['y']}
        wormCoords.insert(0, newHead)

        # draw everything
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPauseScreen():
    pauseSurf = BASICFONT.render('Paused', True, WHITE)
    pauseRect = pauseSurf.get_rect()
    pauseRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(pauseSurf, pauseRect)
    pygame.display.update()
    FPSCLOCK.tick(5)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if not keyUpEvents:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)
    degrees1 = degrees2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotated1 = pygame.transform.rotate(titleSurf1, degrees1)
        rect1 = rotated1.get_rect()
        rect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotated1, rect1)

        rotated2 = pygame.transform.rotate(titleSurf2, degrees2)
        rect2 = rotated2.get_rect()
        rect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotated2, rect2)

        drawPressKeyMsg()
        if checkForKeyPress():
            pygame.event.get()
            return

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3
        degrees2 += 7

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1),
            'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 35)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get()
            return

def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorm(coords):
    for coord in coords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        segmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, segmentRect)
        innerRect = pygame.Rect(x+4, y+4, CELLSIZE-8, CELLSIZE-8)
        pygame.draw.rect(DISPLAYSURF, GREEN, innerRect)

def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

if __name__ == '__main__':
    main()
