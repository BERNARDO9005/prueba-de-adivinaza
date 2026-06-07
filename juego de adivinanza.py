import json
import random
import os
from datetime import datetime
from abc import ABC, abstractmethod

# ========================== CLASE PARA MANEJO DE PUNTAJES ==========================
class HighScoreManager:
    """Gestiona la persistencia de puntajes máximos usando archivos JSON."""
    
    def __init__(self, filename):
        self._filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Crea el archivo si no existe."""
        if not os.path.exists(self._filename):
            with open(self._filename, 'w') as f:
                json.dump([], f)
    
    def load_scores(self):
        """Carga la lista de puntajes desde el archivo."""
        try:
            with open(self._filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_scores(self, scores):
        """Guarda la lista de puntajes en el archivo."""
        with open(self._filename, 'w') as f:
            json.dump(scores, f, indent=4)
    
    def add_score(self, player_name, score, extra=None):
        """
        Agrega un nuevo puntaje.
        score: número de intentos (menor es mejor) o cantidad de victorias (mayor es mejor)
        extra: campo adicional opcional (ej. fecha)
        """
        scores = self.load_scores()
        entry = {
            "player": player_name,
            "score": score,
            "date": extra or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        scores.append(entry)
        self.save_scores(scores)
    
    def get_top_scores(self, ascending=True, limit=10):
        """
        Retorna los top 'limit' puntajes ordenados.
        ascending=True -> menor score es mejor (Adivina el Número)
        ascending=False -> mayor score es mejor (Tres en Raya)
        """
        scores = self.load_scores()
        if ascending:
            scores.sort(key=lambda x: x['score'])
        else:
            scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:limit]


# ========================== CLASE BASE ABSTRACTA ==========================
class Game(ABC):
    """Clase base abstracta para todos los juegos."""
    
    @abstractmethod
    def play(self):
        """Método principal que ejecuta el juego."""
        pass
    
    @abstractmethod
    def get_name(self):
        """Retorna el nombre del juego."""
        pass


# ========================== JUEGO 1: ADIVINA EL NÚMERO ==========================
class GuessNumberGame(Game):
    """
    Juego de adivinanza con rango configurable.
    Guarda el récord de pocos intentos en JSON.
    """
    
    def __init__(self, start=1, end=100, max_attempts=10):
        self._start = start
        self._end = end
        self._max_attempts = max_attempts
        self._secret = None
        self._attempts = 0
        self._score_manager = HighScoreManager("guess_number_scores.json")
    
    def _generate_secret(self):
        """Genera el número secreto aleatoriamente."""
        self._secret = random.randint(self._start, self._end)
    
    def _get_valid_int(self, prompt):
        """Solicita un entero al usuario con manejo de excepciones."""
        while True:
            try:
                value = int(input(prompt))
                return value
            except ValueError:
                print("❌ Error: Debes ingresar un número entero válido.")
    
    def play(self):
        """Ejecuta la partida de adivinanza."""
        print(f"\n🎯 ADIVINA EL NÚMERO (entre {self._start} y {self._end})")
        print(f"Tienes {self._max_attempts} intentos. ¡Menos intentos = mejor puntaje!")
        self._generate_secret()
        self._attempts = 0
        guessed = False
        
        while self._attempts < self._max_attempts and not guessed:
            remaining = self._max_attempts - self._attempts
            guess = self._get_valid_int(f"Intento {self._attempts+1} (restan {remaining}): ")
            self._attempts += 1
            
            if guess < self._secret:
                print("📈 El número es MAYOR.")
            elif guess > self._secret:
                print("📉 El número es MENOR.")
            else:
                print(f"🎉 ¡Correcto! Lo lograste en {self._attempts} intentos.")
                guessed = True
        
        if not guessed:
            print(f"💀 Agotaste tus intentos. El número era {self._secret}.")
            self._attempts = None  # No registra puntaje
        
        # Registrar puntaje si adivinó
        if guessed and self._attempts is not None:
            player = input("Ingresa tu nombre para el récord: ").strip()
            if player:
                self._score_manager.add_score(player, self._attempts)
                print("🏆 Puntaje guardado.")
        
        # Mostrar tabla de récords
        self._show_high_scores()
    
    def _show_high_scores(self):
        """Muestra los mejores puntajes (menor número de intentos)."""
        top = self._score_manager.get_top_scores(ascending=True, limit=5)
        if not top:
            print("📭 Aún no hay récords. ¡Sé el primero!")
            return
        print("\n🏅 TOP 5 - MÍNIMOS INTENTOS:")
        for i, entry in enumerate(top, 1):
            print(f"{i}. {entry['player']} - {entry['score']} intentos ({entry['date']})")
    
    def get_name(self):
        return "Adivina el Número"


# ========================== JUEGO 2: TRES EN RAYA CON IA ==========================
class TicTacToeAI:
    """IA simple para Tres en Raya: intenta ganar, bloquear o elige al azar."""
    
    def get_move(self, board, player_symbol, opponent_symbol):
        """
        board: lista de 9 elementos (0..8), con 'X', 'O' o espacio ' '.
        Retorna el índice (0-8) donde la IA desea jugar.
        """
        # 1. Intentar ganar
        for i in range(9):
            if board[i] == ' ':
                board[i] = player_symbol
                if self._check_win(board, player_symbol):
                    board[i] = ' '
                    return i
                board[i] = ' '
        # 2. Bloquear al oponente
        for i in range(9):
            if board[i] == ' ':
                board[i] = opponent_symbol
                if self._check_win(board, opponent_symbol):
                    board[i] = ' '
                    return i
                board[i] = ' '
        # 3. Elegir centro, esquinas o aleatorio (heurística simple)
        preferencias = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        for i in preferencias:
            if board[i] == ' ':
                return i
        return None  # no debería pasar
    
    def _check_win(self, board, symbol):
        """Verifica si el símbolo dado tiene 3 en línea."""
        lineas = [(0,1,2), (3,4,5), (6,7,8),
                  (0,3,6), (1,4,7), (2,5,8),
                  (0,4,8), (2,4,6)]
        return any(board[a] == board[b] == board[c] == symbol for a,b,c in lineas)


class TicTacToeGame(Game):
    """Juego Tres en Raya contra IA, con registro de victorias totales del jugador."""
    
    def __init__(self):
        self._board = [' '] * 9
        self._player_symbol = 'X'
        self._ai_symbol = 'O'
        self._ai = TicTacToeAI()
        self._score_manager = HighScoreManager("tictactoe_wins.json")
    
    def _print_board(self):
        """Muestra el tablero en consola."""
        print("\n   " + " | ".join(self._board[0:3]))
        print("  ---------")
        print("   " + " | ".join(self._board[3:6]))
        print("  ---------")
        print("   " + " | ".join(self._board[6:9]) + "\n")
    
    def _is_full(self):
        return all(cell != ' ' for cell in self._board)
    
    def _check_win(self, symbol):
        lineas = [(0,1,2), (3,4,5), (6,7,8),
                  (0,3,6), (1,4,7), (2,5,8),
                  (0,4,8), (2,4,6)]
        return any(self._board[a] == self._board[b] == self._board[c] == symbol for a,b,c in lineas)
    
    def _get_player_move(self):
        """Solicita movimiento al jugador con validación de excepciones."""
        while True:
            try:
                pos = input("Elige una posición (1-9): ")
                if not pos.isdigit():
                    raise ValueError("Debe ser un número.")
                idx = int(pos) - 1
                if idx < 0 or idx > 8:
                    raise ValueError("Posición fuera de rango.")
                if self._board[idx] != ' ':
                    raise ValueError("Casilla ocupada.")
                return idx
            except ValueError as e:
                print(f"❌ Error: {e}")
    
    def _update_leaderboard(self, player_name):
        """Actualiza el líder de victorias totales del jugador."""
        # Cargar datos existentes: formato [{"player": nombre, "wins": número}]
        try:
            with open("tictactoe_wins.json", 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        
        found = False
        for entry in data:
            if entry.get("player") == player_name:
                entry["wins"] = entry.get("wins", 0) + 1
                found = True
                break
        if not found:
            data.append({"player": player_name, "wins": 1})
        
        with open("tictactoe_wins.json", 'w') as f:
            json.dump(data, f, indent=4)
    
    def _show_leaderboard(self):
        """Muestra el ranking de victorias."""
        try:
            with open("tictactoe_wins.json", 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        if not data:
            print("📭 Aún no hay victorias registradas.")
            return
        data.sort(key=lambda x: x['wins'], reverse=True)
        print("\n🏆 RANKING DE VICTORIAS (histórico):")
        for i, entry in enumerate(data[:5], 1):
            print(f"{i}. {entry['player']} - {entry['wins']} victorias")
    
    def play(self):
        """Ejecuta una partida completa de Tres en Raya (múltiples rondas)."""
        print("\n🎮 TRES EN RAYA VS IA")
        print("Tú eres X, la IA es O. Gana 3 partidas para registrar tu victoria total.")
        player_wins = 0
        ai_wins = 0
        rounds_played = 0
        
        while player_wins < 3 and ai_wins < 3:
            rounds_played += 1
            print(f"\n--- Ronda {rounds_played} --- (Victorias: Tú {player_wins} - IA {ai_wins})")
            self._board = [' '] * 9
            turn = 'player'  # El jugador comienza siempre
            game_over = False
            
            while not game_over:
                self._print_board()
                if turn == 'player':
                    move = self._get_player_move()
                    self._board[move] = self._player_symbol
                    if self._check_win(self._player_symbol):
                        self._print_board()
                        print("🎉 ¡Ganaste esta ronda!")
                        player_wins += 1
                        game_over = True
                    elif self._is_full():
                        self._print_board()
                        print("🤝 Empate en esta ronda.")
                        game_over = True
                    else:
                        turn = 'ai'
                else:  # turno IA
                    print("Pensando movimiento de la IA...")
                    move = self._ai.get_move(self._board, self._ai_symbol, self._player_symbol)
                    if move is not None:
                        self._board[move] = self._ai_symbol
                        if self._check_win(self._ai_symbol):
                            self._print_board()
                            print("😵 La IA ganó esta ronda.")
                            ai_wins += 1
                            game_over = True
                        elif self._is_full():
                            self._print_board()
                            print("🤝 Empate en esta ronda.")
                            game_over = True
                        else:
                            turn = 'player'
                    else:
                        # Tablero lleno pero no detectado (seguridad)
                        game_over = True
        
        # Al finalizar las 3 victorias necesarias
        if player_wins >= 3:
            print("\n🏆 ¡HAS GANADO EL MATCH! 🏆")
            player_name = input("Ingresa tu nombre para registrar la victoria: ").strip()
            if player_name:
                self._update_leaderboard(player_name)
                print("✅ Victoria registrada en el líder histórico.")
        else:
            print("\n💀 La IA ganó el match. ¡Sigue practicando!")
        
        self._show_leaderboard()
    
    def get_name(self):
        return "Tres en Raya"


# ========================== MENÚ PRINCIPAL ==========================
def main():
    games = [
        GuessNumberGame(),
        TicTacToeGame()
    ]
    
    while True:
        print("\n" + "="*50)
        print("   SUITE DE MINIJUEGOS - POO Edition")
        print("="*50)
        for idx, game in enumerate(games, 1):
            print(f"{idx}. {game.get_name()}")
        print("0. Salir")
        
        try:
            option = int(input("\nSelecciona un juego: "))
            if option == 0:
                print("¡Hasta luego!")
                break
            if 1 <= option <= len(games):
                games[option-1].play()
            else:
                print("Opción inválida.")
        except ValueError:
            print("Por favor ingresa un número válido.")


if __name__ == "__main__":
    main()






