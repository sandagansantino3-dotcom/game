# MAIN GAME LOOP

import pygame
from player import Player
from enemy import Enemy

pygame.init()

win = pygame.display.set_mode((800, 450))
pygame.display.set_caption("BUG GAME")

clock = pygame.time.Clock()

score = 0

class player(object): # player class

  def __init__(self, x, y, width, height):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.vel = 5
    self.isJump = False
    self.jumpCount = 10
    self.left = False
    self.right = False
    self.walkCount = 0
    self.health = 10
    self.max_health = 10

  def draw(self, win):  
    if self.walkCount + 1 >= 27:
      self.walkCount = 0

    if self.left:
      win.blit(walkLeft[self.walkCount // 3], (self.x, self.y))
      self.walkCount += 1

    elif self.right:
      win.blit(walkRight[self.walkCount // 3], (self.x, self.y))
      self.walkCount += 1

    else:
      win.blit(char, (self.x, self.y))

    bar_width = 50
    bar_height = 10
    bar_x = self.x + (self.width // 2) - (bar_width // 2)
    bar_y = self.y - 15
    pygame.draw.rect(win, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(win, (0, 128, 0), (bar_x, bar_y, int(bar_width * (self.health / self.max_health)), bar_height))

class enemy(object): # Class enemy
  walkRight = [pygame.image.load('assets/enemy/R1E.png'), 
               pygame.image.load('assets/enemy/R2E.png'), 
               pygame.image.load('assets/enemy/R3E.png'), 
               pygame.image.load('assets/enemy/R4E.png'), 
               pygame.image.load('assets/enemy/R5E.png'), 
               pygame.image.load('assets/enemy/R6E.png'), 
               pygame.image.load('assets/enemy/R7E.png'), 
               pygame.image.load('assets/enemy/R8E.png'), 
               pygame.image.load('assets/enemy/R9E.png'), 
               pygame.image.load('assets/enemy/R10E.png'), 
               pygame.image.load('assets/enemy/R11E.png') 
               ]
  
  walkLeft =  [pygame.image.load('assets/enemy/L1E.png'), 
               pygame.image.load('assets/enemy/L2E.png'), 
               pygame.image.load('assets/enemy/L3E.png'), 
               pygame.image.load('assets/enemy/L4E.png'), 
               pygame.image.load('assets/enemy/L5E.png'), 
               pygame.image.load('assets/enemy/L6E.png'), 
               pygame.image.load('assets/enemy/L7E.png'), 
               pygame.image.load('assets/enemy/L8E.png'), 
               pygame.image.load('assets/enemy/L9E.png'), 
               pygame.image.load('assets/enemy/L10E.png'), 
               pygame.image.load('assets/enemy/L11E.png')
               ]

  def __init__(self, x, y, width, height, end):
      self.x = x
      self.y = y
      self.width = width
      self.height = height
      self.end = end
      self.path = [self.x, self.end]
      self.walkCount = 0
      self.vel = 3
      self.health = 10
      self.max_health = 10

  def draw(self, win):
    self.move()
    if self.walkCount + 1 >= 33:
      self.walkCount = 0

    if self.vel > 0:
      win.blit(self.walkRight[self.walkCount // 3], (self.x, self.y))
      self.walkCount += 1
      
    else:
      win.blit(self.walkLeft[self.walkCount // 3], (self.x, self.y))
      self.walkCount += 1

    bar_width = 50
    bar_height = 10
    bar_x = self.x + (self.width // 2) - (bar_width // 2)
    bar_y = self.y - 15
    pygame.draw.rect(win, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(win, (0, 128, 0), (bar_x, bar_y, int(bar_width * (self.health / self.max_health)), bar_height))

  def move(self):
    if self.vel > 0:
      if self.x + self.vel < self.path[1]:
        self.x += self.vel
      else:
        self.vel = self.vel * -1
        self.walkCount = 0
    else:
      if self.x + self.vel > self.path[0]:
         self.x += self.vel
      else:
        self.vel = self.vel * -1
        self.walkCount = 0

  

screenwidth = 800

# IMGS_______________________________________
walkRight = [
    pygame.image.load('assets/player/R1.png'),
    pygame.image.load('assets/player/R2.png'),
    pygame.image.load('assets/player/R3.png'),
    pygame.image.load('assets/player/R4.png'),
    pygame.image.load('assets/player/R5.png'),
    pygame.image.load('assets/player/R6.png'),
    pygame.image.load('assets/player/R7.png'),
    pygame.image.load('assets/player/R8.png'),
    pygame.image.load('assets/player/R9.png'),
]
walkLeft = [
    pygame.image.load('assets/player/L1.png'),
    pygame.image.load('assets/player/L2.png'),
    pygame.image.load('assets/player/L3.png'),
    pygame.image.load('assets/player/L4.png'),
    pygame.image.load('assets/player/L5.png'),
    pygame.image.load('assets/player/L6.png'),
    pygame.image.load('assets/player/L7.png'),
    pygame.image.load('assets/player/L8.png'),
    pygame.image.load('assets/player/L9.png'),
]
bg = pygame.transform.scale(pygame.image.load('bg1.png'), (800, 450))
char = pygame.image.load('standing.png')


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