import pygame
import os

print(os.listdir("src"))

print("GAME folder:", os.listdir())
print("SRC folder:", os.listdir("src"))
pygame.init()


win = pygame.display.set_mode((950, 540))
pygame.display.set_caption("BUG GAME")

#variables___________
clock = pygame.time.Clock
 
screenwidth = 950

x = 250
y = 250
width = 64
height = 64
vel = 5

isJump = False
jumpCount = 10

left = False
right = False
walkCount = 0

walkRight = [pygame.image.load('R1E.png'), pygame.image.load('R2.png'), pygame.image.load('R3.png'), pygame.image.load('R4.png'), pygame.image.load('R5.png'), pygame.image.load('R6.png'), pygame.image.load('R7.png'), pygame.image.load('R8.png'), pygame.image.load('R9.png')]
walkLeft = [pygame.image.load('L1.png'), pygame.image.load('L2.png'), pygame.image.load('L3.png'), pygame.image.load('L4.png'), pygame.image.load('L5.png'), pygame.image.load('L6.png'), pygame.image.load('L7.png'), pygame.image.load('L8.png'), pygame.image.load('L9.png')]
bg = pygame.image.load('bg.jpg')
char = pygame.image.load('standing.png')
#______________________

#MAIN LOOP________________________
run = True


def redrawgamewindow():
    global walkCount
    win.blit(bg, (0, 0))

    if walkCount + 1 >=27:
        walkCount =0


    if left:
        win.blit(walkLeft[walkCount//3], (x,y))
        walkCount +=1

    elif right:
        win.blit(walkRight[walkCount//3], (x,y))
        walkCount +=1

    else:
        win.blit(char, (x,y))
            
    pygame.display.update()        
    



while run:
    clock.tick(27)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and x > vel:
        x -= vel
        left = True
        right = False

    elif keys[pygame.K_RIGHT] and x < screenwidth - width - vel:
        x += vel
        right = True
        left = False

    else:
        right = False
        left= False
        walkCount = 0

    if not isJump:
        if keys[pygame.K_SPACE]:
            isJump = True
            right = False
            left= False
            walkCount = 0

    else:
        if jumpCount >= -10:
            neg = 1
            if jumpCount <0:
                neg = -1
            y -= (jumpCount **2)/2 *neg
            jumpCount -=1
            
        else:
            isJump = False
            jumpCount =10

    redrawgamewindow()





   
pygame.quit()            
#___________________________________________________________________