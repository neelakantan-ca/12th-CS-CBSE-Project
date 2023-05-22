from typing import Any
import pygame
import math
from sys import exit
import os
import random

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


class Player(pygame.sprite.Sprite):
    JUMP_HEIGHT = 150
    GRAVITY = 0.7
    TIME_OF_JUMP = math.sqrt((2 * JUMP_HEIGHT) / GRAVITY)
    JUMP_VELOCITY = GRAVITY * TIME_OF_JUMP
    ASSETS_FOLDER = "./Assets/Player"
    ANIMATION_SPEED = 0.15
    PLAYER_SCALE = 1.7

    # Player Assets

    run_sprites = []
    jump_sprite = pygame.transform.scale_by(
        pygame.image.load("./Assets/Player/jump.png").convert_alpha(),
        PLAYER_SCALE,
    )

    animation_state = 0
    player_alive = True
    score = 0

    def __init__(self, x: int, y: int, start_tick: int):
        super().__init__()

        # Load character sprites from ASSETS folder
        run_assets_path = os.path.abspath(self.ASSETS_FOLDER + "/run")
        run_assets_files = sorted(os.listdir(run_assets_path))
        for file in run_assets_files:
            file_path = os.path.join(run_assets_path, file)
            if os.path.isfile(file_path) and file_path.endswith(".png"):
                # Load and Scale Sprite
                img = pygame.transform.scale_by(
                    pygame.image.load(file_path).convert_alpha(),
                    self.PLAYER_SCALE,
                )
                self.run_sprites.append(img)

        self.position = pygame.math.Vector2(x, y)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.GROUND_HEIGHT = y
        self.START_TICK = start_tick
        self.image = self.jump_sprite
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(midbottom=(x, y))

    def onGround(self) -> bool:
        if self.position.y >= self.GROUND_HEIGHT:
            return True
        return False

    def jump(self) -> None:
        if self.onGround():
            self.velocity.y = -self.JUMP_VELOCITY
            self.acceleration.y = self.GRAVITY

    def handleInput(self) -> None:
        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[pygame.K_SPACE]:
            self.jump()

    def setPosition(self) -> None:
        self.rect = self.image.get_rect(
            midbottom=(self.position.x, self.position.y)
        )

    def gameOver(self) -> None:
        self.player_alive = False

    def animationState(self) -> None:
        if not self.onGround():
            self.animation_state = 0
            self.image = self.jump_sprite
            return
        self.animation_state += self.ANIMATION_SPEED
        if self.animation_state >= len(self.run_sprites):
            self.animation_state = 0
        self.image = self.run_sprites[int(self.animation_state)]

    def move(self) -> None:
        self.position += self.velocity + 0.5 * self.acceleration
        self.velocity += self.acceleration
        BELOW_GROUND = self.position.y > self.GROUND_HEIGHT
        if BELOW_GROUND:
            self.acceleration.y = 0
            self.velocity.y = 0
            self.position.y = self.GROUND_HEIGHT

    def calculateScore(self) -> None:
        self.score = int((pygame.time.get_ticks() - self.START_TICK) / 100)

    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.player_alive:
            self.animationState()
            self.move()
            self.handleInput()
            self.setPosition()
            self.calculateScore()
        return super().update(*args, **kwargs)


class Obstacle(pygame.sprite.Sprite):
    def __init__(
        self, img: pygame.surface.Surface, x: int, y: int, speed: int
    ):
        self.image = img
        self.x = x
        self.y = y
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = img.get_rect(midbottom=(x, y))
        super().__init__()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.x -= self.speed
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        if self.rect.bottomright[0] < 0:
            self.kill()
        return super().update(*args, **kwargs)


class ObstacleHandler:
    sprites = []
    ASSETS_FOLDER = "./Assets/Obstacles"
    OBSTACLE_SPAWN_X = 900
    OBSTACLE_SPEED = 3
    OFFSET = 50
    OBSTACLE_SPAWN_PERCENTAGE = 0.97

    def __init__(self):
        for file in sorted(os.listdir(os.path.abspath(self.ASSETS_FOLDER))):
            file_path = os.path.join(self.ASSETS_FOLDER, file)
            if os.path.isfile(file_path):
                img = pygame.transform.scale_by(
                    pygame.image.load(file_path).convert_alpha(), 0.7
                )
                self.sprites.append(img)
        self.obstacles = pygame.sprite.Group()

    def generate(self):
        if random.random() < self.OBSTACLE_SPAWN_PERCENTAGE:
            return
        air_time = Player.TIME_OF_JUMP
        furthest_distance = 0
        for obstacle in self.obstacles.sprites():
            furthest_distance = (
                obstacle.x
                if furthest_distance < obstacle.x
                else furthest_distance
            )
        obstacle = random.choice(self.sprites)
        gap_between_obstacles = self.OBSTACLE_SPAWN_X - furthest_distance
        distance_travelled_in_air = (
            air_time * self.OBSTACLE_SPEED + obstacle.get_width()
        )
        if gap_between_obstacles > distance_travelled_in_air + self.OFFSET:
            self.obstacles.add(
                Obstacle(
                    obstacle,
                    self.OBSTACLE_SPAWN_X,
                    GROUND_HEIGHT + 20,
                    self.OBSTACLE_SPEED,
                )
            )


# Assets
# ground = pygame.image.load("Assets/ground.png")
sky = pygame.transform.scale(
    pygame.image.load("Assets/desert_BG.png"), (800, 400)
)
font = pygame.font.Font(None, 30)


GROUND_HEIGHT = 330
obstacleHandler = ObstacleHandler()
characterGroup = pygame.sprite.GroupSingle()
player = Player(80, GROUND_HEIGHT + 20, pygame.time.get_ticks())
characterGroup.add(player)
# highest = 900
# lowest = 0

run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            exit()

    if pygame.sprite.spritecollide(
        player, obstacleHandler.obstacles, False, pygame.sprite.collide_mask
    ):
        player.gameOver()
    if player.player_alive:
        screen.blit(sky, (0, 0))
        # screen.blit(ground, (0, GROUND_HEIGHT))
        characterGroup.draw(screen)
        characterGroup.update()
        obstacleHandler.generate()
        obstacleHandler.obstacles.draw(screen)
        obstacleHandler.obstacles.update()
        # lowest = player.position.y if player.position.y > lowest else lowest
        # highest = player.position.y if player.position.y < highest else highest
        score_rect = font.render(
            f"Score: {player.score}",
            False,
            "Red",
        )
        screen.blit(score_rect, score_rect.get_rect(topright=(WIDTH - 10, 10)))
    # obstacle.tick(screen)
    pygame.display.update()

pygame.quit()
