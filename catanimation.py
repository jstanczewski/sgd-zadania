import pygame
import sys
from pygame.locals import *

# Inicjalizacja Pygame i ustawienie zegara
pygame.init()
FPS = 30
fpsClock = pygame.time.Clock()

# Ustawienia okna
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Animation')

# Kolor tła i wczytanie obrazków kotów
WHITE = (255, 255, 255)
catImg = pygame.image.load('cat.png')
cat2Img = pygame.image.load('cat.png')

# Parametry kotów: pozycja i wektor ruchu
cat1 = {'x': 10, 'y': 10, 'dir_x': 5, 'dir_y': 0}
cat2 = {'x': 300, 'y': 200, 'dir_x': 0, 'dir_y': 5}

# Główna pętla gry
while True:
    DISPLAYSURF.fill(WHITE)

    # Aktualizacja pozycji kotów
    cat1['x'] += cat1['dir_x']
    cat1['y'] += cat1['dir_y']
    cat2['x'] += cat2['dir_x']
    cat2['y'] += cat2['dir_y']

    # Odbicia od krawędzi dla pierwszego kota
    if cat1['x'] <= 0 or cat1['x'] + catImg.get_width() >= WINDOW_WIDTH:
        cat1['dir_x'] *= -1
    if cat1['y'] <= 0 or cat1['y'] + catImg.get_height() >= WINDOW_HEIGHT:
        cat1['dir_y'] *= -1

    # Odbicia od krawędzi dla drugiego kota
    if cat2['x'] <= 0 or cat2['x'] + cat2Img.get_width() >= WINDOW_WIDTH:
        cat2['dir_x'] *= -1
    if cat2['y'] <= 0 or cat2['y'] + cat2Img.get_height() >= WINDOW_HEIGHT:
        cat2['dir_y'] *= -1

    # Rysowanie kotów na ekranie
    DISPLAYSURF.blit(catImg, (cat1['x'], cat1['y']))
    DISPLAYSURF.blit(cat2Img, (cat2['x'], cat2['y']))

    # Obsługa zdarzeń (zamknięcie okna)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Aktualizacja ekranu i limit klatek
    pygame.display.update()
    fpsClock.tick(FPS)
