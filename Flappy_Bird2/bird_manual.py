import numpy as np
import sys
import os
import time
import pygame
import random
pygame.init()

# window width and height
WIN_WIDTH = 500
WIN_HEIGHT = 800

# images list


# welcome image
# the welcome image
WELCOME_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'message.png')))

# the bird image
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird'+str(i)+'.png'))) for i in range(1,4)]
BLUE_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bluebird'+str(i)+'.png'))) for i in range(1,4)]
RED_BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'redbird'+str(i)+'.png'))) for i in range(1,4)]


# the pipe image

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))

# the base image
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))

# the background image
BG_DAY = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BG_NIGHT = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg_night.png')))

BG_IMG = random.choice((BG_DAY, BG_NIGHT))

# The end image
END_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'gameover.png')))

STAT_FONT = pygame.font.SysFont("arial", 40)
# SCORE_FONT = pygame.font.SysFont('')
GEN = 0

### Build the bird class
class Bird:

    IMGS = random.choice((BIRD_IMGS, BLUE_BIRD_IMGS, RED_BIRD_IMGS))
    # how much does the bird tilt
    MAX_ROTATION = 25
    # rotation velocity
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):

        self.x = x
        self.y = y

        # how much does the bird tilt
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        # which image will show
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):

        # jump upward
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):

        # keep track how many moves since last jump
        self.tick_count += 1

        # how many pixels are moving up or down this frame
        # -10.5*t + 1.5*t**2
        # -10.5 + 1.5*1 = -9 9 pixels up in the first frame
        d = self.vel * self.tick_count + 1.5*(self.tick_count)**2
        
        # if move down exceeds 16, just move down 16.
        if d >= 16 :

            d = d/(abs(d)) * 16

        if d < 0:
            d = d - 2

        self.y = self.y + d

        # if we are moving upward or not reaching the point we want to tilt down
        if d < 0 or self.y < self.height +50 :

            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        # tilt the bird downward
        else:

            if self.tilt > -90 :
                self.tilt -= self.ROT_VEL


    def draw(self, win):

        # Which bird image to show, flapping the wings
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]

        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]

        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]

        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]

        elif self.img_count ==  self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # if the bird is flying downward and exceeds 80 degree, don't flap the wings
        # show the 
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME *2

        # Rotate the image in the center of the image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)


    def get_mask(self):
        """
        Use when we get the collision
        """
        return pygame.mask.from_surface(self.img)



### Build the pipe class
class Pipe:

    # space between pipes
    # GAP = 200
    GAP = random.randrange(200,230)
    # how fast is the pipe moving
    VEL = 5

    def __init__(self, x):

        self.x = x
        self.height = 0
        

        self.top = 0
        self.bottom = 0

        # flip the image vertically
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        # the bottom pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):

        # move the pipe leftward
        self.x = self.x - self.VEL

    def draw(self, win):

        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):

        # get bird and pipe masks
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # find the collision points. Check if they exist
        # bird and the bottom pipe
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) # return None if no collision
        t_point = bird_mask.overlap(top_mask, top_offset) 

        if b_point or t_point:
            return True

        return False


### Build the base class

class Base:


    VEL = 5
    # how width the image is
    WIDTH  = BASE_IMG.get_width() 
    IMG = BASE_IMG

    def __init__(self, y):

        self.y = y
        #two images
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Move the base
        """
        self.x1 = self.x1 - self.VEL
        self.x2 = self.x2 - self.VEL

        # when all the base is passed
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH


        if self.x2 + self.WIDTH <0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """Draw the base
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))







def draw_window(win, bird, pipes, base, score, end = False):
    # draw the window
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    bird.draw(win)

    # draw the score, gen, number of birds alive
    text = STAT_FONT.render('Score:' + str(score), 1, (255,255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    if end:
        win.blit(END_IMG,(100,100))


    pygame.display.update()

def main():




    # Create objects
    base = Base(730)
    pipes = [Pipe(600)]
    bird = Bird(230, 350)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    start = True

    # welcome window
    while start:
        clock.tick(30)
        win.blit(BG_IMG, (0,0))
        win.blit(WELCOME_IMG, (60,100))
        pygame.display.update()

        # click left or press space to start the game
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = False

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    start = False              
    
    score = 0

    run = True
    end = False

    while run:
        clock.tick(20)

        ## Move bird
        bird.move()

        for event in pygame.event.get():
            # quit the game
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:

                    bird.jump()
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    quit()

        # 
        pipe_ind = 0
        
            # if we passed the pipe, change the pipe to be the second one.
        if len(pipes) >1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

    
        rem = []
        add_pipe = False
        for pipe in pipes:
            
            # if collide
            if pipe.collide(bird):
   
                run = False
                main()

                # check if we have passed the pipe, generate a new if true
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            # off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)


            pipe.move()

        # add pipes
        if add_pipe:

            score += 1

            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)


        # Check if the bird hits the ground or above the window
        
        if bird.y + bird.img.get_height() > 730 or bird.y < 0 :

            run = False
            main()
                

        base.move()
        draw_window(win, bird, pipes, base, score)




if __name__ == '__main__':

    main()


