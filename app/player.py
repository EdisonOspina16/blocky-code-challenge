"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from app.renderer import Renderer
from app.block import Block
from app.goal import Goal

TIME_DELAY = 600


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)

        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level

        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.parent is not None:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash():
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0


class RandomPlayer(Player):
    """A computer player that moves randomly.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """

    def make_move(self, board: Block) -> int:
        """Choose a random move to make on the given board, and apply it, 
        mutating the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        random_block = self._choose_random_block(board)

        random_block.highlighted = True
        self.renderer.draw(board, self.id)

        pygame.time.wait(TIME_DELAY)

        action_type = random.randint(0, 4)

        if action_type == 0:
            random_block.rotate(1)
        elif action_type == 1:
            random_block.rotate(3)
        elif action_type == 2:
            random_block.swap(0)
        elif action_type == 3:
            random_block.swap(1)
        else:
            random_block.smash()

        random_block.highlighted = False
        self.renderer.draw(board, self.id)

        return 0

    def _choose_random_block(self, board: Block) -> Block:
        """Choose a random block on the board."""
        max_depth = board.max_depth
        
        depth = random.randint(0, max_depth - 1)
        
        curr_block = board
        curr_depth = 0
        
        while curr_depth < depth and len(curr_block.children) > 0:
            curr_block = random.choice(curr_block.children)
            curr_depth += 1
            
        return curr_block


class SmartPlayer(Player):
    """A computer player that chooses intelligent moves.

       A SmartPlayer looks ahead to determine the best move based on their goal.
       The difficulty level determines how many moves it evaluates.
       A SmartPlayer cannot perform smash moves.

       === Public Attributes ===
       renderer:
           The object that draws our Blocky board on the screen
           and tracks user interactions with the Blocky board.
       id:
           This player's number.  Used by the renderer to refer to the player,
           for example as "Player 2"
       goal:
           This player's assigned goal for the game.
       difficulty:
           How many moves this player considers before choosing one.
       """

    # === Private Attributes ===
    # _difficulty_moves_map:
    #     A dictionary mapping difficulty levels to number of moves to consider
    _difficulty_moves_map: dict[int, int]
    difficulty: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal,
               difficulty: int) -> None:
        """Initialize this SmartPlayer with the given <renderer>, <player_id>,
        <goal>, and <difficulty>.
        """
        super().__init__(renderer, player_id, goal)
        self.difficulty = difficulty

        # Initialize the difficulty to moves map
        self._difficulty_moves_map = {
            0: 5,
            1: 10,
            2: 25,
            3: 50,
            4: 100,
            5: 150
        }

    def make_move(self, board: Block) -> int:
        """Choose the best move to make on the given board, and apply it,
        mutating the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """

        if self.difficulty > 5:
            moves_to_consider = 150
        else:
            moves_to_consider = self._difficulty_moves_map[self.difficulty]

        best_score = -1
        best_move = None
        best_block = None

        current_score = self.goal.score(board)

        for _ in range(moves_to_consider):
            block = self._choose_random_block(board)

            action_type = random.randint(0, 3)

            if action_type == 0:
                block.rotate(1)
                move_type = "rotate_cw"
            elif action_type == 1:
                block.rotate(3)
                move_type = "rotate_ccw"
            elif action_type == 2:
                block.swap(0)
                move_type = "swap_h"
            else:
                block.swap(1)
                move_type = "swap_v"

            new_score = self.goal.score(board)

            if new_score > best_score:
                best_score = new_score
                best_move = move_type
                best_block = block

            if move_type == "rotate_cw":
                block.rotate(3)
            elif move_type == "rotate_ccw":
                block.rotate(1)
            elif move_type == "swap_h":
                block.swap(0)
            elif move_type == "swap_v":
                block.swap(1)


        if best_move is not None and best_block is not None:

            best_block.highlighted = True
            self.renderer.draw(board, self.id)

            pygame.time.wait(TIME_DELAY)

            if best_move == "rotate_cw":
                best_block.rotate(1)
            elif best_move == "rotate_ccw":
                best_block.rotate(3)
            elif best_move == "swap_h":
                best_block.swap(0)
            elif best_move == "swap_v":
                best_block.swap(1)

            best_block.highlighted = False
            self.renderer.draw(board, self.id)

        return 0

    def _choose_random_block(self, board: Block) -> Block:
        """Selecciona un bloque aleatorio en el tablero."""
        max_depth = min(board.max_depth, 3)  # Limita la profundidad máxima
        depth = random.randint(0, max_depth)

        current = board
        for _ in range(depth):
            if not current.children:  # Si es una hoja, terminar
                break
            current = random.choice(current.children)

        return current


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
