import pygame
import sys
import random
import os
import time
from colorama import init, deinit, Fore

# Initialize colorama
init(autoreset=True)

# Initialize Pygame
try:
    os.system("cls")
    pygame.init()
except ImportError:
    print(f"{Fore.RED}Error: Pygame is not installed.")
    print(f"Please make sure to install the required dependencies using the following command:")
    print(f"pip install -r {Fore.CYAN}requirements.txt{Fore.RESET}")
    print("Check the requirements.txt file for the necessary dependencies.")
    sys.exit()
except pygame.error as e:
    print(f"{Fore.RED}Error initializing Pygame:{Fore.RESET} {e}")
    sys.exit()
finally:
    print(f"{Fore.GREEN}Game started!{Fore.RESET}")

# Load sounds
pygame.mixer.init()
die_sound = pygame.mixer.Sound("die.mp3")
score_sound = pygame.mixer.Sound("score.mp3")
die_sound.set_volume(0.2)  # Set volume to 20%
score_sound.set_volume(0.2)  # Set volume to 20%

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10
FPS = 15

# Colors
BACKGROUND_COLOR = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game constants
SCORE_FONT = pygame.font.SysFont("Consolas", 16)
TIMER_FONT = pygame.font.SysFont("Consolas", 16)
DEBUG_FONT = pygame.font.SysFont("Consolas", 16)

# Snake class
class Snake:
    """Represents the snake in the game."""

    def __init__(self):
        """Initialize the snake."""
        self.length = 1
        self.positions = [((WIDTH // 2), (HEIGHT // 2))]
        self.direction = random.choice([0, 1, 2, 3])  # 0: up, 1: down, 2: left, 3: right
        self.directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # (x, y)
        self.color = GREEN

    def get_head_position(self):
        """Get the position of the snake's head."""
        return self.positions[0]

    def update(self):
        """Update the snake's position."""
        cur = self.get_head_position()
        x, y = self.directions[self.direction]
        new = (((cur[0] + (x * GRID_SIZE)) % WIDTH), (cur[1] + (y * GRID_SIZE)) % HEIGHT)
        self.check_self_collision(new)
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_self_collision(self, new_head):
        """Check for collision with itself."""
        if new_head in self.positions[2:]:
            self.reset()

    def reset(self):
        """Reset the snake when a collision occurs."""
        print("Game Over! Restarting...")
        die_sound.play()  # Play the die sound
        time.sleep(0.5)
        self.length = 1
        self.positions = [((WIDTH // 2), (HEIGHT // 2))]
        self.direction = random.choice([0, 1, 2, 3])
        global score  # Add this line to access the global score variable
        score = 0  # Reset the score to 0
        global time_left
        time_left = time_left_maximum

    def render(self, surface):
        """Render the snake on the game surface."""
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], GRID_SIZE, GRID_SIZE))

# Apple class
class Apple:
    """Represents the apple in the game."""

    def __init__(self):
        """Initialize the apple."""
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        """Randomize the position of the apple."""
        self.position = (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
                         random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)

    def render(self, surface):
        """Render the apple on the game surface."""
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

# Initialize the screen
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
except pygame.error as e:
    print(f"{Fore.RED}Error initializing Pygame display:{Fore.RESET} {e}")
    sys.exit()

clock = pygame.time.Clock()

# Initialize the game objects
snake = Snake()
apple = Apple()

# Game variables
score = 0
high_score = 0
time_left = 30.5  # Initial time left in seconds (Default)
time_left_maximum = 30.5  # Maximum value of time left in seconds
time_left_increment = 5  # Time added to the timer when eating an apple
time_left_decrement = 0.06  # Time subtracted from the timer per frame

# Game loop
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and not snake.direction == 1:
                    snake.direction = 0
                elif event.key == pygame.K_DOWN and not snake.direction == 0:
                    snake.direction = 1
                elif event.key == pygame.K_LEFT and not snake.direction == 3:
                    snake.direction = 2
                elif event.key == pygame.K_RIGHT and not snake.direction == 2:
                    snake.direction = 3

        snake.update()

        # Check for collision with apple
        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            score_sound.play()  # Play the score sound
            if score > high_score:
                high_score = score
            apple.randomize_position()
            if time_left <= time_left_maximum:
                time_left += time_left_increment  # Add time when eating an apple

        # Check for time_left higher than time_left_max
        if time_left > time_left_maximum:
            time_left = time_left_maximum

        # Decrease time left
        time_left -= time_left_decrement

        # Game over when time runs out
        if time_left <= 0:
            snake.reset()
            time_left = time_left_maximum  # Reset the time left

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        snake.render(screen)
        apple.render(screen)

        # Draw score and high score
        score_text = SCORE_FONT.render(f"Score: {score}", True, (255, 255, 255))
        high_score_text = SCORE_FONT.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 30))
        screen.blit(high_score_text, (10, 50))

        # Draw blue progress bar representing time left
        progress_bar_length = int((time_left / 10) * 128 / 3)
        pygame.draw.rect(screen, BLUE, (10, HEIGHT - 20, progress_bar_length, 10))

        # Draw timer text
        timer_text = TIMER_FONT.render(f"Time Left: {int(time_left)}s", True, (255, 255, 255))
        screen.blit(timer_text, (10, HEIGHT - 40))

        # Draw FPS debug log
        fps_text = DEBUG_FONT.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

        pygame.display.flip()

        # Set the frame rate
        clock.tick(FPS)

except Exception as e:
    print(f"{Fore.RED}An unexpected error occurred:{Fore.RESET} {e}")
    pygame.quit()
    sys.exit()
