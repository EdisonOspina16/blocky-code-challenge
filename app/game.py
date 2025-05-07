"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Game class, which is the main class for the
Blocky game.

At the bottom of the file, there are some function that you
can call to try playing the game in several different configurations.
"""
import random
from typing import List
from app.block import Block, random_init
from app.goal import BlobGoal, PerimeterGoal
from app.player import Player, HumanPlayer, RandomPlayer, SmartPlayer
from app.renderer import Renderer, COLOUR_LIST, colour_name, BOARD_WIDTH


class Game:
    """A game of Blocky.

    === Public Attributes ===
    board:
        The Blocky board on which this game will be played.
    renderer:
        The object that is capable of drawing our Blocky board on the screen,
        and tracking user interactions with the Blocky board.
    players:
        The entities that are playing this game.

    === Representation Invariants ===
    - len(players) >= 1
    """
    board: Block
    renderer: Renderer
    players: List[Player]

    def __init__(self, max_depth: int,
                 num_human: int,
                 random_players: int,
                 smart_players: List[int]) -> None:
        """Inicialice este juego, como se describe en la tarea 2.

            Condición previa:
            2 <= profundidad máxima <= 5
        """

        self.players = []

        # Calcular el número total de jugadores
        total_players = num_human + random_players + len(smart_players)

        # Crear el renderer primero ya que los jugadores lo necesitan
        self.renderer = Renderer(total_players)

        # Inicializar el tablero aleatorio y establecer posiciones/tamaños
        self.board = random_init(0, max_depth)
        self.board.update_block_locations((0, 0), BOARD_WIDTH)

        # Crear los jugadores humanos
        for i in range(num_human):
            # Elegir un color objetivo aleatorio para este jugador
            target_colour = random.choice(COLOUR_LIST)

            # Crear un objetivo aleatorio (Blob o Perimeter)
            if random.random() < 0.5:
                goal = BlobGoal(target_colour)
            else:
                goal = PerimeterGoal(target_colour)

            # Crear y añadir el jugador humano
            player = HumanPlayer(self.renderer, i, goal)
            self.players.append(player)

        # Crear los jugadores aleatorios
        for i in range(random_players):
            # Elegir un color objetivo aleatorio para este jugador
            target_colour = random.choice(COLOUR_LIST)

            # Crear un objetivo aleatorio (Blob o Perimeter)
            if random.random() < 0.5:
                goal = BlobGoal(target_colour)
            else:
                goal = PerimeterGoal(target_colour)

            # Crear y añadir el jugador aleatorio
            player = RandomPlayer(self.renderer, i + num_human, goal)
            self.players.append(player)

        # Crear los jugadores inteligentes
        for idx, difficulty in enumerate(smart_players):
            # Elegir un color objetivo aleatorio para este jugador
            target_colour = random.choice(COLOUR_LIST)

            # Crear un objetivo aleatorio (Blob o Perimeter)
            if random.random() < 0.5:
                goal = BlobGoal(target_colour)
            else:
                goal = PerimeterGoal(target_colour)

            # Crear y añadir el jugador inteligente con su nivel de dificultad
            player_id = num_human + random_players + idx
            player = SmartPlayer(self.renderer, player_id, goal, difficulty)
            self.players.append(player)

        # Dibujar el tablero inicial
        if self.players:  # Verificar que haya al menos un jugador
            self.renderer.draw(self.board, 0)


    def run_game(self, num_turns: int) -> None:
        """Run the game for the number of turns specified.

        Each player gets <num_turns> turns. The first player in self.players
        goes first.  Before each move, print to the console whose turn it is
        and what the turn number is.  After each move, print the current score
        of the player who just moved.

        Report player numbers and turn numbers using 1-based counting.
        For example, refer to the self.players[0] as 'Player 1'.

        When the game is over, print who won to the console.

        """
        # Index within self.players of the current player.
        index = 0
        for turn in range(num_turns * len(self.players)):
            player = self.players[index]
            print(f'Player {player.id +1}, turn {turn + 1}')
            if self.players[index].make_move(self.board) == 1:
                break
            else:
                print(f'Player {player.id + 1} CURRENT SCORE: ' +
                      f'{player.goal.score(self.board)}')
                index = (index + 1) % len(self.players)

        # Determine and report the winner.
        max_score = 0
        winning_player = 0
        for i in range(len(self.players)):
            score = self.players[i].goal.score(self.board)
            print(f'Player {i + 1} : {score}')
            if score > max_score:
                max_score = score
                winning_player = i
        print(f'WINNER is Player {winning_player + 1}!')
        print('Players had these goals:')
        for player in self.players:
            print(f'Player {player.id + 1} ' +
                  f'goal = \n\t{player.goal.description()}: ' +
                  f'{colour_name(player.goal.colour)}')


def auto_game() -> None:
    """Run a game with two computer players of different difficulty.
    """
    random.seed(1001)
    game = Game(4, 0, 0, [1, 6])
    game.run_game(10)


def two_player_game() -> None:
    """Run a game with two human players.
    """
    random.seed(507)
    game = Game(3, 2, 0, [])
    game.run_game(5)


def solitaire_game() -> None:
    """Run a game with one human player.
    """
    random.seed(507)
    game = Game(4, 1, 0, [])
    game.run_game(30)


def sample_game() -> None:
    """Run a sample game with one human player, one random player,
    and one smart player.
    """
    # random.seed(1001)
    game = Game(5, 1, 1, [6])
    game.run_game(3)


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['run_game'],
    #     'allowed-import-modules': [
    #         'doctest', 'python_ta', 'random', 'typing',
    #         'block', 'goal', 'player', 'renderer'
    #     ],
    # })
    # sample_game()
    # auto_game()
    # two_player_game()
    solitaire_game()