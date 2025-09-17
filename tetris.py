import pygame
import random
import sys
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Tetris pieces (tetrominoes) with their rotations
PIECES = {
    'I': [
        ['....', '####', '....', '....'],
        ['..#.', '..#.', '..#.', '..#.'],
        ['....', '####', '....', '....'],
        ['..#.', '..#.', '..#.', '..#.']
    ],
    'O': [
        ['....', '.##.', '.##.', '....']
    ],
    'T': [
        ['....', '.#..', '###.', '....'],
        ['....', '.#..', '.##.', '.#..'],
        ['....', '....', '###.', '.#..'],
        ['....', '.#..', '##..', '.#..']
    ],
    'S': [
        ['....', '.##.', '##..', '....'],
        ['....', '.#..', '.##.', '..#.']
    ],
    'Z': [
        ['....', '##..', '.##.', '....'],
        ['....', '..#.', '.##.', '.#..']
    ],
    'J': [
        ['....', '.#..', '.###', '....'],
        ['....', '..##', '..#.', '..#.'],
        ['....', '....', '###.', '..#.'],
        ['....', '.#..', '.#..', '##..']
    ],
    'L': [
        ['....', '..#.', '###.', '....'],
        ['....', '.#..', '.#..', '.##.'],
        ['....', '....', '###.', '#...'],
        ['....', '##..', '.#..', '.#..']
    ]
}

PIECE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class Piece:
    def __init__(self, shape: str):
        self.shape = shape
        self.color = PIECE_COLORS[shape]
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0
    
    def get_rotated_piece(self) -> List[str]:
        return PIECES[self.shape][self.rotation % len(PIECES[self.shape])]
    
    def get_cells(self) -> List[Tuple[int, int]]:
        cells = []
        pattern = self.get_rotated_piece()
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + x, self.y + y))
        return cells

class TetrisGame:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.game_over = False
        
        # Initialize display
        self.screen_width = GRID_WIDTH * CELL_SIZE + 2 * GRID_X_OFFSET + 200
        self.screen_height = GRID_HEIGHT * CELL_SIZE + 2 * GRID_Y_OFFSET
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tetris")
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def get_new_piece(self) -> Piece:
        return Piece(random.choice(list(PIECES.keys())))
    
    def is_valid_position(self, piece: Piece, dx: int = 0, dy: int = 0, rotation: int = None) -> bool:
        if rotation is None:
            rotation = piece.rotation
        
        old_rotation = piece.rotation
        piece.rotation = rotation
        
        for x, y in piece.get_cells():
            new_x, new_y = x + dx, y + dy
            if (new_x < 0 or new_x >= GRID_WIDTH or 
                new_y >= GRID_HEIGHT or 
                (new_y >= 0 and self.grid[new_y][new_x] != BLACK)):
                piece.rotation = old_rotation
                return False
        
        piece.rotation = old_rotation
        return True
    
    def place_piece(self, piece: Piece):
        for x, y in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared
        
        # Scoring system
        if lines_cleared > 0:
            self.score += [0, 40, 100, 300, 1200][lines_cleared] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def move_piece(self, dx: int, dy: int) -> bool:
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        new_rotation = (self.current_piece.rotation + 1) % len(PIECES[self.current_piece.shape])
        if self.is_valid_position(self.current_piece, rotation=new_rotation):
            self.current_piece.rotation = new_rotation
    
    def drop_piece(self):
        if not self.move_piece(0, 1):
            self.place_piece(self.current_piece)
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.get_new_piece()
            
            if not self.is_valid_position(self.current_piece):
                self.game_over = True
    
    def hard_drop(self):
        while self.move_piece(0, 1):
            self.score += 2
        self.drop_piece()
    
    def draw_grid(self):
        # Draw background
        self.screen.fill(DARK_GRAY)
        
        # Draw game area background
        game_area = pygame.Rect(GRID_X_OFFSET, GRID_Y_OFFSET, 
                               GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, BLACK, game_area)
        
        # Draw placed pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != BLACK:
                    rect = pygame.Rect(GRID_X_OFFSET + x * CELL_SIZE,
                                     GRID_Y_OFFSET + y * CELL_SIZE,
                                     CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Draw current piece
        if not self.game_over:
            for x, y in self.current_piece.get_cells():
                if y >= 0:
                    rect = pygame.Rect(GRID_X_OFFSET + x * CELL_SIZE,
                                     GRID_Y_OFFSET + y * CELL_SIZE,
                                     CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.current_piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET),
                           (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE))
        
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE),
                           (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE))
    
    def draw_next_piece(self):
        next_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        next_y = GRID_Y_OFFSET + 50
        
        # Draw "Next" label
        text = self.font.render("Next:", True, WHITE)
        self.screen.blit(text, (next_x, next_y - 30))
        
        # Draw next piece preview
        pattern = self.next_piece.get_rotated_piece()
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell == '#':
                    rect = pygame.Rect(next_x + x * CELL_SIZE // 2,
                                     next_y + y * CELL_SIZE // 2,
                                     CELL_SIZE // 2, CELL_SIZE // 2)
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_info(self):
        info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        info_y = GRID_Y_OFFSET + 150
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (info_x, info_y))
        
        # Lines
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (info_x, info_y + 40))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (info_x, info_y + 80))
        
        # Controls
        controls_y = info_y + 140
        controls = [
            "Controls:",
            "← → : Move",
            "↓ : Soft Drop",
            "Space: Hard Drop",
            "↑ : Rotate",
            "R: Restart"
        ]
        
        for i, control in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            font = self.font if i == 0 else self.small_font
            text = font.render(control, True, color)
            self.screen.blit(text, (info_x, controls_y + i * 25))
    
    def draw_game_over(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        restart_text = self.small_font.render("Press R to restart", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        self.__init__()
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            dt = clock.tick(60)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
            
            # Game logic
            if not self.game_over:
                self.fall_time += dt
                if self.fall_time >= self.fall_speed:
                    self.drop_piece()
                    self.fall_time = 0
            
            # Draw everything
            self.draw_grid()
            self.draw_next_piece()
            self.draw_info()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()