# MAIN GAME LOOP

import pygame
from player import Player
from enemy import Enemy
from pathlib import Path

pygame.init()
GAME_FOLDER = Path(__file__).parent

win = pygame.display.set_mode((800, 450))
pygame.display.set_caption("BUG GAME")
clock = pygame.time.Clock()
score = 0

screenwidth = 800

background_path = (
    GAME_FOLDER / "assets" / "backgrounds" / "bg1.png"
)

bg = pygame.transform.scale(
    pygame.image.load(str(background_path)),
    (800, 450)
)

def redrawgamewindow():
  win.blit(bg, (0, 0))  
  man.draw(win)  
  goblin.draw(win)
  pygame.display.update()


# MAIN LOOP________________________
man = Player(300, 215, 64, 64)
goblin = Enemy(100, 220, 64, 64, 450)
run = True

while run:
  clock.tick(30)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  keys = pygame.key.get_pressed()

  if keys[pygame.K_LEFT] and man.x > man.vel:
    man.x -= man.vel
    man.left = True
    man.right = False

  elif keys[pygame.K_RIGHT] and man.x < screenwidth - man.width - man.vel:
    man.x += man.vel
    man.right = True
    man.left = False

  else:
    man.right = False
    man.left = False
    man.walkCount = 0

  if not man.isJump:
    if keys[pygame.K_SPACE]:
      man.isJump = True
      man.right = False
      man.left = False
      man.walkCount = 0
  else:
    if man.jumpCount >= -10:
      neg = 1
      if man.jumpCount < 0:
        neg = -1
      man.y -= (man.jumpCount**2) * 0.5 * neg
      man.jumpCount -= 1
    else:
      man.isJump = False
      man.jumpCount = 10

  redrawgamewindow()

pygame.quit()