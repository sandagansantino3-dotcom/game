import pygame
pygame.init()

win = pygame.display.set_mode((800, 450))
pygame.display.set_caption("BUG GAME")


#variables___________
clock = pygame.time.Clock()

class player(object):
    def __init__(self, x , y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 5
        self.isJump = False
        self.jumpCount = 10
        self.left = False
        self.left = False
        self.right = False
        self.walkCount = 0

    def draw(self.win):
        if  self.walkCount + 1 >=27:
            self.walkCount =0


    if self.left:
        win.blit(walkLeft[self.walkCount//3], (self.x,self.y))
        self.walkCount +=1

    elif self.right:
        win.blit(walkRight[self.walkCount//3], (self.x,self.y))
        self.walkCount +=1

    else:
        win.blit(char, (self.x,self.y)) 
 
screenwidth = 800



#______________________

#IMGS_______________________________________
walkRight = [pygame.image.load('R1.png'), pygame.image.load('R2.png'), pygame.image.load('R3.png'),
              pygame.image.load('R4.png'), pygame.image.load('R5.png'), pygame.image.load('R6.png')
              , pygame.image.load('R7.png'), pygame.image.load('R8.png'), pygame.image.load('R9.png')]
walkLeft = [pygame.image.load('L1.png'), pygame.image.load('L2.png'), pygame.image.load('L3.png'), 
            pygame.image.load('L4.png'), pygame.image.load('L5.png'), pygame.image.load('L6.png'), 
            pygame.image.load('L7.png'), pygame.image.load('L8.png'), pygame.image.load('L9.png')]
bg = pygame.image.load('bg.jpg')
char = pygame.image.load('standing.png')
#___________________________________________



def redrawgamewindow():
    man.draw(win)
    win.blit(bg, (0, 0))
    pygame.display.update()       
    

#MAIN LOOP________________________
man = player(300, 410, 64, 64)
run = True
while run:
    clock.tick(27)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and self.x > self.vel:
        self.x -= self.vel
        self.left = True
        self.right = False

    elif keys[pygame.K_RIGHT] and self.x < screenwidth - self.width - self.vel:
        self.x += self.vel
        self.right = True
        self.left = False

    else:
        self.right = False
        self.left= False
        self.walkCount = 0

    if not isJump:
        if keys[pygame.K_SPACE]:
            self.isJump = True
            self.right = False
            self.left= False
            self.walkCount = 0

    else:
        if self.jumpCount >= -10:
            neg = 1
            if self.jumpCount <0:
                neg = -1
            y -= (self.jumpCount **2)/2 *neg
            self.jumpCount -=1
            
        else:
            self.isJump = False
            self.jumpCount =10

    redrawgamewindow()


# Test to see if this shit works


 
pygame.quit()            
#___________________________________________________________________
