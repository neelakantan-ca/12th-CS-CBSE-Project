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

from typing import Any, List
import pygame
import math
import os
import random
import neat
import argparse

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

    JUMP_HEIGHT = 100
    GRAVITY = 0.4
    TIME_OF_JUMP = math.sqrt((2 * JUMP_HEIGHT) / GRAVITY)
    JUMP_VELOCITY = GRAVITY * TIME_OF_JUMP
    ASSETS_FOLDER = "./Assets/Player"
    ANIMATION_SPEED = 0.17
    PLAYER_SCALE = 1.7

    # Player Assets

    _run_sprites = []
    _animation_state = 0
    _is_alive = True

    score = 0

    def __init__(
        self, x: int, y: int, start_tick: int, obstacle_handler
    ) -> None:
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
        self.obstacle_handler = obstacle_handler

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

    def __init__(self):
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

    def set_ground_height(self, ground_height) -> None:
        self.GROUND_HEIGHT = ground_height

    def get_closest(self) -> int:
        closest = self.OBSTACLE_SPAWN_X
        for obstacle in self.obstacles.sprites():
            if (
                closest > obstacle.rect.bottomleft[0] - 80
                and obstacle.rect.bottomleft[0] > 80
            ):
                closest = obstacle.rect.bottomleft[0] - 80
        return closest

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
            if furthest_distance < obstacle.x:
                furthest_distance = obstacle.x
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

    sky = pygame.transform.scale(
        pygame.image.load("Assets/desert_BG.png"), (800, 400)
    )
    font = pygame.font.Font(None, 30)

    def __init__(
        self,
        screen: pygame.surface.Surface,
        player: List[Player],
        obstacleHandler: ObstacleHandler,
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

        self.GROUND_HEIGHT = player[0].GROUND_HEIGHT - 20
        self.screen = screen
        self.obstacleHandler = obstacleHandler
        self.obstacleHandler.set_ground_height(self.GROUND_HEIGHT)
        self.characterGroup = pygame.sprite.Group()
        self.players = player
        self.characterGroup.add(self.players)

    def run_multiple(self):
        """run runs the game

        This function starts a blocking game loop that terminates when the
        player dies.

        Returns
        -------
        int
            The score of the player is returned to the calling class.
        """
        pygame.key.set_repeat(100)
        alive = list(self.players)
        dead = []
        while len(alive) > 0:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [player.score for player in self.players]
            for i, player in enumerate(alive):
                if pygame.sprite.spritecollide(
                    player,
                    self.obstacleHandler.obstacles,
                    False,
                    pygame.sprite.collide_mask,  # type: ignore
                ):
                    player.game_over()
                    self.characterGroup.remove(player)
                    dead.append(alive.pop(i))
            self.characterGroup.update()
            self.obstacleHandler.generate()
            self.obstacleHandler.obstacles.update()
            scores = [player.score for player in alive]
            if self.screen is not None:
                self.screen.blit(self.sky, (0, 0))
                self.characterGroup.draw(self.screen)
                self.obstacleHandler.obstacles.draw(self.screen)
                score_rect = self.font.render(
                    f"Score: {scores[0] if len(scores) > 0 else 0}",
                    False,
                    "Red",
                )
                self.screen.blit(
                    score_rect, score_rect.get_rect(topright=(WIDTH - 10, 10))
                )
            pygame.display.update()
        return [player.score for player in self.players]

    def scoreboard(self, scores: List[tuple[str, int]]):
        """scoreboard displays the scoreboard

        Displays the scoreboard on the screen provided to the `game` class

        Parameters
        ----------
        scores : List[tuple[str, int]]
            A list of tuples in the format `(name, score)` retrieved from
            database
        """

        index = 0
        background = pygame.image.load("Assets/scoreboard.png")
        text_x: int = 245
        score_rects = [
            self.font.render(f"{score[0]} - {score[1]}", True, "Red")
            for score in scores
        ]

        while True:
            text_y: int = 135
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        return
                    case pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if (10 <= x <= 66) and (340 <= y <= 383):
                            if 0 <= index - 4:
                                index -= 4
                        elif (10 <= x <= 66) and (25 <= y <= 68):
                            print("Return to main menu")
                        elif (730 <= x <= 785) and (340 <= y <= 383):
                            if index + 4 < len(score_rects):
                                print("test")
                                index += 4

            clock.tick(FPS)
            self.screen.blit(background, (0, 0))
            scores_to_display = score_rects[index : index + 3]
            for score_rect in scores_to_display:
                self.screen.blit(
                    score_rect,
                    score_rect.get_rect(bottomleft=(text_x, text_y)),
                )
                text_y += 75
            pygame.display.update()


class AI(Player):
    def __init__(
        self,
        x: int,
        y: int,
        start_tick: int,
        obstacle_handler: ObstacleHandler,
        genome,
        config: str,
    ):
        super().__init__(x, y, start_tick, obstacle_handler)
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0

    def _handle_input(self) -> None:
        inputs = (self.position.y, self.obstacle_handler.get_closest(), FPS)
        # print(inputs[1])
        if self.net.activate((inputs))[0] > 0.5:
            self.jump()

    def _calculate_score(self) -> None:
        super()._calculate_score()
        self.genome.fitness = self.score


class NeatHelper:
    def __init__(self, path: str) -> None:
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            path,
        )

    def train(self):
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.population.add_reporter(neat.StatisticsReporter())

        return self.population.run(self.fitness, 200)

    def fitness(self, genomes, config):
        runners = []
        obstacleHandler = ObstacleHandler()
        for _, genome in genomes:
            runners.append(
                AI(
                    80,
                    350,
                    pygame.time.get_ticks(),
                    obstacleHandler,
                    genome,
                    config,
                )
            )
        game = Game(screen, runners, obstacleHandler)
        game.run_multiple()


parser = argparse.ArgumentParser(
    description="A simple game", formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "--type",
    choices=["AI", "M"],
    dest="mode",
    help="Sets the play mode.\n\n\tM  - Manual Player Mode\n\tAI - \
Artificial Intelligence",
    required=True,
)
args = parser.parse_args()

if args.mode == "AI":
    ai_helper = NeatHelper("./neat_config")

    ai_helper.train()
elif args.mode == "M":
    obstacleHandler = ObstacleHandler()

    game = Game(
        screen=screen,
        player=[
            Player(80, 330 + 20, pygame.time.get_ticks(), obstacleHandler)
        ],
        obstacleHandler=obstacleHandler,
    )

    score = game.run_multiple()

    print(score)

    game.scoreboard([("Name " + str(i), 500) for i in range(1, 20)])

pygame.quit()
