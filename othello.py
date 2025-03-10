# Alexandre Booh Louha - matricule:20220478
# Rafi Dahoui - matricule: 20228733
import math
import random
from copy import deepcopy

class OthelloGame:
    def __init__(self):
        self.reset_board()

    def reset_board(self):
        self.board = []
        for _ in range(8):
            self.board.append([' ']*8)
        self.board[3][3] = self.board[4][4] = 'O'
        self.board[3][4] = self.board[4][3] = 'X'
        self.current_player = 'X'
        self.directions = [(-1,-1), (-1,0), (-1,1), (0,-1), 
                           (0,1), (1,-1), (1,0), (1,1)]

    def print_board(self):
        print("  0 1 2 3 4 5 6 7")
        i = 0
        for row in self.board:
            print(i, end=" ")
            print(" ".join(row).replace(' ', '.'))
            i += 1


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
                flipped += temp_flip
                
        if flipped:
            self.board[x][y] = player
            for i, j in flipped:
                self.board[i][j] = player
            return True
        return False

    def is_terminal(self):
        if not self.get_valid_moves('X') and not self.get_valid_moves('O'):
            return True
        return False


    def get_score(self):
        x, o = 0, 0
        for row in self.board:
            for cell in row:
                if cell == 'X':
                    x += 1
                elif cell == 'O':
                    o += 1
        return x, o

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

#Évalue l'état du plateau en fonction du nombre de pions du joueur 
# de la position des pions et de la mobilité des coups disponibles.
def evaluate_board(board, player):
    opponent = 'O' if player == 'X' else 'X'
    score = 0
    position_score = 0
    temp_game = OthelloGame()
    temp_game.board = deepcopy(board)
    
    # Calculer le score des pièces et le score de position en une seule boucle
    for i in range(8):
        for j in range(8):
            if board[i][j] == player:
                score += 1
                position_score += POSITION_WEIGHTS[i][j]
            elif board[i][j] == opponent:
                score -= 1
                position_score -= POSITION_WEIGHTS[i][j]
    
    # Calculer la mobilité
    valid_moves_player = len(temp_game.get_valid_moves(player))
    valid_moves_opponent = len(temp_game.get_valid_moves(opponent))
    mobility = valid_moves_player - valid_moves_opponent
    
    return score + position_score * 0.5 + mobility * 0.2

# Implémente l'algorithme Minimax pour choisir 
# le meilleur coup en évaluant les états futurs du jeu.
def minimax_move(board, player, depth=6):
    game = OthelloGame()
    game.board = deepcopy(board)

    def minimax(depth, alpha, beta, is_maximizing, current_player):
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)

        best_value = -math.inf if is_maximizing else math.inf
        valid_moves = game.get_valid_moves(current_player)

        for move in valid_moves:
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(current_player, move)
            value = minimax(depth - 1, alpha, beta, not is_maximizing, 'O' if current_player == 'X' else 'X')

            if is_maximizing:
                best_value = max(best_value, value)
                alpha = max(alpha, value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, value)

            if beta <= alpha:
                break

        return best_value

    best_move = None
    best_value = -math.inf
    for move in game.get_valid_moves(player):
        child = OthelloGame()
        child.board = deepcopy(game.board)
        child.make_move(player, move)
        value = minimax(depth - 1, -math.inf, math.inf, False, 'O' if player == 'X' else 'X')

        if value > best_value or (value == best_value and random.random() < 0.3):
            best_value = value
            best_move = move

    return best_move


# Implémente l'algorithme Alpha-Bêta 
# pour réduire l'espace de recherche de Minimax.
def alphabeta_move(board, player, depth=7):
    game = OthelloGame()
    game.board = deepcopy(board)

    def alphabeta(depth, alpha, beta, is_maximizing, current_player):
        if depth == 0 or game.is_terminal():
            return evaluate_board(game.board, player)

        best_value = -math.inf if is_maximizing else math.inf
        valid_moves = game.get_valid_moves(current_player)

        for move in valid_moves:
            child = OthelloGame()
            child.board = deepcopy(game.board)
            child.make_move(current_player, move)

            value = alphabeta(depth - 1, alpha, beta, not is_maximizing, 'O' if current_player == 'X' else 'X')

            if is_maximizing:
                best_value = max(best_value, value)
                alpha = max(alpha, value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, value)

            if beta <= alpha:
                break

        return best_value

    best_move = None
    best_value = -math.inf

    for move in game.get_valid_moves(player):
        child = OthelloGame()
        child.board = deepcopy(game.board)
        child.make_move(player, move)
        value = alphabeta(depth - 1, -math.inf, math.inf, False, 'O' if player == 'X' else 'X')

        if value > best_value:
            best_value = value
            best_move = move

    return best_move


# Utilise la simulation Monte-Carlo pour 
# choisir le meilleur coup en simulant plusieurs parties.
def monte_carlo_move(board, player, simulations=500):
    game = OthelloGame()
    game.board = deepcopy(board)
    valid_moves = game.get_valid_moves(player)
    if not valid_moves:
        return None
    
    win_counts = {move: 0 for move in valid_moves}
    
    for move in valid_moves:
        for _ in range(simulations):
            sim_game = OthelloGame()
            sim_game.board = deepcopy(board)
            sim_game.make_move(player, move)
            current_player = {'X': 'O', 'O': 'X'}.get(player)
            
            while not sim_game.is_terminal():
                random_moves = sim_game.get_valid_moves(current_player)
                if random_moves:
                    sim_game.make_move(current_player, random.choice(random_moves))
                current_player = 'X' if not current_player == 'X' else 'O'

            
            x_score, o_score = sim_game.get_score()
            if (player == 'X' and x_score > o_score) or (player == 'O' and o_score > x_score):
                win_counts[move] += 1
    
    best_move = max(win_counts, key=win_counts.get)
    return best_move



def human_vs_ai():
    game = OthelloGame()
    algorithms = {'1': minimax_move, '2': alphabeta_move, '3': monte_carlo_move}
    
    print("Choisir l'algorithme :\n1. Minimax (6 plis)\n2. Alpha-Beta (7 plis)\n3. Monte-Carlo (10 000 simulations)")
    choice = input("Votre choix (1, 2 ou 3): ").strip()
    ai_algorithm = algorithms.get(choice)
    
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
    print("\nScore - X: {x} | O: {o}")
    print("Gagnant: ", 'X' if x > o else 'O' if o > x else 'Égalité')

human_vs_ai()
