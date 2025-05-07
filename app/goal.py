"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from app.block import Block


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
        -1  if this cell has never been visited
            0  if this cell has been visited and discovered
            not to be of the target colour
            1  if this cell has been visited and discovered
            to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        row, col = pos
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
            return 0

        if visited[row][col] != -1:
            return 0

        if board[row][col] != self.colour:
            visited[row][col] = 0
            return 0

        visited[row][col] = 1

        blob_size = 1

        # Up
        blob_size += self._undiscovered_blob_size((row - 1, col), board, visited)
        # Down
        blob_size += self._undiscovered_blob_size((row + 1, col), board, visited)
        # Left
        blob_size += self._undiscovered_blob_size((row, col - 1), board, visited)
        # Right
        blob_size += self._undiscovered_blob_size((row, col + 1), board, visited)

        return blob_size

    def score(self, board: Block) -> int:
        """Devuelve la puntuación actual de este gol en el tablero dado.

           La puntuación es el tamaño de la mancha conectada más grande del color objetivo del gol.
        """

        # Flatten the board for easier blob detection
        flattened = board.flatten()
        n = len(flattened)

        # Create a parallel visited structure initialized with -1
        visited = [[-1 for _ in range(n)] for _ in range(n)]

        max_blob_size = 0

        # Check every cell in the flattened board
        for i in range(n):
            for j in range(n):
                # Only process unvisited cells
                if visited[i][j] == -1:
                    # Get the blob size starting from this cell
                    blob_size = self._undiscovered_blob_size((i, j), flattened, visited)
                    max_blob_size = max(max_blob_size, blob_size)

        return max_blob_size

    def description(self) -> str:
        """Return a description of this goal.
        """
        return f"Create the largest blob of {self.colour} cells."


class PerimeterGoal(Goal):

    def score(self, board: Block) -> int:
        flattened = board.flatten()
        n = len(flattened)
        score = 0

        # Verifica los bordes superior e inferior (incluidas las esquinas)
        for j in range(n):
            if flattened[0][j] == self.colour:
                score += 2 if j == 0 or j == n - 1 else 1
            if flattened[n - 1][j] == self.colour:
                score += 2 if j == 0 or j == n - 1 else 1

        # Verifica los bordes izquierdo y derecho (excluyendo las esquinas para evitar el conteo doble)
        for i in range(1, n - 1):
            if flattened[i][0] == self.colour:
                score += 1
            if flattened[i][n - 1] == self.colour:
                score += 1

        return score

    def description(self) -> str:
        return f"Poner la mayor cantidad de celdas {self.colour} en el borde del tablero. Las esquinas valen puntos dobles."


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })