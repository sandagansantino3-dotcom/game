import pygame

pygame.init()

win = pygame.display.set_mode((800, 450))
pygame.display.set_caption("BUG GAME")

clock = pygame.time.Clock()


class player(object): # This will be our player class

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

class enemy(object): # Class for enemy
  walkRight = [pygame.image.load('R1E.png'), 
               pygame.image.load('R2E.png'), 
               pygame.image.load('R3E.png'), 
               pygame.image.load('R4E.png'), 
               pygame.image.load('R5E.png'), 
               pygame.image.load('R6E.png'), 
               pygame.image.load('R7E.png'), 
               pygame.image.load('R8E.png'), 
               pygame.image.load('R9E.png'), 
               pygame.image.load('R10E.png'), 
               pygame.image.load('R11E.png') 
               ]
  
  walkLeft =  [pygame.image.load('L1E.png'), 
               pygame.image.load('L2E.png'), 
               pygame.image.load('L3E.png'), 
               pygame.image.load('L4E.png'), 
               pygame.image.load('L5E.png'), 
               pygame.image.load('L6E.png'), 
               pygame.image.load('L7E.png'), 
               pygame.image.load('L8E.png'), 
               pygame.image.load('L9E.png'), 
               pygame.image.load('L10E.png'), 
               pygame.image.load('L11E.png')
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

  def test(self):
    pass

screenwidth = 800

# IMGS_______________________________________
walkRight = [
    pygame.image.load('R1.png'),
    pygame.image.load('R2.png'),
    pygame.image.load('R3.png'),
    pygame.image.load('R4.png'),
    pygame.image.load('R5.png'),
    pygame.image.load('R6.png'),
    pygame.image.load('R7.png'),
    pygame.image.load('R8.png'),
    pygame.image.load('R9.png'),
]
walkLeft = [
    pygame.image.load('L1.png'),
    pygame.image.load('L2.png'),
    pygame.image.load('L3.png'),
    pygame.image.load('L4.png'),
    pygame.image.load('L5.png'),
    pygame.image.load('L6.png'),
    pygame.image.load('L7.png'),
    pygame.image.load('L8.png'),
    pygame.image.load('L9.png'),
]
bg = pygame.image.load('bg.jpg')
char = pygame.image.load('standing.png')


def redrawgamewindow():
  win.blit(bg, (0, 0))  
  man.draw(win)  
  goblin.draw(win)
  pygame.display.update()


# MAIN LOOP________________________
man = player(300, 350, 64, 64)
goblin = enemy(100, 350, 64, 64, 450)
run = True

while run:
  clock.tick(27)
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