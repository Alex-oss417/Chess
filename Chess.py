import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED_HIGHLIGHT = (130, 151, 105)
POSSIBLE_MOVE_HIGHLIGHT = (186, 202, 43)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("Segoe UI Symbol", 45)

PIECES_ICONS = {
    'W': {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'},
    'B': {'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'}
}

def create_board():
    return [
        ['BR', 'BN', 'BB', 'BQ', 'BK', 'BB', 'BN', 'BR'],
        ['BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP'],
        ['WR', 'WN', 'WB', 'WQ', 'WK', 'WB', 'WN', 'WR']
    ]

pawn_moved_status = {
    'W': [False] * 8,
    'B': [False] * 8
}

def draw_board(screen, board, selected_square, possible_moves):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            
            if selected_square == (r, c):
                color = SELECTED_HIGHLIGHT
            elif (r, c) in possible_moves:
                color = POSSIBLE_MOVE_HIGHLIGHT
                
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            piece = board[r][c]
            if piece != '--':
                color_type = piece[0]
                piece_type = piece[1]
                icon = PIECES_ICONS[color_type][piece_type]
                text_surface = FONT.render(icon, True, BLACK)
                text_rect = text_surface.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE//2, r * SQUARE_SIZE + SQUARE_SIZE//2))
                screen.blit(text_surface, text_rect)

def get_basic_moves(board, r, c):
    moves = []
    piece = board[r][c]
    if piece == '--':
        return moves
    
    color = piece[0]
    piece_type = piece[1]
    enemy_color = 'B' if color == 'W' else 'W'
    
    if piece_type == 'P':
        direction = -1 if color == 'W' else 1
        if 0 <= r + direction < 8 and board[r + direction][c] == '--':
            moves.append((r + direction, c))
            if not pawn_moved_status[color][c]:
                if 0 <= r + direction * 2 < 8 and board[r + direction * 2][c] == '--':
                    moves.append((r + direction * 2, c))
        for dc in [-1, 1]:
            if 0 <= r + direction < 8 and 0 <= c + dc < 8:
                if board[r + direction][c + dc].startswith(enemy_color):
                    moves.append((r + direction, c + dc))

    elif piece_type == 'N':
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == '--' or board[nr][nc].startswith(enemy_color):
                    moves.append((nr, nc))

    elif piece_type in ['B', 'R', 'Q']:
        directions = []
        if piece_type in ['B', 'Q']: directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece_type in ['R', 'Q']: directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == '--':
                    moves.append((nr, nc))
                elif board[nr][nc].startswith(enemy_color):
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc

    elif piece_type == 'K':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board[nr][nc] == '--' or board[nr][nc].startswith(enemy_color):
                        moves.append((nr, nc))
                        
    return moves

def show_promotion_menu(screen, color):
    menu_active = True
    options = ['Q', 'R', 'B', 'N']
    while menu_active:
        screen.fill((50, 50, 50))
        title = pygame.font.SysFont("Arial", 24).render("Выберите фигуру для превращения:", True, WHITE)
        screen.blit(title, (50, 150))
        
        rects = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(50 + i * 120, 250, 100, 100)
            rects.append((rect, opt))
            pygame.draw.rect(screen, LIGHT_SQUARE, rect)
            icon = PIECES_ICONS[color][opt]
            text = FONT.render(icon, True, BLACK)
            screen.blit(text, text.get_rect(center=rect.center))
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, opt in rects:
                    if rect.collidepoint(pos):
                        return opt

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Модифицированные шахматы")
    clock = pygame.time.Clock()
    
    board = create_board()
    turn = 'W'
    selected_square = None
    possible_moves = []
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                c = pos[0] // SQUARE_SIZE
                r = pos[1] // SQUARE_SIZE
                
                if board[r][c].startswith(turn):
                    selected_square = (r, c)
                    possible_moves = get_basic_moves(board, r, c)
                elif selected_square and (r, c) in possible_moves:
                    orig_r, orig_c = selected_square
                    piece = board[orig_r][orig_c]
                    
                    if piece[1] == 'P':
                        pawn_moved_status[turn][orig_c] = True
                    
                    board[r][c] = piece
                    board[orig_r][orig_c] = '--'
                    
                    target_row = 0 if turn == 'W' else 7
                    if r == target_row and piece[1] != 'K':
                        chosen_piece = show_promotion_menu(screen, turn)
                        board[r][c] = turn + chosen_piece
                    
                    selected_square = None
                    possible_moves = []
                    turn = 'B' if turn == 'W' else 'W'
                else:
                    selected_square = None
                    possible_moves = []
                    
        draw_board(screen, board, selected_square, possible_moves)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
