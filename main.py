# ╔──────────────────────────────────────────────────────────╗
# │  ____  _               ____                              │
# │ |  _ \(_)_ __   ___   |  _ \ _   _ _ __  _ __   ___ _ __ │
# │ | | | | | '_ \ / _ \  | |_) | | | | '_ \| '_ \ / _ \ '__|│
# │ | |_| | | | | | (_) | |  _ <| |_| | | | | | | |  __/ |   │
# │ |____/|_|_| |_|\___/  |_| \_\\__,_|_| |_|_| |_|\___|_|   │
# │                                                          │
# ╚──────────────────────────────────────────────────────────╝
# Authors: Neelakantan C.A
# Version: 1.0.0

from typing import Any
import pygame
import math
import os
import random

# ╔──────────────────────────────────────────────────────────╗
# │   ____                        ____       _               │
# │  / ___| __ _ _ __ ___   ___  / ___|  ___| |_ _   _ _ __  │
# │ | |  _ / _` | '_ ` _ \ / _ \ \___ \ / _ \ __| | | | '_ \ │
# │ | |_| | (_| | | | | | |  __/  ___) |  __/ |_| |_| | |_) |│
# │  \____|\__,_|_| |_| |_|\___| |____/ \___|\__|\__,_| .__/ │
# │                                                   |_|    │
# ╚──────────────────────────────────────────────────────────╝

# Initialize the game
pygame.init()

# Set Width, Height and FPS for Game Window
WIDTH = 800
HEIGHT = 400
FPS = 60

# The clock controls how many times the game refreshes per second
clock = pygame.time.Clock()

# Setup the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Dino Run")

# Set keys to repeat after 1s of holding
pygame.key.set_repeat(100)


# ╔──────────────────────────────────────────────────────────────╗
# │  ____  _                          ___  _     _           _   │
# │ |  _ \| | __ _ _   _  ___ _ __   / _ \| |__ (_) ___  ___| |_ │
# │ | |_) | |/ _` | | | |/ _ \ '__| | | | | '_ \| |/ _ \/ __| __|│
# │ |  __/| | (_| | |_| |  __/ |    | |_| | |_) | |  __/ (__| |_ │
# │ |_|   |_|\__,_|\__, |\___|_|     \___/|_.__// |\___|\___|\__|│
# │                |___/                      |__/               │
# ╚──────────────────────────────────────────────────────────────╝
class Player(pygame.sprite.Sprite):
    """Player An instance of a player in the game

    An instance of a player with associated to functions to manipulate player.

    Attributes
    ----------
    JUMP_HEIGHT : int
        The height in pixels the player moves up on each jump
    GRAVITY : float
        The gravity which affects how fast the player will fall down after
        jumping
    TIME_OF_JUMP : float
        Automatically calculated value. Used to determine minimum time between
        obstacle spawns
    ASSETS_FOLDER : str
        Folder where player assets are stored
    ANIMATION_SPEED : float
        Controls the animation speed (time between player sprite changes)
    PLAYER_SCALE : float
        Sets the player scale relative the source image / sprite.
    score : int
        The score is calculated when the current player's game is over
            (ie) Player is dead.
        It is a measure of how well the player performed.

    """

    JUMP_HEIGHT = 125
    GRAVITY = 0.7
    TIME_OF_JUMP = math.sqrt((2 * JUMP_HEIGHT) / GRAVITY)
    JUMP_VELOCITY = GRAVITY * TIME_OF_JUMP
    ASSETS_FOLDER = "./Assets/Player"
    ANIMATION_SPEED = 0.15
    PLAYER_SCALE = 1.7

    # Player Assets

    _run_sprites = []
    _animation_state = 0
    _is_alive = True
    score = 0

    def __init__(self, x: int, y: int, start_tick: int) -> None:
        """__init__ Creates an instance of a player.

        Parameters
        ----------
        x : int
            The starting `x` position of a player
        y : int
            The starting `y` position of a player
        start_tick : int
            The tick of the game's clock at which player was created.
            (Scoring begins from this time)

        """

        super().__init__()

        # Load character sprites from ASSETS folder
        run_assets_path = os.path.abspath(self.ASSETS_FOLDER + "/run")
        # Sort player assets to ensure consistent ordering across runs
        run_assets_files = sorted(os.listdir(run_assets_path))
        for file in run_assets_files:
            # Check if the asset selected is an image
            if not file.endswith(".png"):
                continue
            # Get the full path to each asset
            file_path = os.path.join(run_assets_path, file)
            if not os.path.isfile(file_path):
                continue
            # Load the sprite and set the scale
            img = pygame.transform.scale_by(
                pygame.image.load(file_path).convert_alpha(),
                self.PLAYER_SCALE,
            )
            # Append individual sprite frames to a list
            self._run_sprites.append(img)

        # Set the sprite used during jumping
        self.jump_sprite = pygame.transform.scale_by(
            pygame.image.load("./Assets/Player/jump.png").convert_alpha(),
            self.PLAYER_SCALE,
        )
        # Players position vector created based on initial coordinates
        self.position = pygame.math.Vector2(x, y)
        # Players acceleration vector
        self.acceleration = pygame.math.Vector2(0, 0)
        # Players velocity vector
        self.velocity = pygame.math.Vector2(0, 0)
        # Assume the players initially on the ground and set the height to
        # players current y coordinate
        self.GROUND_HEIGHT = y
        self.START_TICK = start_tick
        # Initialize the default sprite of the player as the jumping sprite
        self.image = self.jump_sprite
        # Create a mask from the sprite of player
        # The mask is used to calculate collisions
        self.mask = pygame.mask.from_surface(self.image)
        # Set the location of player's sprite at the provided coordinates
        self.rect = self.image.get_rect(midbottom=(x, y))

    def on_ground(self) -> bool:
        """on_ground Determines whether the player is on the ground.

        Returns `True` if player is on the ground, `False` if player is in the
        air

        Returns
        -------
        bool
            Result: True (Player on ground) | False (Player in air)
        """

        # Check if the player's y coordinate is above the height of the ground
        PLAYER_ABOVE_GROUND = self.position.y >= self.GROUND_HEIGHT
        if PLAYER_ABOVE_GROUND:
            return True
        return False

    def jump(self) -> None:
        """jump Makes the player jump

        This function is used to make the player instance start a jump
        """

        # Set an upwards velocity on the player to make the player jump
        # Only if the player is current on the ground
        # Also reset acceleration to gravity until jump is over
        ON_GROUND = self.on_ground()
        if ON_GROUND:
            self.velocity.y = -self.JUMP_VELOCITY
            self.acceleration.y = self.GRAVITY

    def _handle_input(self) -> None:
        """_handle_input Controls inputs made the user on the player object

        Handles user controlled player actions
        """

        # Gets all keys pressed
        pressedKeys = pygame.key.get_pressed()
        # Handle each key action
        if pressedKeys[pygame.K_SPACE]:
            self.jump()

    def _set_position(self) -> None:
        """_set_position Sets the player position

        Sets the player position based on the player's position vector
        """

        self.rect = self.image.get_rect(
            midbottom=(self.position.x, self.position.y)
        )

    def game_over(self) -> None:
        """game_over Ends the game for the player instance

        The game ends for the current player. The global game can still
        continue however the current player will no longer move and scoring
        will have paused.
        """

        self._is_alive = False
        self._calculate_score()

    def update_animation_state(self) -> None:
        """update_animation_state is called to set the new sprite for the
        player.

        This function is called each new frame to calculate what sprite is
        used for the player.
        """

        ON_GROUND = self.on_ground()
        if not ON_GROUND:
            self._animation_state = 0
            self.image = self.jump_sprite
            return
        self._animation_state += self.ANIMATION_SPEED
        ANIMATION_ENDED = self._animation_state >= len(self._run_sprites)
        if ANIMATION_ENDED:
            self._animation_state = 0
        self.image = self._run_sprites[int(self._animation_state)]

    def move(self) -> None:
        """move is called to recalculate the player's position

        The function is called to calculate the player's new vertical position.
        """

        self.position += self.velocity + 0.5 * self.acceleration
        self.velocity += self.acceleration
        BELOW_GROUND = self.position.y > self.GROUND_HEIGHT
        if BELOW_GROUND:
            self.acceleration.y = 0
            self.velocity.y = 0
            self.position.y = self.GROUND_HEIGHT

    def _calculate_score(self) -> None:
        """_calculate_score calculates the score of the player

        This function is called when the player dies to calculate the
        performance of the player
        """

        self.score = int((pygame.time.get_ticks() - self.START_TICK) / 100)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """update is called every frame, and handles making player updates.

        This function is called every new frame. All updates to player are
        calculated and handled when from this function call
        """

        if self._is_alive:
            self.update_animation_state()
            self.move()
            self._handle_input()
            self._set_position()


# ╔───────────────────────────────────────╗
# │   ___  _         _             _      │
# │  / _ \| |__  ___| |_ __ _  ___| | ___ │
# │ | | | | '_ \/ __| __/ _` |/ __| |/ _ \│
# │ | |_| | |_) \__ \ || (_| | (__| |  __/│
# │  \___/|_.__/|___/\__\__,_|\___|_|\___|│
# │                                       │
# ╚───────────────────────────────────────╝
class Obstacle(pygame.sprite.Sprite):
    """Obstacle Each obstacle in game, is an instance of this class

    Each obstacle in the game is an instance of this class.
    This class handles updating the position of the obstacle.
    And handle object deletion after the object is off-screen.

    """

    def __init__(
        self, img: pygame.surface.Surface, x: int, y: int, speed: int
    ):
        """__init__ Creates an obstacle

        Creates an instance of an obstacle the player would have to avoid

        Parameters
        ----------
        img : pygame.surface.Surface
            The image used for the obstacle
        x : int
            Initial spawn x of the obstacle
        y : int
            Initial spawn y of the obstacle
        speed : int
            The speed at which the obstacle moves towards the left of the
            screen
        """

        self.image = img
        self.x = x
        self.y = y
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = img.get_rect(midbottom=(x, y))
        super().__init__()

    def update(self, *args: Any, **kwargs: Any) -> None:
        """update Handles updates to the obstacle each frame

        This function is called each time the screen is updated.
        Updates to obstacle properties are made within this function.

        """

        # Check if the obstacle outside the screen area
        # If the obstacle is outside the screen, destroy the object
        OBSTACLE_OFF_SCREEN = self.rect.bottomright[0] < 0
        if OBSTACLE_OFF_SCREEN:
            return self.kill()
        # Calculate the new position of the obstacle
        self.x -= self.speed
        # Update the position of the obstacle
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))


# ╔───────────────────────────────────────╗
# │   ___  _         _             _      │
# │  / _ \| |__  ___| |_ __ _  ___| | ___ │
# │ | | | | '_ \/ __| __/ _` |/ __| |/ _ \│
# │ | |_| | |_) \__ \ || (_| | (__| |  __/│
# │  \___/|_.__/|___/\__\__,_|\___|_|\___|│
# │  _   _                 _ _            │
# │ | | | | __ _ _ __   __| | | ___ _ __  │
# │ | |_| |/ _` | '_ \ / _` | |/ _ \ '__| │
# │ |  _  | (_| | | | | (_| | |  __/ |    │
# │ |_| |_|\__,_|_| |_|\__,_|_|\___|_|    │
# │                                       │
# ╚───────────────────────────────────────╝
class ObstacleHandler:
    """Manages all obstacle instances at run time

    This class handles creation, tracking and updating all obstacles generated
    during run time.

    Attributes
    ----------

    ASSETS_FOLDER : str
        The folder from which images for obstacles are pulled from.
    OBSTACLE_SPAWN_X : int
        The initial x position at which obstacles are created.
    OBSTACLE_SPEED : int
        The speed in pixels that the obstacle moves towards the left of the
        screen.
    OFFSET : int
        The minimum distance between successive generated obstacles.
    OBSTACLE_SPAWN_PERCENTAGE : int
        The percentage chance that an obstacle is generated each frame as long
        as `OFFSET` is maintained.
    """

    ASSETS_FOLDER = "./Assets/Obstacles"
    OBSTACLE_SPAWN_X = 900
    OBSTACLE_SPEED = 5
    OFFSET = 50
    OBSTACLE_SPAWN_PERCENTAGE = 0.97

    def __init__(self, ground_height: int):
        """__init__ This function is used to create a handler for all obstacles


        Parameters
        ----------
        ground_height : int
            The height at which the ground is at. Used as the height to spawn
            obstacles at.
        """

        self.sprites = []
        for file in sorted(os.listdir(os.path.abspath(self.ASSETS_FOLDER))):
            file_path = os.path.join(self.ASSETS_FOLDER, file)
            if not (os.path.isfile(file_path) and file_path.endswith(".png")):
                continue
            img = pygame.transform.scale_by(
                pygame.image.load(file_path).convert_alpha(), 0.2
            )
            self.sprites.append(img)
        self.obstacles = pygame.sprite.Group()
        self.GROUND_HEIGHT = ground_height

    def generate(self) -> None:
        """generate is called to create a new obstacle.

        This function is called every time a new obstacle is needed.
        The function only creates a new obstacle if able to do so.
        """

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
        distance_traveled_in_air = (
            air_time * self.OBSTACLE_SPEED + obstacle.get_width()
        )
        if not (
            gap_between_obstacles > distance_traveled_in_air + self.OFFSET
        ):
            return
        self.obstacles.add(
            Obstacle(
                obstacle,
                self.OBSTACLE_SPAWN_X,
                self.GROUND_HEIGHT + 20,
                self.OBSTACLE_SPEED,
            )
        )


# ╔─────────────────────────────╗
# │   ____                      │
# │  / ___| __ _ _ __ ___   ___ │
# │ | |  _ / _` | '_ ` _ \ / _ \│
# │ | |_| | (_| | | | | | |  __/│
# │  \____|\__,_|_| |_| |_|\___|│
# │                             │
# ╚─────────────────────────────╝
class Game:
    """An instance of a game.

    This class handles running one instance of a game.
    """

    def __init__(
        self,
        screen: pygame.surface.Surface,
        background: pygame.surface.Surface,
        font: pygame.font.Font,
        ground_height: int = 330,
    ) -> None:
        """__init__ Used to create a game instance

        Sets all parameters for the game.

        Parameters
        ----------
        screen : pygame.surface.Surface
            The screen on which the game is to be displayed
        background : pygame.surface.Surface
            The background art used in the game
        font : pygame.font.Font
            The font to be used for rendering text
        ground_height : int, optional
            The height at which the ground should be rendered, by default 330
        """

        self.sky = background
        self.font = font
        self.GROUND_HEIGHT = ground_height

        self.obstacleHandler = ObstacleHandler(self.GROUND_HEIGHT)
        self.characterGroup = pygame.sprite.GroupSingle()
        self.player = Player(
            80, self.GROUND_HEIGHT + 20, pygame.time.get_ticks()
        )
        self.characterGroup.add(self.player)

    def run(self) -> int:
        """run runs the game

        This function starts a blocking game loop that terminates when the
        player dies.

        Returns
        -------
        int
            The score of the player is returned to the calling class.
        """

        while self.player._is_alive:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.player.score

            if pygame.sprite.spritecollide(
                self.player,
                self.obstacleHandler.obstacles,
                False,
                pygame.sprite.collide_mask,  # type: ignore
            ):
                self.player.game_over()

            screen.blit(sky, (0, 0))

            if not (self.player._is_alive):
                break
            self.characterGroup.draw(screen)
            self.characterGroup.update()
            self.obstacleHandler.generate()
            self.obstacleHandler.obstacles.draw(screen)
            self.obstacleHandler.obstacles.update()
            score_rect = font.render(
                f"Score: {self.player.score}",
                False,
                "Red",
            )
            screen.blit(
                score_rect, score_rect.get_rect(topright=(WIDTH - 10, 10))
            )
            # obstacle.tick(screen)
            pygame.display.update()
        return self.player.score


# Assets
# ground = pygame.image.load("Assets/ground.png")
sky = pygame.transform.scale(
    pygame.image.load("Assets/desert_BG.png"), (800, 400)
)
font = pygame.font.Font(None, 30)

game = Game(screen=screen, background=sky, font=font)

score = game.run()

print(score)

pygame.quit()
