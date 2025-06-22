# Star Pusher (a Sokoban clone), by Al Sweigart al@inventwithpython.com
# (Pygame) A puzzle game where you push the stars over their goals.

import random, sys, copy, os, pygame
from pygame.locals import *

FPS = 30  # frames per second to update the screen
WINWIDTH = 800
WINHEIGHT = 600
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40
CAM_MOVE_SPEED = 5

OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR    = BRIGHTBLUE
TEXTCOLOR  = WHITE

UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Star Pusher')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    IMAGESDICT = {
        'uncovered goal': pygame.image.load('RedSelector.png'),
        'covered goal':   pygame.image.load('Selector.png'),
        'star':           pygame.image.load('Star.png'),
        'corner':         pygame.image.load('Wall_Block_Tall.png'),
        'wall':           pygame.image.load('Wood_Block_Tall.png'),
        'inside floor':   pygame.image.load('Plain_Block.png'),
        'outside floor':  pygame.image.load('Grass_Block.png'),
        'title':          pygame.image.load('star_title.png'),
        'solved':         pygame.image.load('star_solved.png'),
        'princess':       pygame.image.load('princess.png'),
        'boy':            pygame.image.load('boy.png'),
        'catgirl':        pygame.image.load('catgirl.png'),
        'horngirl':       pygame.image.load('horngirl.png'),
        'pinkgirl':       pygame.image.load('pinkgirl.png'),
        'rock':           pygame.image.load('Rock.png'),
        'short tree':     pygame.image.load('Tree_Short.png'),
        'tall tree':      pygame.image.load('Tree_Tall.png'),
        'ugly tree':      pygame.image.load('Tree_Ugly.png')
    }

    TILEMAPPING = {
        'x': IMAGESDICT['corner'],
        '#': IMAGESDICT['wall'],
        'o': IMAGESDICT['inside floor'],
        ' ': IMAGESDICT['outside floor']
    }
    OUTSIDEDECOMAPPING = {
        '1': IMAGESDICT['rock'],
        '2': IMAGESDICT['short tree'],
        '3': IMAGESDICT['tall tree'],
        '4': IMAGESDICT['ugly tree']
    }

    currentImage = 0
    PLAYERIMAGES = [
        IMAGESDICT['princess'],
        IMAGESDICT['boy'],
        IMAGESDICT['catgirl'],
        IMAGESDICT['horngirl'],
        IMAGESDICT['pinkgirl']
    ]

    startScreen()

    levels = readLevelsFile('starPusherLevels.txt')
    currentLevelIndex = 0

    while True:
        result = runLevel(levels, currentLevelIndex)
        if result in ('solved', 'next'):
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels) - 1
        # 'reset' just reruns the same level


def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True

    levelSurf = BASICFONT.render(
        f'Level {levelNum+1} of {len(levels)}', True, TEXTCOLOR
    )
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)

    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - mapHeight // 2) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - mapWidth  // 2) + TILEHEIGHT

    levelIsComplete = False
    cameraOffsetX = cameraOffsetY = 0
    cameraUp = cameraDown = cameraLeft = cameraRight = False

    while True:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True
                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    currentImage = (currentImage + 1) % len(PLAYERIMAGES)
                    mapNeedsRedraw = True
            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo and not levelIsComplete:
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)
            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True
            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (
            HALF_WINWIDTH + cameraOffsetX,
            HALF_WINHEIGHT + cameraOffsetY
        )
        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render(f"Steps: {gameStateObj['stepCounter']}", True, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            # display "Level Complete" message for 3 seconds
            completeSurf = BASICFONT.render('Level Complete!', True, TEXTCOLOR)
            completeRect = completeSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))
            DISPLAYSURF.blit(completeSurf, completeRect)
            pygame.display.update()
            pygame.time.wait(3000)
            return 'next'

        pygame.display.update()
        FPSCLOCK.tick()


def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#', 'x'):
        return True
    return False


def decorateMap(mapObj, startxy):
    startx, starty = startxy
    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] == '#':
                if ((isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or
                    (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or
                    (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or
                    (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1))):
                    mapObjCopy[x][y] = 'x'
            elif (mapObjCopy[x][y] == ' ' and
                  random.randint(0, 99) < OUTSIDE_DECORATION_PCT):
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    if isWall(mapObj, x, y):
        return True
    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True
    elif (x, y) in gameStateObj['stars']:
        return True
    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    playerx, playery = gameStateObj['player']
    stars = gameStateObj['stars']
    if playerMoveTo == UP:
        xOff, yOff = 0, -1
    elif playerMoveTo == RIGHT:
        xOff, yOff = 1, 0
    elif playerMoveTo == DOWN:
        xOff, yOff = 0, 1
    elif playerMoveTo == LEFT:
        xOff, yOff = -1, 0

    if isWall(mapObj, playerx + xOff, playery + yOff):
        return False
    else:
        if (playerx + xOff, playery + yOff) in stars:
            if not isBlocked(mapObj, gameStateObj, playerx + 2*xOff, playery + 2*yOff):
                ind = stars.index((playerx + xOff, playery + yOff))
                stars[ind] = (stars[ind][0] + xOff, stars[ind][1] + yOff)
            else:
                return False
        gameStateObj['player'] = (playerx + xOff, playery + yOff)
        return True


def startScreen():
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    instructionText = [
        'Push the stars over the marks.',
        'Arrow keys to move, WASD for camera, P to change character.',
        'Backspace to reset level, Esc to quit.',
        'N for next level, B to go back a level.'
    ]

    DISPLAYSURF.fill(BGCOLOR)
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)
    for line in instructionText:
        instSurf = BASICFONT.render(line, True, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height
        DISPLAYSURF.blit(instSurf, instRect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_ESCAPE,):
                    terminate()
                return
        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), f'Cannot find level file: {filename}'
    content = open(filename, 'r').readlines() + ['\r\n']
    levels = []
    levelNum = 0
    mapTextLines = []
    mapObj = []
    for lineNum, rawLine in enumerate(content):
        line = rawLine.rstrip('\r\n')
        if ';' in line:
            line = line[:line.find(';')]
        if line != '':
            mapTextLines.append(line)
        elif mapTextLines:
            maxWidth = max(len(l) for l in mapTextLines)
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))
            for x in range(maxWidth):
                mapObj.append([])
            for y, textLine in enumerate(mapTextLines):
                for x, ch in enumerate(textLine):
                    mapObj[x].append(ch)

            startx = starty = None
            goals = []
            stars = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx, starty = x, y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))

            assert startx is not None, f'Level {levelNum+1} missing start @'
            assert goals, f'Level {levelNum+1} has no goals'
            assert len(stars) >= len(goals), \
                f'Level {levelNum+1} impossible: {len(goals)} goals, {len(stars)} stars'

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}
            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter
    if x < len(mapObj)-1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter)
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter)
    if y < len(mapObj[x])-1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter)
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter)


def drawMap(mapObj, gameStateObj, goals):
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect(
                x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT
            )
            cell = mapObj[x][y]
            if cell in TILEMAPPING:
                baseTile = TILEMAPPING[cell]
            else:
                baseTile = TILEMAPPING[' ']
            mapSurf.blit(baseTile, spaceRect)

            if cell in OUTSIDEDECOMAPPING:
                mapSurf.blit(OUTSIDEDECOMAPPING[cell], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            return False
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
