import pygame
from .constants import PIECE_DARK, PIECE_LIGHT, BLUE, SQUARE_SIZE, ROWS, COLS, WIDTH, HEIGHT, GREY, BOARD_DARK, BOARD_LIGHT
import math
import time

# Import Piece class
from .piece import Piece

class Game:
    def __init__(self, win, difficulty, show_help=False):
        self.difficulty = difficulty
        self.show_valid_moves = show_help  # Use the help choice parameter instead of difficulty
        self._init()
        self.win = win
        self.board_offset_y = 200
        self.black_icon = pygame.image.load("assets/black_piece.png")
        self.red_icon = pygame.image.load("assets/white_piece.png")
        # Adjust pause button position for smaller window
        self.pause_button = pygame.Rect(WIDTH - 110, 20, 100, 100)
        self.pause_icon_color = (255, 255, 255)
        # Initialize timers (10 minutes in seconds)
        self.black_time = 10 * 60
        self.white_time = 10 * 60
        self.last_time = time.time()
        self.is_paused = False
        # Load move sound
        try:
            self.move_sound = pygame.mixer.Sound('assets/move-self.mp3')
            self.enable_move_sound = False  # Default to False, set in main.py
        except pygame.error as e:
            print(f"[ERROR] Failed to load move-self.mp3: {e}")
            self.move_sound = None

    def _init(self):
        self.selected = None
        self.board = Board(self)  # Pass the Game instance to Board
        self.turn = PIECE_DARK
        self.valid_moves = {}
        self.black_score = 0
        self.white_score = 0
        # Reset timers
        self.black_time = 10 * 60
        self.white_time = 10 * 60
        self.last_time = time.time()
        self.is_paused = False

    def update(self):
        # Update timers
        if not self.is_paused:
            current_time = time.time()
            elapsed = current_time - self.last_time
            if self.turn == PIECE_DARK:
                self.black_time = max(0, self.black_time - elapsed)
            else:
                self.white_time = max(0, self.white_time - elapsed)
            self.last_time = current_time

        self.board.draw(self.win, self.turn, self.black_time, self.white_time)
        if self.show_valid_moves:
            self.draw_valid_moves(self.valid_moves)
        self.draw_scores()
        self.draw_pause_button()
        pygame.display.update()

    def winner(self):
        # Check for timer-based wins
        if self.black_time <= 0:
            return PIECE_LIGHT  # White wins if black's time runs out
        if self.white_time <= 0:
            return PIECE_DARK  # Black wins if white's time runs out
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        # Check if the click is outside the board boundaries
        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return "nothing_selected"
            
        # If we have a selected piece, try to move it
        if self.selected:
            # Call move with the selected piece and the position clicked
            result = self._move(row, col)
            
            if not result:
                # If the move wasn't valid, we deselect or select a new piece
                self.selected = None
                return self.select(row, col)  # Recursively call select to re-evaluate the click
            else:
                return "move_made"  # Indicate that a move was successfully made
            
        piece = self.board.get_piece(row, col)
        
        # If there's no piece at the selected position or it's not the current player's piece
        if piece == 0 or piece.color != self.turn:
            return "nothing_selected"
            
        # Valid selection
        self.valid_moves = self.board.get_valid_moves(piece)
        
        # If there are no valid moves for this piece
        if not self.valid_moves:
            return "nothing_selected"
            
        self.selected = piece
        return "piece_selected"

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            
            if skipped:
                self.board.remove(skipped)
                if self.turn == PIECE_DARK:
                    self.black_score += len(skipped)
                else:
                    self.white_score += len(skipped)
                new_moves = self.board.get_valid_moves(self.selected)
                capture_moves = {move: skips for move, skips in new_moves.items() if skips}
                
                if capture_moves:
                    self.valid_moves = capture_moves
                    return True
            
            if row == 0 or row == ROWS - 1:
                self.selected.make_king()
                if self.selected.color == PIECE_LIGHT:
                    self.board.red_kings += 1
                else:
                    self.board.white_kings += 1
            
            self.change_turn()
            # Play move sound if available and enabled
            if self.move_sound and getattr(self, 'enable_move_sound', False):
                self.move_sound.play()

            self.selected = None # Deselect the piece after a successful move

            return True
        return False

    def draw_valid_moves(self, moves):
        self.board.draw_valid_moves(self.win, moves)  # Pass win to Board.draw_valid_moves

    def draw_scores(self):
        font = pygame.font.SysFont('Consolas', 40, bold=True)
        title_font = pygame.font.SysFont('Consolas', 35, bold=True)
        screen_width = self.win.get_width()
        rect_width = 250  # Reduced width
        rect_height = 120
        rect_x = 40  # Move to left with 40px margin
        rect_y = 20
        border_radius = 20

        # Draw the black border with rounded corners
        pygame.draw.rect(self.win, (0, 0, 0), (rect_x - 2, rect_y - 2, rect_width + 4, rect_height + 4), border_radius=border_radius)

        # Draw the background panel
        pygame.draw.rect(self.win, (128, 128, 128), (rect_x, rect_y, rect_width, rect_height), border_radius=border_radius)

        # Draw "Score" title
        title_text = title_font.render("Score", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=rect_x + rect_width//2, top=rect_y + 10)
        self.win.blit(title_text, title_rect)

        # Draw scores
        # Black score (left)
        black_score_text = font.render(str(self.black_score), True, (255, 255, 255))
        black_score_rect = black_score_text.get_rect(center=(rect_x + rect_width//4, rect_y + 80))
        pygame.draw.circle(self.win, (0, 0, 0), black_score_rect.center, 35)
        self.win.blit(black_score_text, black_score_rect)

        # White score (right)
        white_score_text = font.render(str(self.white_score), True, (0, 0, 0))
        white_score_rect = white_score_text.get_rect(center=(rect_x + 3*rect_width//4, rect_y + 80))
        pygame.draw.circle(self.win, (255, 255, 255), white_score_rect.center, 35)
        self.win.blit(white_score_text, white_score_rect)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == PIECE_DARK:
            self.turn = PIECE_LIGHT
        else:
            self.turn = PIECE_DARK

    def get_valid_moves(self):
        valid_moves = {}
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.get_piece(row, col)
                if piece != 0 and piece.color == self.turn:
                    moves = self.board.get_valid_moves(piece)
                    if moves:
                        valid_moves[(row, col)] = moves
        return valid_moves

    def draw_pause_button(self):
        # Draw button background with rounded corners
        pygame.draw.rect(self.win, (0, 0, 0), self.pause_button, border_radius=20)
        
        # Draw pause icon (two white rectangles)
        bar_width = 12
        bar_height = 45
        bar_spacing = 4  # Reduced spacing between bars
        center_x = self.pause_button.centerx
        center_y = self.pause_button.centery
        
        # Left bar with rounded corners
        left_bar = pygame.Rect(
            center_x - bar_spacing - bar_width,
            center_y - bar_height // 2,
            bar_width,
            bar_height
        )
        # Right bar with rounded corners
        right_bar = pygame.Rect(
            center_x + bar_spacing,
            center_y - bar_height // 2,
            bar_width,
            bar_height
        )
        
        # Draw the bars with rounded corners
        pygame.draw.rect(self.win, self.pause_icon_color, left_bar, border_radius=6)
        pygame.draw.rect(self.win, self.pause_icon_color, right_bar, border_radius=6)

    def is_pause_button_clicked(self, pos):
        return self.pause_button.collidepoint(pos)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if not self.is_paused:
            # Reset the last_time when unpausing to prevent time jump
            self.last_time = time.time()

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

class Board:
    def __init__(self, game):
        self.game = game  # Set the Game instance directly during initialization
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
        # Calculate offsets for centering
        self.board_offset_x = (WIDTH - (COLS * SQUARE_SIZE)) // 2
        self.board_offset_y = (HEIGHT - (ROWS * SQUARE_SIZE)) // 2
        # Load wooden background
        self.wood_bg = pygame.image.load("assets/wood.jpeg")
        self.wood_bg = pygame.transform.scale(self.wood_bg, (COLS * SQUARE_SIZE, ROWS * SQUARE_SIZE))
        # Initialize font for turn indicator
        self.font = pygame.font.Font("assets/ps2p.ttf", 36)
    
    def draw_turn_indicator(self, win, turn, black_time, white_time):
        # Create text for turn
        turn_text = "WHITE'S TURN" if turn == PIECE_LIGHT else "BLACK'S TURN"
        text_surface = self.font.render(turn_text, True, (255, 0, 0))  # Red color
        
        # Calculate position (centered above the board)
        text_rect = text_surface.get_rect(centerx=self.board_offset_x + (COLS * SQUARE_SIZE) // 2,
                                        top=self.board_offset_y - 50)
        
        # Draw text with a subtle shadow for better visibility
        shadow_surface = self.font.render(turn_text, True, (0, 0, 0))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        win.blit(shadow_surface, shadow_rect)
        win.blit(text_surface, text_rect)

        # Draw timers
        timer_font = pygame.font.Font("assets/ps2p.ttf", 28)
        
        # Black timer (extreme left)
        black_time_text = f"BLACK: {self.format_time(black_time)}"
        black_surface = timer_font.render(black_time_text, True, (0, 0, 0))
        black_rect = black_surface.get_rect(
            left=20,  # 20px from left edge
            top=self.board_offset_y + (ROWS * SQUARE_SIZE) + 20  # 20px below the board
        )
        win.blit(black_surface, black_rect)
        
        # White timer (extreme right)
        white_time_text = f"WHITE: {self.format_time(white_time)}"
        white_surface = timer_font.render(white_time_text, True, (255, 255, 255))
        white_rect = white_surface.get_rect(
            right=WIDTH - 20,  # 20px from right edge
            top=self.board_offset_y + (ROWS * SQUARE_SIZE) + 20  # 20px below the board
        )
        win.blit(white_surface, white_rect)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def draw_squares(self, win):
        # Fill background with grey
        win.fill(GREY)
        # Draw wooden background
        win.blit(self.wood_bg, (self.board_offset_x, self.board_offset_y))
        # Draw the squares with transparency
        for row in range(ROWS):
            for col in range(COLS):
                color = BOARD_DARK if (row + col) % 2 == 0 else BOARD_LIGHT
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(s, (*color, 180), (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                win.blit(s, (col * SQUARE_SIZE + self.board_offset_x, 
                           row * SQUARE_SIZE + self.board_offset_y))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == PIECE_LIGHT:
                self.red_kings += 1
            else:
                self.white_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, PIECE_LIGHT))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, PIECE_DARK))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
    def draw(self, win, turn, black_time, white_time):
        self.draw_squares(win)
        self.draw_turn_indicator(win, turn, black_time, white_time)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    # Draw white border if the piece is selected
                    if self.game.selected and piece == self.game.selected:
                        # Draw a rounded rectangle border around the square with padding
                        padding = 5  # Adjust padding size as needed
                        rect_x = col * SQUARE_SIZE + self.board_offset_x + padding
                        rect_y = row * SQUARE_SIZE + self.board_offset_y + padding
                        rect_width = SQUARE_SIZE - 2 * padding
                        rect_height = SQUARE_SIZE - 2 * padding
                        border_thickness = 5  # Adjust thickness as needed
                        border_radius = 15 # Adjust radius as needed for rounded corners

                        # Draw shadow
                        shadow_offset = 3 # Adjust shadow offset as needed
                        shadow_color = (50, 50, 50) # Dark grey color for shadow
                        pygame.draw.rect(win, shadow_color, (rect_x + shadow_offset, rect_y + shadow_offset, rect_width, rect_height), border_thickness, border_radius=border_radius)

                        # Draw the white border
                        pygame.draw.rect(win, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), border_thickness, border_radius=border_radius)

                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == PIECE_LIGHT:
                self.red_left -= 1
            else:
                self.white_left -= 1
    
    def winner(self):
        if self.red_left <= 0:
            return PIECE_DARK
        elif self.white_left <= 0:
            return PIECE_LIGHT
        return None
    
    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == PIECE_DARK or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == PIECE_LIGHT or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
    
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def draw_valid_moves(self, win, moves):
        board_offset_x = (WIDTH - (COLS * SQUARE_SIZE)) // 2
        board_offset_y = (HEIGHT - (ROWS * SQUARE_SIZE)) // 2
        
        t = pygame.time.get_ticks() / 1000.0  # Time in seconds
        animation_duration = 2.0 # Increased duration for a slower animation
        animation_progress = (t % animation_duration) / animation_duration # Progress from 0 to 1
        
        min_radius = 5 # Smallest radius for the circle
        max_radius = SQUARE_SIZE // 4 # Reduced max radius to make the circle smaller

        # Calculate radius using a sine wave for grow and shrink effect
        # sin(pi * progress) goes from 0 to 1 and back to 0 over progress 0 to 1
        radius_factor = math.sin(animation_progress * math.pi)
        current_radius = int(min_radius + radius_factor * (max_radius - min_radius))
        
        # Keep alpha relatively constant for a pulsing effect
        alpha = 200 # Semi-transparent blue

        for move in moves:
            row, col = move
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 + board_offset_x
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + board_offset_y
            
            # Draw the pulsing circle
            if current_radius > 0 and alpha > 0:
                circle_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                # Use a blue color with the calculated alpha
                pygame.draw.circle(circle_surface, (0, 0, 255, alpha), (current_radius, current_radius), current_radius)
                # Blit the circle surface onto the main window, centered
                win.blit(circle_surface, (center_x - current_radius, center_y - current_radius))

    def get_board_state(self):
        """
        Returns a serializable representation of the board state for network transmission
        """
        state = {
            "board_pieces": [],
            "red_left": self.red_left,
            "white_left": self.white_left,
            "red_kings": self.red_kings,
            "white_kings": self.white_kings,
            "black_score": self.game.black_score if self.game else 0,  # Fallback to 0 if game is None
            "white_score": self.game.white_score if self.game else 0   # Fallback to 0 if game is None
        }
        
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    # Store piece data in a serializable format
                    piece_data = {
                        "row": piece.row,
                        "col": piece.col,
                        "color": piece.color,
                        "king": piece.king
                    }
                    state["board_pieces"].append(piece_data)
        
        return state

    def set_board_state(self, state):
        """
        Sets the board state based on a received network state
        """
        if not state:
            return
            
        # Reset board
        for row in range(ROWS):
            for col in range(COLS):
                self.board[row][col] = 0
        
        # Set piece counts
        self.red_left = state["red_left"]
        self.white_left = state["white_left"]
        self.red_kings = state["red_kings"]
        self.white_kings = state["white_kings"]
        
        # Set scores
        if self.game:
            self.game.black_score = state.get("black_score", 0)
            self.game.white_score = state.get("white_score", 0)
        
        # Add pieces
        for piece_data in state["board_pieces"]:
            piece = Piece(piece_data["row"], piece_data["col"], piece_data["color"])
            if piece_data["king"]:
                piece.make_king()
            self.board[piece_data["row"]][piece_data["col"]] = piece