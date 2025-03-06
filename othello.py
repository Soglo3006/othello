import math
import random
from copy import deepcopy

# ================== MOTEUR DU JEU ==================

class OthelloGame:
    def __init__(self):
        self.reset_board()

    def reset_board(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 'O'
        self.board[3][4] = self.board[4][3] = 'X'
        self.current_player = 'X'
        self.directions = [(-1,-1), (-1,0), (-1,1), (0,-1), 
                         (0,1), (1,-1), (1,0), (1,1)]

    def print_board(self):
        print("  0 1 2 3 4 5 6 7")
        for i, row in enumerate(self.board):
            print(i, end=" ")
            print(" ".join(row).replace(' ', '.'))

    def is_valid_move(self, player, pos):
        if self.board[pos[0]][pos[1]] != ' ':
            return False
            
        opponent = 'O' if player == 'X' else 'X'
        
        for dx, dy in self.directions:
            x, y = pos[0] + dx, pos[1] + dy
            if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == opponent:
                while 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == opponent:
                    x += dx
                    y += dy
                if 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == player:
                    return True
        return False

    def get_valid_moves(self, player):
        return [(i,j) for i in range(8) for j in range(8) 
                if self.is_valid_move(player, (i,j))]

    def make_move(self, player, pos):
        if pos is None:
            return False
            
        x, y = pos
        if self.board[x][y] != ' ':
            return False

        opponent = 'O' if player == 'X' else 'X'
        flipped = []
        
        for dx, dy in self.directions:
            temp_flip = []
            nx, ny = x + dx, y + dy
            
            while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent:
                temp_flip.append((nx, ny))
                nx += dx
                ny += dy
                
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == player:
                flipped.extend(temp_flip)
                
        if flipped:
            self.board[x][y] = player
            for i, j in flipped:
                self.board[i][j] = player
            return True
        return False

    def is_terminal(self):
        return not self.get_valid_moves('X') and not self.get_valid_moves('O')

    def get_score(self):
        x = sum(row.count('X') for row in self.board)
        o = sum(row.count('O') for row in self.board)
        return x, o

# ================== ALGORITHMES ================== 

POSITION_WEIGHTS = [
    [500, -150, 30, 10, 10, 30, -150, 500],
    [-150, -250, 0, 0, 0, 0, -250, -150],
    [30, 0, 1, 2, 2, 1, 0, 30],
    [10, 0, 2, 16, 16, 2, 0, 10],
    [10, 0, 2, 16, 16, 2, 0, 10],
    [30, 0, 1, 2, 2, 1, 0, 30],
    [-150, -250, 0, 0, 0, 0, -250, -150],
    [500, -150, 30, 10, 10, 30, -150, 500]
]

def evaluate_board(board, player):
    # Création d'une instance temporaire pour calculer les coups valides
    temp_game = OthelloGame()
    temp_game.board = deepcopy(board)
    
    opponent = 'O' if player == 'X' else 'X'
    
    # Critère 1: Différence de pièces
    score = sum(row.count(player) for row in board) - sum(row.count(opponent) for row in board)
    
    # Critère 2: Valeur des positions
    position_score = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == player:
                position_score += POSITION_WEIGHTS[i][j]
            elif board[i][j] == opponent:
                position_score -= POSITION_WEIGHTS[i][j]
    
    # Critère 3: Mobilité
    mobility = len(temp_game.get_valid_moves(player)) - len(temp_game.get_valid_moves(opponent))
    
    return score + position_score * 0.5 + mobility * 0.2

def minimax_move(board, player, depth=6):
    game = OthelloGame()
    game.board = deepcopy(board)
    
    def max_value(depth, alpha, beta):
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)
            
        max_eval = -math.inf
        for move in game.get_valid_moves(player):
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(player, move)
            eval = min_value(depth-1, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    
    def min_value(depth, alpha, beta):
        opponent = 'O' if player == 'X' else 'X'
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)
            
        min_eval = math.inf
        for move in game.get_valid_moves(opponent):
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(opponent, move)
            eval = max_value(depth-1, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval
    
    best_move = None
    best_value = -math.inf
    for move in game.get_valid_moves(player):
        child = OthelloGame()
        child.board = deepcopy(game.board)
        child.make_move(player, move)
        value = min_value(depth-1, -math.inf, math.inf)
        if value > best_value or (value == best_value and random.random() < 0.3):
            best_value = value
            best_move = move
    return best_move


def alphabeta_move(board, player, depth=7):
    game = OthelloGame()
    game.board = deepcopy(board)
    
    def max_value(depth, alpha, beta):
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)
        
        max_eval = -math.inf
        for move in game.get_valid_moves(player):
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(player, move)
            eval = min_value(depth-1, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    
    def min_value(depth, alpha, beta):
        opponent = 'O' if player == 'X' else 'X'
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)
        
        min_eval = math.inf
        for move in game.get_valid_moves(opponent):
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(opponent, move)
            eval = max_value(depth-1, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval
    
    best_move = None
    best_value = -math.inf
    for move in game.get_valid_moves(player):
        child = OthelloGame()
        child.board = deepcopy(game.board)
        child.make_move(player, move)
        value = min_value(depth-1, -math.inf, math.inf)
        if value > best_value:
            best_value = value
            best_move = move
    
    return best_move

# ================== INTERFACE ================== 

def human_vs_ai():
    game = OthelloGame()
    algorithms = {'1': minimax_move, '2': alphabeta_move}
    
    print("Choisir l'algorithme :\n1. Minimax (6 plis)\n2. Alpha-Beta (7 plis)")
    choice = input("Votre choix (1 ou 2): ").strip()
    ai_algorithm = algorithms.get(choice, minimax_move)
    
    while not game.is_terminal():
        game.print_board()
        print("\nJoueur actuel:", game.current_player)
        
        if game.current_player == 'X':
            moves = game.get_valid_moves('X')
            if not moves:
                print("Aucun coup possible, passez le tour")
                game.current_player = 'O'
                continue
                
            print("Coups valides:", moves)
            try:
                x = int(input("Ligne (0-7): "))
                y = int(input("Colonne (0-7): "))
                if (x, y) in moves:
                    game.make_move('X', (x, y))
                    game.current_player = 'O'
                else:
                    print("Coup invalide!")
            except ValueError:
                print("Entrez des nombres valides!")
        
        else:
            print("L'IA réfléchit...")
            move = ai_algorithm(game.board, 'O')
            game.make_move('O', move)
            game.current_player = 'X'

    x, o = game.get_score()
    print("\n=== Résultat final ===")
    game.print_board()
    print(f"\nScore - X: {x} | O: {o}")
    print("Gagnant: ", 'X' if x > o else 'O' if o > x else 'Égalité')

if __name__ == "__main__":
    human_vs_ai()