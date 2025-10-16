import pygame
import random
import sys
import math
# Khởi tạo pygame
pygame.init()

# Các thông số cơ bản
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
BASE_SPEED = 10
SPEED_STEP = 0.5

# Màu sắc
BACKGROUND_COLOR = (244, 201, 127)  # Màu vàng nhạt
BORDER_COLOR = (139, 90, 43)  # Màu nâu
SNAKE_BODY_COLOR = (34, 139, 34)  # Xanh lá đậm
SNAKE_HEAD_COLOR = (0, 100, 0)  # Xanh lá đậm hơn
SNAKE_EYE_COLOR = (255, 255, 255)  # Trắng
FOOD_COLOR = (255, 69, 0)  
GRID_COLOR = (232, 178, 108)  
TEXT_COLOR = (255, 255, 255) 
BUTTON_COLOR = (50, 150, 50)
BUTTON_HOVER_COLOR = (70, 170, 70)

# Hướng di chuyển
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (cur[0] + x, cur[1] + y)

        if new[0] < 0 or new[0] >= GRID_WIDTH or new[1] < 0 or new[1] >= GRID_HEIGHT:
            return False

        if new in self.positions[2:]:
            return False

        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

class Food:
    def __init__(self, snake):
        self.snake = snake
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake.positions:
                self.position = pos
                break

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.is_running = True
        self.is_paused = False
        self.high_score = 0
        self.restart_button = Button(
            WINDOW_WIDTH // 2 - 75,
            WINDOW_HEIGHT // 2 + 50,
            150,
            50,
            "Restart",
            BUTTON_COLOR,
            BUTTON_HOVER_COLOR,
            TEXT_COLOR,
            self.font,
        )
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food(self.snake)
        self.is_running = True
        self.is_paused = False

    def draw_grid(self):
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_score(self):
        score_text = self.font.render(
            f'Score: {self.snake.score}  Best: {self.high_score}', True, TEXT_COLOR
        )
        self.screen.blit(score_text, (10, 10))

    def draw_food(self):
        food_center = (
            int(self.food.position[0] * GRID_SIZE + GRID_SIZE / 2),
            int(self.food.position[1] * GRID_SIZE + GRID_SIZE / 2),
        )
        pygame.draw.circle(self.screen, FOOD_COLOR, food_center, int(GRID_SIZE / 2))

    def draw_snake(self):
        for i, pos in enumerate(self.snake.positions):
            x, y = pos
            center = (int(x * GRID_SIZE + GRID_SIZE / 2), int(y * GRID_SIZE + GRID_SIZE / 2))
            
            if i == 0:  # Head
                pygame.draw.circle(self.screen, SNAKE_HEAD_COLOR, center, int(GRID_SIZE / 2))
                
                # Eyes
                eye_offset = 3
                left_eye = (center[0] - eye_offset, center[1] - eye_offset)
                right_eye = (center[0] + eye_offset, center[1] - eye_offset)
                pygame.draw.circle(self.screen, SNAKE_EYE_COLOR, left_eye, 2)
                pygame.draw.circle(self.screen, SNAKE_EYE_COLOR, right_eye, 2)
                
            else:  # Body
                pygame.draw.circle(self.screen, SNAKE_BODY_COLOR, center, int(GRID_SIZE / 2) - 1)
            
            # Connect segments
            if i > 0:
                prev = self.snake.positions[i-1]
                current = pos
                pygame.draw.line(self.screen, SNAKE_BODY_COLOR, 
                                 (prev[0] * GRID_SIZE + GRID_SIZE / 2, prev[1] * GRID_SIZE + GRID_SIZE / 2),
                                 (current[0] * GRID_SIZE + GRID_SIZE / 2, current[1] * GRID_SIZE + GRID_SIZE / 2),
                                 int(GRID_SIZE / 2))

    def game_over_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        title = self.font.render("Game Over!", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        summary_lines = [
            f"Score: {self.snake.score}",
            f"Best: {self.high_score}",
            "Press Enter to play again",
            "Press Esc to quit",
        ]
        for idx, line in enumerate(summary_lines):
            text = self.font.render(line, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20 + idx * 35))
            self.screen.blit(text, text_rect)

        self.restart_button.draw(self.screen)
        pygame.display.update()

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        pause_text = self.font.render("Paused - Press Space to resume", True, TEXT_COLOR)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        pygame.display.update()

    def handle_keydown(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if self.is_running:
            if key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
                return

            if self.is_paused:
                return

            if key == pygame.K_UP:
                self.snake.change_direction(UP)
            elif key == pygame.K_DOWN:
                self.snake.change_direction(DOWN)
            elif key == pygame.K_LEFT:
                self.snake.change_direction(LEFT)
            elif key == pygame.K_RIGHT:
                self.snake.change_direction(RIGHT)
        else:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
                self.reset_game()

    def update_game_state(self):
        if not self.snake.update():
            self.is_running = False
            self.high_score = max(self.high_score, self.snake.score)
            return

        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.snake.score += 10
            self.food.randomize_position()
            self.high_score = max(self.high_score, self.snake.score)

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        self.draw_score()
        pygame.display.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                elif not self.is_running and self.restart_button.is_clicked(event):
                    self.reset_game()

            if self.is_running and not self.is_paused:
                self.update_game_state()
                if not self.is_running:
                    continue
                self.render()
                speed = BASE_SPEED + int(self.snake.score * SPEED_STEP / 10)
                self.clock.tick(speed)
            elif self.is_paused:
                self.draw_pause_overlay()
                self.clock.tick(10)
            else:
                self.game_over_screen()

if __name__ == "__main__":
    game = Game()
    game.run()
