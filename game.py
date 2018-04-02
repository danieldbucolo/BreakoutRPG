#################################################
# BREAKOUT ULTIMATE RPG
# CREATED BY DANIEL BUCOLO
#
# TODO: OPTIMIZATION FOR FURTHER DEVELOPMENT
##################################################
# TODO: PLAYER TALENT SYSTEM & UI
# TODO: BOSS LEVEL
# TODO: SAVE SYSTEM
# TODO: MENU & FINAL UI SCREENS
# TODO: FIX FULL SCREEN SCALING
# TODO: TEXTURES
# TODO: SOUNDS
#
#################################################
import sys, pygame, os, math

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)
orange = (255, 165, 0)


# Paddle class
class Player(object):
    width = 180
    height = 8

    def __init__(self):
        self.vertloc = SCREEN_START_HEIGHT - Wall.width - Player.height
        self.rect = pygame.Rect(Wall.width + 10, self.vertloc, Player.width, Player.height)
        self.prepared = False
        self.color = red

    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0: self.move_single_axis(dx, 0)
        if dy != 0: self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                 if self.rect.centerx > wall.rect.centerx: self.rect.left = 30
                 if self.rect.centerx < wall.rect.centerx: self.rect.right = 930
            else:
                # Move the rect
                self.rect.x += dx
                self.rect.y += dy


# Class for ball
class Ball(object):
    width = 7
    height = 13

    def __init__(self, posx, posy, velx, vely):
        self.rect = pygame.Rect(posx, posy, Ball.width, Ball.height)
        self.velx = velx
        self.vely = vely
        self.lives = 3
        self.health = 100
        self.score = 0
        self.current_level = 1
        self.level_completed = False
        self.type = 1
        self.color = green
        self.time_to_reset = True

    def move(self):
        # Move each axis separately. Note that this checks for collisions both times.
        if self.velx != 0: self.move_single_axis()
        if self.vely != 0: self.move_single_axis()

    def move_single_axis(self):
        # Move the rect
        self.rect.x += self.velx
        self.rect.y += self.vely

        # If you collide with a wall, move out based on velocity
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if wall.type == 1: self.velx = -self.velx
                if wall.type == 2:
                    if self.vely < 0: self.vely = -self.vely
                if wall.type == 3:
                    # Subtract health that is formula of level number
                    self.health -= 25 + int(self.current_level * .25)
                    if self.health <= 0:
                        # If player has lives reset otherwise game over
                        if self.lives > 0:
                            self.health = 100
                            self.lives -= 1
                            self.reset()
                        else:
                            self.current_level = 1
                            self.lives = 3
                            self.health = 100
                            self.score = 0
                            self.reset()
                            self.time_to_reset = True
                    else:
                        self.reset()

        # Check for paddle collision
        if self.rect.colliderect(player.rect):
            if self.vely > 0: self.vely = -self.vely
            if (self.velx > 0 > player_velocity) or (self.velx < 0 < player_velocity) or self.velx == 0:
                self.velx = player_velocity

        # Check for block collision
        for block in blocks:
            if self.rect.colliderect(block.rect):
                block.hit()
                if block.rect.centery > self.rect.centery:
                   if self.vely > 0: self.vely = -self.vely
                if block.rect.centery < self.rect.centery:
                    if self.vely < 0: self.vely = -self.vely
                if block.rect.centerx > self.rect.centerx:
                    if self.velx > 0: self.velx = -self.velx
                if block.rect.centerx < self.rect.centerx:
                    if self.velx < 0: self.velx = -self.velx

    def reset(self):
        self.rect = pygame.Rect(player.rect.centerx - 15, 450, 30, 30)
        player.prepared = False


# Nice class to hold a wall rect
# Types are 1 = wall, 2 = ceiling, 3 = floor
class Wall(object):
    width = 16

    def __init__(self, pos, wall_type):
        walls.append(self)
        if wall_type == 1: self.rect = pygame.Rect(pos, 0, Wall.width, SCREEN_START_HEIGHT)
        if wall_type == 2: self.rect = pygame.Rect(0, 0, SCREEN_START_WIDTH, Wall.width)
        if wall_type == 3: self.rect = pygame.Rect(0, SCREEN_START_HEIGHT - Wall.width, SCREEN_START_WIDTH, Wall.width)
        self.type = wall_type


# Block parent class
class Block(object):
    size = 1024
    height = math.sqrt(size / 2)
    width = height * 2
    space_size = 4

    def __init__(self, pos):
        self.pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], Block.width, Block.height)
        self.active = True
        self.color = black

    def update(self):
        pygame.draw.rect(image, self.color, self.rect)

    def die(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.active = False


# Class for a basic block
# Types are 1 = normal health, 2 = double health
class BasicBlock(Block):

    def __init__(self, pos, block_type):
        super().__init__(pos)
        if block_type == 1:
            self.health = 100
            self.type = 1
            self.color = blue
        if block_type == 2:
            self.health = 200
            self.type = 2
            self.color = red

    def hit(self):
        ball.score += 10
        self.health -= 50
        if self.health == 0:
            if self.type == 1: ball.score += 50
            if self.type == 2: ball.score += 100
            self.die()


# Class for a block that switches or disappears depending on whether you hit it
# State False = Red (Will switch upon being hit) - - True = Green (Will disappear upon being hit)
class TrafficBlock(Block):

    def __init__(self, pos, state):
        super().__init__(pos)
        self.state = state
        if state: self.color = green
        else: self.color = red

    def hit(self):
        if self.state:
            ball.score += 50
            self.die()
        else:
            self.state = True
            self.color = green


# Block that will do damage if its abilities hit the player's paddle
# Types 1 = Basic, slow shot downward, 100 health
class AttackBlock(Block):

    def __init__(self, pos, type):
        super().__init__(pos)
        self.type = type
        if type == 1:
            self.health = 100
            self.color = orange
        self.bullets = []
        self.num_of_bullets = 0
        self.max_bullets = 2
        self.time_since_last_shot = 0

    def hit(self):
        if self.type == 1:
            ball.score += 10
            self.health -= 50
            if self.health <= 0:
                if self.type == 1: ball.score += 50
                self.die()

    class Bullet(object):

        def __init__(self, pos, velx, vely):
            self.rect = pygame.Rect(pos[0] + 29, pos[1] + 14, 6, 12)
            self.pos = (pos[0], pos[1])
            self.velx = velx
            self.vely = vely
            self.active = True

        def move(self):
            # Move each axis separately. Note that this checks for collisions both times.
            if self.velx != 0 or self.vely != 0: self.move_single_axis()

        def move_single_axis(self):
            # Move the rect
            self.rect.x += self.velx
            self.rect.y += self.vely
            if self.rect.colliderect(player.rect):
                ball.health -= 20
                if ball.health < 0:
                    ball.lives -= 1
                    ball.health = 100
                    ball.reset()
                self.die()
            for wall in walls:
                if self.rect.colliderect(wall.rect): self.die()

        def update(self):
            pygame.draw.rect(image, red, self.rect)
            self.move()

        def die(self):
            self.rect = pygame.Rect(0, 0, 0, 0)
            self.active = False

    def shoot(self):
        self.bullets.append(self.Bullet(self.pos, 0, 2))

    def update(self):
        super().update()
        self.num_of_bullets = 0
        for bullet in self.bullets:
            if bullet.active:
                self.num_of_bullets += 1
        if self.num_of_bullets < self.max_bullets and \
                (self.time_since_last_shot > 240 or self.num_of_bullets == 0) \
                and self.active:
            self.shoot()
            self.time_since_last_shot = 0
            self.num_of_bullets += 1
        self.time_since_last_shot += 1
        for bullet in self.bullets: bullet.update()


def create_walls(width, height):
    Wall(0, 1)
    Wall(width - 16, 1)
    Wall(0, 2)
    Wall(0, 3)


# Helps with generating blocks
# Type 1 = Basic, 2 = Traffic, 3 = Attack
# Strength = Varrying strengths the higher the stronger
def generate_block_row(row_size, type, strength, vertloc):
    inter_block_space = Block.space_size * (row_size - 1)
    total_block_width = row_size * Block.width
    remaining_space = SCREEN_START_WIDTH - (total_block_width + inter_block_space)

    i = 0
    while i < row_size:
        block_location = (remaining_space / 2) + (i * (Block.width + Block.space_size))
        new_block = Block((0, 0))
        if type == 1: new_block = BasicBlock((block_location, vertloc), strength)
        blocks.append(new_block)
        i += 1


def calculate_horizontal_offset(num_blocks):
    return (SCREEN_START_WIDTH - (num_blocks * Block.width) - ((num_blocks - 1) * Block.space_size)) / 2


def calculate_vertical_offset(num_rows):
    row_consumed_vertical_space = (num_rows * Block.height) + ((num_rows - 1) * Block.space_size)
    row_remaining_vertical_space = SCREEN_START_HEIGHT - row_consumed_vertical_space - \
                                   no_mans_space_height - scoring_text_height
    row_vertical_offset = row_remaining_vertical_space / 2
    return row_vertical_offset


def generate_level(level_num):
    # if level_num == 1:
    #     num_rows = 3
    #     vertical_row_offset = calculate_vertical_offset(num_rows)
    #     i = 0
    #     while i < num_rows:
    #         type = 2
    #         if i == 1: type = 3
    #         generate_block_row(type, 1, 1,
    #                            vertical_row_offset + scoring_text_height + (i * (Block.height + Block.space_size)))
    #         i += 1
    #
    # if level_num == 2:
    #     num_rows = 3
    #     vertical_row_offset = calculate_vertical_offset(num_rows)
    #     generate_block_row(2, 1, 1, vertical_row_offset + scoring_text_height)
    #
    #     second_row_vert_loc = vertical_row_offset + scoring_text_height + Block.height + Block.space_size
    #     i = 0
    #     num_blocks = 3
    #     while i < num_blocks:
    #         type = 1
    #         if i == 1: type = 2
    #         blocks.append(BasicBlock((calculate_horizontal_offset(num_blocks) + (i * (Block.width + Block.space_size)),
    #                                   second_row_vert_loc), type))
    #         i += 1
    #
    #     generate_block_row(2, 1, 1,
    #                        (vertical_row_offset + scoring_text_height) + (2 * (Block.height + Block.space_size)))
    #
    # if level_num == 3:
    #     num_rows = 3
    #     vertical_row_offset = calculate_vertical_offset(num_rows)
    #     generate_block_row(3, 1, 1, vertical_row_offset + scoring_text_height)
    #
    #     second_row_vert_loc = vertical_row_offset + scoring_text_height + Block.height + Block.space_size
    #     i = 0
    #     num_blocks = 5
    #     while i < num_blocks:
    #         type = 1
    #         if i == 2: type = 2
    #         blocks.append(BasicBlock((calculate_horizontal_offset(num_blocks) + (i * (Block.width + Block.space_size)),
    #                                   second_row_vert_loc), type))
    #         i += 1
    #
    #     generate_block_row(3, 1, 1,
    #                        (vertical_row_offset + scoring_text_height) + (2 * (Block.height + Block.space_size)))
    #
    # if level_num == 4:
    #     num_rows = 3
    #     vertical_row_offset = calculate_vertical_offset(3)
    #     generate_block_row(9, 1, 1, vertical_row_offset)
    #
    #     second_row_vert_loc = vertical_row_offset + Block.height + Block.space_size
    #     i = 0
    #     num_blocks = 11
    #     while i < num_blocks:
    #         type = 1
    #         if i == 0 or i == 3 or i == 7 or i == 10: type = 2
    #         blocks.append(BasicBlock((calculate_horizontal_offset(num_blocks) + (i * (Block.width + Block.space_size)),
    #                                   second_row_vert_loc), type))
    #         i += 1
    #
    #     generate_block_row(9, 1, 1, vertical_row_offset + (2 * (Block.height + Block.space_size)))
    #
    # if level_num == 5:
    #     first_point = (SCREEN_START_WIDTH / 5, calculate_vertical_offset(1))
    #     second_point = (SCREEN_START_WIDTH / 2, calculate_vertical_offset(1))
    #     third_point = ((SCREEN_START_WIDTH * 4) / 5, calculate_vertical_offset(1))
    #     blocks.append(BasicBlock((first_point[0] - (Block.width / 2), first_point[1] - (Block.height/2)), 2))
    #     blocks.append(BasicBlock(
    #         (first_point[0] - (Block.width / 2), first_point[1] - (Block.height * 1.5) - Block.space_size), 1))
    #     blocks.append(BasicBlock(
    #         (first_point[0] - (Block.width * 1.5) - Block.space_size,
    #          first_point[1] - (Block.height * .5)), 1))
    #     blocks.append(BasicBlock(
    #         (first_point[0] + (Block.width * .5) + Block.space_size,
    #          first_point[1] - (Block.height * .5)), 1))
    #     blocks.append(BasicBlock(
    #         (first_point[0] - (Block.width / 2), first_point[1] + (Block.height * .5) + Block.space_size), 1))
    #
    #     blocks.append(BasicBlock((second_point[0] - (Block.width / 2), second_point[1] - (Block.height/2)), 1))
    #     blocks.append(BasicBlock(
    #         (second_point[0] - Block.width - Block.space_size,
    #          second_point[1] - (Block.height * 1.5) - Block.space_size), 1))
    #     blocks.append(BasicBlock(
    #         (second_point[0] + Block.space_size,
    #          second_point[1] - (Block.height * 1.5) - Block.space_size), 1))
    #     blocks.append(BasicBlock(
    #         (second_point[0] - Block.width - Block.space_size,
    #          second_point[1] + (Block.height * .5) + Block.space_size), 1))
    #     blocks.append(BasicBlock(
    #         (second_point[0] + Block.space_size,
    #          second_point[1] + (Block.height * .5) + Block.space_size), 1))
    #
    #     blocks.append(BasicBlock((third_point[0] - (Block.width / 2), third_point[1] - (Block.height/2)), 2))
    #     blocks.append(BasicBlock(
    #         (third_point[0] - (Block.width / 2), third_point[1] - (Block.height * 1.5) - Block.space_size), 1))
    #     blocks.append(BasicBlock(
    #         (third_point[0] - (Block.width * 1.5) - Block.space_size,
    #          third_point[1] - (Block.height * .5)), 1))
    #     blocks.append(BasicBlock(
    #         (third_point[0] + (Block.width * .5) + Block.space_size,
    #          third_point[1] - (Block.height * .5)), 1))
    #     blocks.append(BasicBlock(
    #         (third_point[0] - (Block.width / 2), third_point[1] + (Block.height * .5) + Block.space_size), 1))
    #
    # if level_num == 6:
    #     num_rows = 5
    #     vertical_offset = calculate_vertical_offset(5)
    #     horizontal_offset = (SCREEN_START_WIDTH - (18 * Block.width + (17 * Block.space_size))) / 2
    #     generate_block_row(18, 1, 1, vertical_offset)
    #     blocks.append(TrafficBlock(
    #         ((horizontal_offset + (3 * Block.width) + (3 * Block.space_size)),
    #          (vertical_offset + (2 * Block.height) + Block.space_size)), False))
    #     blocks.append(TrafficBlock(
    #         ((SCREEN_START_WIDTH - horizontal_offset - (4 * Block.width) - (4 * Block.space_size)),
    #          (vertical_offset + (2 * Block.height) + Block.space_size)), False))
    #     generate_block_row(18, 1, 1, vertical_offset + (4 * Block.height + ((num_rows - 1) * Block.space_size)))
    #
    if level_num == 1:
        num_rows = 5
        vertical_offset = calculate_vertical_offset(5)
        horizontal_offset = (SCREEN_START_WIDTH - (18 * Block.width + (17 * Block.space_size))) / 2
        generate_block_row(18, 1, 1, vertical_offset)
        blocks.append(TrafficBlock(
            ((horizontal_offset + (3 * Block.width) + (3 * Block.space_size)),
             (vertical_offset + (2 * Block.height) + Block.space_size)), False))
        blocks.append(AttackBlock(
            ((horizontal_offset + (8.5 * Block.width) + (8 * Block.space_size)),
             (vertical_offset + (2 * Block.height) + Block.space_size)), 1))
        blocks.append(TrafficBlock(
            ((SCREEN_START_WIDTH - horizontal_offset - (4 * Block.width) - (4 * Block.space_size)),
             (vertical_offset + (2 * Block.height) + Block.space_size)), False))
        generate_block_row(18, 1, 1, vertical_offset + (4 * Block.height + ((num_rows - 1) * Block.space_size)))


def scale_image():
    if screen_rect.size != SCREEN_START_SIZE:
        fit_to_rect = image_rect.fit(screen_rect)
        fit_to_rect.center = screen_rect.center
        scaled = pygame.transform.smoothscale(image, fit_to_rect.size)
        screen.blit(scaled, fit_to_rect)
    else:
        screen.blit(image, (0, 0))


def wait():
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

SCREEN_START_SIZE = SCREEN_START_WIDTH, SCREEN_START_HEIGHT = (960, 540)
no_mans_space_height = 200
scoring_text_height = 50
os.environ["SDL_VIDEO_CENTERED"] = '1'
pygame.init()
fps = pygame.time.Clock()
myfont = pygame.font.SysFont('Comic Sans MS', 30)
paddle_speed = [0, 0]
screen = pygame.display.set_mode(SCREEN_START_SIZE, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
screen_rect = screen.get_rect()
image = pygame.Surface(SCREEN_START_SIZE).convert()
image_rect = image.get_rect()
walls = []
blocks = []
player_velocity = 0
player = Player()
create_walls(SCREEN_START_WIDTH, SCREEN_START_HEIGHT)
ball = Ball(0, 0, 0, 0)

while 1:
    active_blocks = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.VIDEORESIZE:
            # resave screen dimensions
            size = event.dict['size']
            width = size[0]
            height = int(width / (1920 / 1080))

            # re generate objects
            screen = pygame.display.set_mode((width, height), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
            screen_rect = screen.get_rect()

    if ball.level_completed:
        congrats_surface = myfont.render("CONGRATS", False, white)
        image.fill(black)
        image.blit(congrats_surface, (400, 225))
        scale_image()
        pygame.display.flip()
        wait()
        image.fill(black)
        ball.current_level += 1
        if ball.current_level % 2 == 2: ball.lives += 1
        generate_level(ball.current_level)
        ball.level_completed = False
        player.prepared = False

    if ball.time_to_reset:
        blocks = []
        image.fill(black)
        ball.time_to_reset = False
        player.prepared = False
        ball.level_completed = False
        generate_level(ball.current_level)

    lives_surface = myfont.render(str(ball.lives), False, white)
    health_surface = myfont.render(str(ball.health), False, white)
    score_surface = myfont.render(str(ball.score), False, white)

    # Get key presses and calculate paddle and ball physics
    pressed = pygame.key.get_pressed()
    if (pressed[pygame.K_LEFT] or pressed[pygame.K_a]) and not (pressed[pygame.K_RIGHT] or pressed[pygame.K_d]):
        player_velocity = -4
    if (pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) and not (pressed[pygame.K_LEFT] or pressed[pygame.K_a]):
        player_velocity = 4
    if not pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT] \
            and not pressed[pygame.K_a] and not pressed[pygame.K_d]: player_velocity = 0
    if pressed[pygame.K_SPACE]:
        if not player.prepared:
            ball.velx = player_velocity
            ball.vely = -4
            player.prepared = True
    player.move(player_velocity, 0)
    if player.prepared: ball.move()
    else: ball.reset()

    # Draw objects
    image.fill(black)
    #for wall in walls: pygame.draw.rect(image, green, wall.rect)
    image.blit(lives_surface, (10, 0))
    image.blit(health_surface, (450, 0))
    image.blit(score_surface, (850, 0))
    for block in blocks:
        block.update()
        if block.active: active_blocks += 1
    pygame.draw.rect(image, green, player.rect)
    #pygame.draw.rect(image, (255, 0, 0), ball.rect)
    pygame.draw.circle(image, blue, (ball.rect.centerx, ball.rect.centery), 13)

    if len(blocks) > 0 and active_blocks == 0:
        ball.level_completed = True
        ball.reset()

    # Render
    scale_image()
    pygame.display.flip()
    fps.tick_busy_loop(60)
