import pygame
from sys import exit
import os

# import random

# Intialize the game
pygame.init()

# Set Width, Height and FPS for Game Window
WIDTH = 800
HEIGHT = 400
FPS = 60

clock = (
    pygame.time.Clock()
)  # The clock controls how many times the game refreshes per second

# Setup the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Dino Run")

# Set keys to repeat after 1s of holding
pygame.key.set_repeat(100)


class Player:
    GRAVITY = 0
    JUMP_VELOCITY = 15
    ASSETS_FOLDER = "./Assets/Player"

    # Player Assets

    sprites = []

    run_state = 0

    def __init__(self, x, y, obstacle_handler):
        self.x = x
        self.y = y
        self.GROUND_HEIGHT = y
        self.obstacle_handler = obstacle_handler

        # Load character sprites from ASSETS folder
        for file in sorted(os.listdir(os.path.abspath(self.ASSETS_FOLDER))):
            file_path = os.path.join(self.ASSETS_FOLDER, file)
            if os.path.isfile(file_path):
                # Load and Scale Sprite
                img = pygame.transform.scale_by(
                    pygame.image.load(file_path).convert_alpha(), 0.7
                )

                self.sprites.append(img)

    def get_draw(self):
        img = pygame.Surface((0, 0))
        if self.onGround():
            if self.run_state < 60:
                img = self.sprites[2]
            elif self.run_state < 120:
                img = self.sprites[3]
            elif self.run_state >= 120:
                self.run_state = 0
                img = self.sprites[2]
        else:
            img = self.sprites[4]
        return img

    def jump(self):
        if self.onGround():
            self.GRAVITY = -self.JUMP_VELOCITY

    def get_position(self):
        return self.get_draw().get_rect(midbottom=(self.x, self.y))

    def tick(self):
        self.run_state += 6
        self.GRAVITY += 1
        self.y += self.GRAVITY
        if self.y > self.GROUND_HEIGHT:
            self.y = self.GROUND_HEIGHT

    def onGround(self):
        if self.y == self.GROUND_HEIGHT:
            return True
        if self.y > self.GROUND_HEIGHT:
            return False


class ObstacleHandler:
    sprites = []

    obstacles = []

    ASSETS_FOLDER = "./Assets/Obstacles"

    OBSTACLE_SPEED = 3
    SPEED_MULTIPLIER = 1

    OBSTACLE_SPAWN_X = 900

    PLAYER_WIDTH = 95

    def __init__(self):
        for file in sorted(os.listdir(os.path.abspath(self.ASSETS_FOLDER))):
            file_path = os.path.join(self.ASSETS_FOLDER, file)
            if os.path.isfile(file_path):
                img = pygame.transform.scale_by(
                    pygame.image.load(file_path).convert_alpha(), 0.7
                )
                self.sprites.append(img)

    def tick(self, display):
        # Handle collision

        # Move obstacles
        for index, obstacle in enumerate(self.obstacles):
            if obstacle[1].bottomright[0] < 0:
                del self.obstacles[index]
            else:
                obstacle[1].x -= self.OBSTACLE_SPEED * self.SPEED_MULTIPLIER

        # General Obstacles

        self.generate()

        # Draw Obstacles
        self.draw(display)

    def generate(self):
        pass

    def draw(self, display):
        for obstacle in self.obstacles:
            display.blit(obstacle[0], obstacle[1])

    def set_jump_velocity(self, vel, acceleration):
        self.JUMP_VELOCITY = vel
        self.gravity = acceleration


# Assets
ground = pygame.image.load("Assets/ground.png")
sky = pygame.transform.scale(pygame.image.load("Assets/sky.webp"), (800, 400))


GROUND_HEIGHT = 330
obstacle = ObstacleHandler()
character = Player(80, GROUND_HEIGHT + 20, obstacle)
obstacle.set_jump_velocity(character.JUMP_VELOCITY, character.GRAVITY)


run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                character.jump()

    screen.blit(sky, (0, 0))
    screen.blit(ground, (0, GROUND_HEIGHT))
    character.tick()
    screen.blit(character.get_draw(), character.get_position())
    obstacle.tick(screen)
    pygame.display.update()

pygame.quit()
