"""
DO WHATEVER YOU WANT TO PUBLIC LICENSE
Version 2, December 2004
 
Copyright (C) 2019 Sheng Zhuang <shengzh9@gmail.com>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.
 
DO WHATEVER YOU WANT TO PUBLIC LICENSE
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHATEVER YOU WANT TO.
"""


import random, math, pygame
from pygame.locals import *
from brick import BrickPattern

# resolution, and all width, height and x, y are represented in res
res = 40
screen_width, screen_height = 18*res, 22*res
pad = res - 2            # add padding to tile, to have grid lines around tiles
offset = res + 1         # offset for padding
v = 500                  # 500ms, brick fall speed
speedscale = (500/v)**2  # to scale up score accoding to speed

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height)) 
pygame.display.set_caption("TEpRIS")
clock = pygame.time.Clock()


class Brick:
    def __init__(self,bp,wall):
        self.ip = random.randint(0, len(bp.bricks)-1)
        self.patterns = bp.bricks[self.ip]
        self.pat = self.patterns[random.randint(0, len(self.patterns)-1)] #[(0,0),(1,0),(2,0),(3,0)]
        self.colour = bp.brick_colors[self.ip]
        self.x = 3        # the brick start point coor_x
        self.y = -4       # the brick start point coor_y
        self.locs = [(x+self.x, y+self.y) for x, y in self.pat]  # all brick_tiles coordinations in real time
        self.r_count = 0  # rotation index through pattern list
        self.wall = wall
        self.v = v        # falling speed
        self.cdf = 2 * v  # countdown before freezed, 3 * fall_speed in ms

    def draw(self):
        for x,y in self.locs:
            if y >= 0:
                pygame.draw.rect(screen, self.colour, (x*res+offset,y*res+offset,pad,pad))
    
    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self._move_l()

        # quick down
        if keys[pygame.K_SPACE]:
            self._projection()

        if keys[pygame.K_RIGHT]:   
            self._move_r()
        
        if keys[pygame.K_DOWN]:
            self._move_d()

        """
        rotate it as up is pressed.
        when the brick is too close to the wall, instead of locking it down,
        we add a move to kick it out 1 or 2 pixels
        """
        if keys[pygame.K_UP]:
            """
            rotate action feels quite sticky, not sure if something is not right
            """
            if self.is_turnable():
                self._rotate()
            elif self.is_turnable(left=1):
                self._move_l()
                self._rotate()
            elif self.is_turnable(left=2):
                self._move_l()
                self._move_l()
                self._rotate()
            elif self.is_turnable(left=-1):
                self._move_r()
                self._rotate()
            elif self.is_turnable(left=-2):
                self._move_r()
                self._move_r()
                self._rotate()
            elif self.is_turnable(up=1):
                self._move_u()
                self._rotate()
            elif self.is_turnable(up=2):
                self._move_u()
                self._move_u()
                self._rotate()

    def fall(self):
        # brick fall 1 unit as v count down to zero, speed control with v
        if not self.is_bottom():
            self.v -= clock.get_rawtime()
            clock.tick()
            if self.v < 0:
                self.v = v
                self.y += 1
                self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def _move_l(self):
        if not self.is_leftedge():
            self.x -= 1
            self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def _move_r(self):
        if not self.is_rightedge():
            self.x += 1
            self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def _move_d(self):
        if not self.is_bottom():
            self.y += 1
            self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def _move_u(self):
            self.y -= 1
            self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def _rotate(self):
        self.r_count += 1
        self.r_count %= len(self.patterns)
        self.pat = self.patterns[self.r_count]
        self.locs = [(x+self.x, y+self.y) for x, y in self.pat]
    
    def _projection(self):
        # push the brick directly to the bottom
        while not self.is_bottom():
            self.y += 1
            self.locs = [(x+self.x, y+self.y) for x, y in self.pat]

    def is_leftedge(self):
        for x,y in self.locs:
            if x < 1:
                return True
            elif (x-1,y) in self.wall.locs:
                return True
        return False

    def is_rightedge(self):
        for x,y in self.locs:
            if x > 8:
                return True
            elif (x+1,y) in self.wall.locs:
                return True
        return False

    def is_turnable(self, left = 0, up = 0, rotate = 1):
        """
        # create a shadow brick, make a move, check if all tiles are still in legit area
        :param default rotate = 1, for checking the brick in next rotation pattern
        :param left and up is for kicking, in case the brick is totally locked 
        when too close to right edge or bottom
        """
        sx, sy = self.x, self.y
        sx -= left
        sy -= up
        sr = self.r_count + rotate
        sr %= len(self.patterns)
        spat = self.patterns[sr]
        slocs = [(x+sx, y+sy) for x, y in spat]

        #and check all tiles are in right position
        for x,y in slocs:
            if x < 0 or x > 9 or y > 19 or (x, y) in self.wall.locs:
                return False
        return True

    def is_bottom(self):
        for x,y in self.locs:  
            if y > 18:
                return True
            elif (x,y+1) in self.wall.locs:
                return True
        return False
        
    def is_frozen(self):
        # count down after it touch the bottom, until it is frozen,
        # and return the status
        if self.is_bottom():
            if self.cdf > 0:
                self.cdf -= clock.get_rawtime()
                clock.tick()
                return False
            return True


class Ghost(Brick):
    """
    ghost brick will inherent from the current brick 
    and project to the bottom as a shadow brick for referencing
    """
    def __init__(self, brick, wall):
        self.pat = brick.pat
        self.colour = (25,25,25)
        self.x = brick.x
        self.y = brick.y
        self.locs = [(x+self.x, y+self.y) for x, y in self.pat]
        self.wall = wall

    def draw(self):
        self._projection()
        for x,y in self.locs:
            pygame.draw.rect(screen, self.colour, (x*res+offset,y*res+offset,pad,pad))
    

class Wall:
    """
    solid part at the bottom, which takes in bricks, 
    and also control clear-lines, 
    and touch the ceing to end game
    """
    def __init__(self):
        self.locs = []
        self.solid_lines = []
        self.score = 0
        self.sc = {"0":0, "1":5, "2":10, "3":20, "4":50,}

    def update(self, brick):
        # take in tiles of the current brick after frozen
        for loc in brick.locs:
            self.locs.append(loc)
        self.score += 1
    
    def draw(self):
        # draw the wall, tile by tile
        for x, y in self.locs:
            if y >= 0:
                pygame.draw.rect(screen, (60,60,60), (x*res+offset,y*res+offset,pad,pad))
                pygame.draw.rect(screen, (100,100,100), (x*res+offset+6,y*res+offset+6,pad-12,pad-12))

    def _get_solid_lines(self):
        # to get a list of True/False value to solid line or not
        for i in range(20): 
            is_solid_line = True
            for j in range(10):
                if (j,i) not in self.locs:
                    is_solid_line = False
            self.solid_lines.append(is_solid_line)
    
    def clear_solid_line(self):
        self._get_solid_lines()
        for i, line in enumerate(self.solid_lines):
            # line value is True or False
            if line:
                for j in range(10):
                    if (j, i) in self.locs:
                        self.locs.remove((j,i)) 
                k = i - 1
                while k >= 0:
                    for m in range(10):
                        if (m,k) in self.locs:
                            self.locs[self.locs.index((m,k))]=(m,k+1)
                    k -= 1
        # update score, based on lines and speed
        sl = [x for x in self.solid_lines if x]
        k = str(len(sl))
        self.score += math.floor(self.sc[k]*speedscale)
        self.solid_lines = []
    
    def is_stackable(self):
        # check if wall reach to the ceiling
        for _,y in self.locs:
            if y <= 0:
                return False
        return True

class Board:
    def draw_playing(self):
        # draw playing screen
        screen.fill((0,0,0))
        self._draw_dashboard()
        self._draw_grid()

    def draw_pause(self):
        # draw pause screen
        self._draw_logo()
        self._draw_text('Press esc to continue', 40, (255, 255, 255), 2*res, 6*res)

    def draw_gameover(self):
        # draw game over screen
        self._draw_text('Press enter to restart', 40, (255, 255, 255), 2*res, 6*res)

    def draw_intro(self):
        # draw open introduction screen
        self._draw_logo()
        self._draw_text('Welcome to TEpRIS', 80, (255, 255, 255), 1.5*res, 6*res)
        self._draw_text('Press enter to begin', 40, (255, 255, 255), 5*res, 9*res)

    def _draw_logo(self):
        # those 3 square thing on the bottom right
        locs = [(15,18),(13,18),(15,16)]
        for x,y in locs:
            pygame.draw.rect(screen, (200,200,200), (x*res,y*res,pad*2,pad*2))

    def _draw_text(self, text, size, color, x, y):
        # font = pygame.font.SysFont('comicsans', size, bold=True)
        font = pygame.font.Font('fonts/Indie_Flower/IndieFlower-Regular.ttf', size, bold=True)
        label = font.render(text, 1, color)
        screen.blit(label, (x,y))
    
    def _draw_grid(self):
        # draw background grid
        for i in range(10):
            for j in range(20):
                pygame.draw.rect(screen, (20, 20, 20), (i*res+offset,j*res+offset,pad,pad))

    def _draw_dashboard(self):
        pygame.draw.rect(screen, (20, 20, 20), (12*res,0,6*res,22*res))

    def show_score(self, wall):
        self._draw_text(f"score {wall.score}", 30, (255, 255, 255), 12.5*res, 20*res)

    @staticmethod
    def draw_next_brick(brick):
        for i in range(12,18):
            for j in range(4,8):
                pygame.draw.rect(screen, (10, 10, 10), (i*res,j*res,pad,pad))
        for x,y in brick.pat:
            pygame.draw.rect(screen, brick.colour, ((x+13)*res,(y+4)*res,pad,pad))

# class object setup
bp = BrickPattern()
wall = Wall()
current_brick = Brick(bp,wall)
next_brick = Brick(bp,wall)
board = Board()

# game status
start = False
pause = False
game_over = False
run = True

# run tetris
while run:
    if pause:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pause = False

        screen.fill((100,100,100))
        # board.draw_playing()
        board.draw_pause()
        pygame.display.update()

    elif start:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == QUIT:
                    run = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pause = True
        
        # v decrease as score increase
        # v is more like interval, the samller the faster the brick fall
        v -= wall.score/5000

        keys = pygame.key.get_pressed()
        board.draw_playing()
        board.draw_next_brick(next_brick)
        board.show_score(wall)
        current_brick.move(keys)
        current_brick.fall()
        ghost = Ghost(current_brick, wall)
        ghost.draw()
        current_brick.draw()
        
        if wall.is_stackable():
            if current_brick.is_frozen():
                wall.update(current_brick)
                current_brick = next_brick
                next_brick = Brick(bp,wall)
        else:
            game_over = True
            start = False

        wall.draw()
        wall.clear_solid_line()
        pygame.display.update()

    elif game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    v = 500
                    start = True
                    game_over = False
                    wall = Wall()
                    current_brick = Brick(bp,wall)
                    next_brick = Brick(bp,wall)
            board.draw_gameover()
            pygame.display.update()
    else:
        # game main screen
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    start = True
        screen.fill((100,100,100))
        board.draw_intro()
        pygame.display.update()

pygame.quit()
