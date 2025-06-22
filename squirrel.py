# Squirrel Eat Squirrel, by Al Sweigart al@inventwithpython.com
# (Pygame) A game where squirrels eat each other and grow monstrously large.

import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30                    # base frames per second
WINWIDTH = 640
WINHEIGHT = 480
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (24, 255, 0)
WHITE      = (255, 255, 255)
RED        = (255,   0,   0)

# Level-up constants
LEVELUPTIME     = 2        # seconds to display "Level Up!"
SPEED_INCREMENT = 5        # increase in FPS each level

CAMERASLACK  = 90
MOVERATE     = 9
BOUNCERATE   = 6
BOUNCEHEIGHT = 30
STARTSIZE    = 25
WINSIZE      = 300
INVULNTIME   = 2
GAMEOVERTIME = 4
MAXHEALTH    = 3

NUMGRASS         = 80
NUMSQUIRRELS     = 30
SQUIRRELMINSPEED = 3
SQUIRRELMAXSPEED = 7
DIRCHANGEFREQ    = 2

LEFT  = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Squirrel Eat Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    L_SQUIR_IMG = pygame.image.load('squirrel.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = [pygame.image.load(f'grass{i}.png') for i in range(1, 5)]

    while True:
        runGame()

def runGame():
    # Game state flags and timers
    invulnerableMode    = False
    invulnerableStart   = 0
    gameOverMode        = False
    gameOverStart       = 0
    winMode             = False

    # Level-up state
    score               = 0
    gameSpeed           = FPS
    levelUpMode         = False
    levelUpStart        = 0

    # Prepare game-over and win surfaces
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))
    winSurf      = BASICFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE)
    winRect      = winSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))
    winSurf2     = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2     = winSurf2.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT + 30))

    camerax = cameray = 0
    grassObjs    = []
    squirrelObjs = []
    playerObj = {
        'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
        'facing': LEFT,
        'size': STARTSIZE,
        'x': HALF_WINWIDTH,
        'y': HALF_WINHEIGHT,
        'bounce': 0,
        'health': MAXHEALTH
    }

    moveLeft = moveRight = moveUp = moveDown = False

    # Initial grass
    for i in range(10):
        grass = makeNewGrass(camerax, cameray)
        grass['x'] = random.randint(0, WINWIDTH)
        grass['y'] = random.randint(0, WINHEIGHT)
        grassObjs.append(grass)

    while True:
        # End invulnerability
        if invulnerableMode and time.time() - invulnerableStart > INVULNTIME:
            invulnerableMode = False

        # Move enemy squirrels
        for sObj in squirrelObjs:
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] = (sObj['bounce'] + 1) % (sObj['bouncerate'] + 1)
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'], sObj['movey'] = getRandomVelocity(), getRandomVelocity()
                img = R_SQUIR_IMG if sObj['movex'] > 0 else L_SQUIR_IMG
                sObj['surface'] = pygame.transform.scale(img, (sObj['width'], sObj['height']))

        # Remove off-screen objects
        grassObjs    = [g for g in grassObjs if not isOutsideActiveArea(camerax, cameray, g)]
        squirrelObjs = [s for s in squirrelObjs if not isOutsideActiveArea(camerax, cameray, s)]

        # Add grass & squirrels
        while len(grassObjs)    < NUMGRASS:    grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS: squirrelObjs.append(makeNewSquirrel(camerax, cameray))

        # Camera follow
        pcx = playerObj['x'] + playerObj['size']//2
        pcy = playerObj['y'] + playerObj['size']//2
        if pcx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = pcx - (HALF_WINWIDTH + CAMERASLACK)
        elif (camerax + HALF_WINWIDTH) - pcx > CAMERASLACK:
            camerax = pcx + CAMERASLACK - HALF_WINWIDTH
        if pcy - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = pcy - (HALF_WINHEIGHT + CAMERASLACK)
        elif (cameray + HALF_WINHEIGHT) - pcy > CAMERASLACK:
            cameray = pcy + CAMERASLACK - HALF_WINHEIGHT

        # Draw background
        DISPLAYSURF.fill(GRASSCOLOR)
        for gObj in grassObjs:
            gRect = pygame.Rect(gObj['x']-camerax, gObj['y']-cameray, gObj['width'], gObj['height'])
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # Draw enemy squirrels
        for sObj in squirrelObjs:
            bounceAmt = getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight'])
            sObj['rect'] = pygame.Rect(sObj['x']-camerax, sObj['y']-cameray-bounceAmt, sObj['width'], sObj['height'])
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        # Draw player
        flashOn = round(time.time(),1)*10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashOn):
            pbounce = getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT)
            playerObj['rect'] = pygame.Rect(playerObj['x']-camerax,
                                            playerObj['y']-cameray-pbounce,
                                            playerObj['size'], playerObj['size'])
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])

        # Draw health meter
        drawHealthMeter(playerObj['health'])

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown=False; moveUp=True
                elif event.key in (K_DOWN, K_s):
                    moveUp=False; moveDown=True
                elif event.key in (K_LEFT, K_a):
                    moveRight=False; moveLeft=True
                    if playerObj['facing']!=LEFT:
                        playerObj['surface']=pygame.transform.scale(L_SQUIR_IMG,(playerObj['size'],playerObj['size']))
                    playerObj['facing']=LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft=False; moveRight=True
                    if playerObj['facing']!=RIGHT:
                        playerObj['surface']=pygame.transform.scale(R_SQUIR_IMG,(playerObj['size'],playerObj['size']))
                    playerObj['facing']=RIGHT
                elif winMode and event.key==K_r:
                    return
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a):   moveLeft=False
                elif event.key in (K_RIGHT, K_d): moveRight=False
                elif event.key in (K_UP, K_w):    moveUp=False
                elif event.key in (K_DOWN, K_s):  moveDown=False
                elif event.key == K_ESCAPE:       terminate()

        # Pause game-over display
        if gameOverMode:
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStart > GAMEOVERTIME:
                return
        else:
            # Move player
            if moveLeft:  playerObj['x'] -= MOVERATE
            if moveRight: playerObj['x'] += MOVERATE
            if moveUp:    playerObj['y'] -= MOVERATE
            if moveDown:  playerObj['y'] += MOVERATE
            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce']!=0:
                playerObj['bounce']=(playerObj['bounce']+1)%(BOUNCERATE+1)

            # Collision with squirrels
            for i in range(len(squirrelObjs)-1, -1, -1):
                sObj = squirrelObjs[i]
                if 'rect' in sObj and playerObj['rect'].colliderect(sObj['rect']):
                    if sObj['width']*sObj['height'] <= playerObj['size']**2:
                        score += 1
                        playerObj['size'] += int((sObj['width']*sObj['height'])**0.2) + 1
                        del squirrelObjs[i]
                        # Level up on every 5th squirrel
                        if score % 5 == 0:
                            levelUpMode = True
                            levelUpStart = time.time()
                            gameSpeed += SPEED_INCREMENT
                        # Update player image size
                        img = L_SQUIR_IMG if playerObj['facing']==LEFT else R_SQUIR_IMG
                        playerObj['surface'] = pygame.transform.scale(img, (playerObj['size'], playerObj['size']))
                        if playerObj['size'] > WINSIZE:
                            winMode = True
                    elif not invulnerableMode:
                        invulnerableMode = True
                        invulnerableStart = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode  = True
                            gameOverStart = time.time()

        # Win display
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        # Display "Level Up" message
        if levelUpMode:
            lvlSurf = BASICFONT.render('Level Up!', True, RED)
            lvlRect = lvlSurf.get_rect(center=(HALF_WINWIDTH, HALF_WINHEIGHT))
            DISPLAYSURF.blit(lvlSurf, lvlRect)
            if time.time() - levelUpStart > LEVELUPTIME:
                levelUpMode = False

        pygame.display.update()
        FPSCLOCK.tick(gameSpeed)

def drawHealthMeter(currentHealth):
    for i in range(currentHealth):
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10*MAXHEALTH) - i*10, 20, 10))
    for i in range(MAXHEALTH):
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10*MAXHEALTH) - i*10, 20, 10), 1)

def terminate():
    pygame.quit()
    sys.exit()

def getBounceAmount(curBounce, bounceRate, bounceHeight):
    return int(math.sin((math.pi/float(bounceRate))*curBounce) * bounceHeight)

def getRandomVelocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    return speed if random.randint(0,1)==0 else -speed

def getRandomOffCameraPos(cx, cy, w, h):
    camRect = pygame.Rect(cx, cy, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(cx-WINWIDTH, cx+2*WINWIDTH)
        y = random.randint(cy-WINHEIGHT, cy+2*WINHEIGHT)
        objRect = pygame.Rect(x, y, w, h)
        if not objRect.colliderect(camRect):
            return x, y

def makeNewSquirrel(cx, cy):
    sq = {}
    size0 = random.randint(5,25)
    mult  = random.randint(1,3)
    sq['width']  = (size0 + random.randint(0,10)) * mult
    sq['height'] = (size0 + random.randint(0,10)) * mult
    sq['x'], sq['y'] = getRandomOffCameraPos(cx, cy, sq['width'], sq['height'])
    sq['movex'], sq['movey'] = getRandomVelocity(), getRandomVelocity()
    img = R_SQUIR_IMG if sq['movex']>0 else L_SQUIR_IMG
    sq['surface'] = pygame.transform.scale(img, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10,18)
    sq['bounceheight'] = random.randint(10,50)
    return sq

def makeNewGrass(cx, cy):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES)-1)
    gr['width']  = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(cx, cy, gr['width'], gr['height'])
    return gr

def isOutsideActiveArea(cx, cy, obj):
    left = cx - WINWIDTH
    top  = cy - WINHEIGHT
    bounds = pygame.Rect(left, top, WINWIDTH*3, WINHEIGHT*3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not bounds.colliderect(objRect)

if __name__ == '__main__':
    main()
