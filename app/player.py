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
    pass


class SmartPlayer(Player):




    def make_move(self, board: Block) -> int:
        """Choose the best move to make on the given board, and apply it,
        mutating the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        # Determine how many moves to consider
        if self.difficulty > 5:
            moves_to_consider = 150
        else:
            moves_to_consider = self._difficulty_moves_map[self.difficulty]

        # Find the best move
        best_score = -1
        best_move = None
        best_block = None

        # Track the current score before any moves
        current_score = self.goal.score(board)

        # Try different moves to find the best one
        for _ in range(moves_to_consider):
            # Choose a random block
            block = self._choose_random_block(board)

            # Choose a random action (excluding smash)
            action_type = random.randint(0, 3)

            # Create a copy of the original state to restore later
            # For rotations, we'll need to track how many we did
            # For swaps, we'll track the swap axis

            # Apply the action
            if action_type == 0:
                # Rotate clockwise
                block.rotate(1)
                move_type = "rotate_cw"
            elif action_type == 1:
                # Rotate counter-clockwise
                block.rotate(3)
                move_type = "rotate_ccw"
            elif action_type == 2:
                # Swap horizontally
                block.swap(0)
                move_type = "swap_h"
            else:
                # Swap vertically
                block.swap(1)
                move_type = "swap_v"

            # Calculate the score after this move
            new_score = self.goal.score(board)

            # Check if this is better than the current best
            if new_score > best_score:
                best_score = new_score
                best_move = move_type
                best_block = block

            # Undo the move to restore the board
            if move_type == "rotate_cw":
                block.rotate(3)  # Rotate counter-clockwise to undo
            elif move_type == "rotate_ccw":
                block.rotate(1)  # Rotate clockwise to undo
            elif move_type == "swap_h":
                block.swap(0)  # Swap horizontally again to undo
            elif move_type == "swap_v":
                block.swap(1)  # Swap vertically again to undo

        # Apply the best move found
        if best_move is not None and best_block is not None:
            # Highlight the block we're going to modify
            best_block.highlighted = True
            self.renderer.draw(board, self.id)

            # Pause for a moment so the user can see the selected block
            pygame.time.wait(TIME_DELAY)

            # Apply the chosen best move
            if best_move == "rotate_cw":
                best_block.rotate(1)
            elif best_move == "rotate_ccw":
                best_block.rotate(3)
            elif best_move == "swap_h":
                best_block.swap(0)
            elif best_move == "swap_v":
                best_block.swap(1)

            # Un-highlight the block and redraw the board
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
