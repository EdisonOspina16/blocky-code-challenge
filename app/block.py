"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Block class, the main data structure used in the game.
"""
from typing import Optional, Tuple, List
import random
from app.renderer import COLOUR_LIST, TEMPTING_TURQUOISE, BLACK, colour_name


HIGHLIGHT_COLOUR = TEMPTING_TURQUOISE
FRAME_COLOUR = BLACK


class Block:
    """A square block in the Blocky game.

    === Public Attributes ===
    position:
        The (x, y) coordinates of the upper left corner of this Block.
        Note that (0, 0) is the top left corner of the window.
    size:
        The height and width of this Block.  Since all blocks are square,
        we needn't represent height and width separately.
    colour:
        If this block is not subdivided, <colour> stores its colour.
        Otherwise, <colour> is None and this block's sublocks store their
        individual colours.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero.  If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    highlighted:
        True iff the user has selected this block for action.
    children:
        The blocks into which this block is subdivided.  The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.
    parent:
        The block that this block is directly within.

    === Representation Invariations ===
    - len(children) == 0 or len(children) == 4
    - If this Block has children,
        - their max_depth is the same as that of this Block,
        - their size is half that of this Block,
        - their level is one greater than that of this Block,
        - their position is determined by the position and size of this Block,
          as defined in the Assignment 2 handout, and
        - this Block's colour is None
    - If this Block has no children,
        - its colour is not None
    - level <= max_depth
    """
    position: Tuple[int, int]
    size: int
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    highlighted: bool
    children: List['Block']
    parent: Optional['Block']

    def __init__(self, level: int,
                 colour: Optional[Tuple[int, int, int]] = None,
                 children: Optional[List['Block']] = None) -> None:
        
        self.position = (0,0)
        self.size = 0
        self.level = level
        self.max_depth = 0
        self.highlighted = False
        self.parent = None

        if children is not None:
            self.children = children
            self.colour = None
            for child in self.children:
                child. parent = self
                child.level = level + 1
                child.max_depth = self.max_depth

        else:
            self.children = []
            self.colour = colour


    def rectangles_to_draw(self) -> List[Tuple[Tuple[int, int, int],
                                        Tuple[int, int],
                                        Tuple[int, int],
                                        int]]:
        """
        Return a list of tuples describing all of the rectangles to be drawn
        in order to render this Block.

        This includes (1) for every undivided Block:
            - one rectangle in the Block's colour
            - one rectangle in the FRAME_COLOUR to frame it at the same
            dimensions, but with a specified thickness of 3
        and (2) one additional rectangle to frame this Block in the
        HIGHLIGHT_COLOUR at a thickness of 5 if this block has been
        selected for action, that is, if its highlighted attribute is True.

        The rectangles are in the format required by method Renderer.draw.
        Each tuple contains:
        - the colour of the rectangle
        - the (x, y) coordinates of the top left corner of the rectangle
        - the (height, width) of the rectangle, which for our Blocky game
        will always be the same
        - an int indicating how to render this rectangle. If 0 is specified
        the rectangle will be filled with its colour. If > 0 is specified,
        the rectangle will not be filled, but instead will be outlined in
        the FRAME_COLOUR, and the value will determine the thickness of
        the outline.

        The order of the rectangles does not matter.
        """
        rectangles = []

        if not self.children:
            rectangles.append(
                (self.colour, self.position, (self.size, self.size), 0)
            )

            rectangles.append(
                (FRAME_COLOUR, self.position, (self.size, self.size), 3)
            )
        else:
            for child in self.children:
                rectangles.extend(child.rectangles_to_draw())

        if self.highlighted:
            rectangles.append(
                (HIGHLIGHT_COLOUR, self.position, (self.size, self.size), 5)
            )

        return rectangles

    def swap(self, direction: int) -> None:
        """Swap the child Blocks of this Block.

        If <direction> is 1, swap vertically.  If <direction> is 0, swap
        horizontally. If this Block has no children, do nothing.
        """
        if len(self.children) != 4:
            return

        if direction == 0:
            self.children[0], self.children[1] = self.children[1], self.children[0]
            self.children[2], self.children[3] = self.children[3], self.children[2]

        elif direction == 1:
            self.children[0], self.children[3] = self.children[3], self.children[0]
            self.children[1], self.children[2] = self.children[2], self.children[1]

        self.update_block_locations(self.position, self.size)

    def rotate(self, direction: int) -> None:
        """Rota este Bloque y todos sus descendientes.

        Si <direction> es 1, rota en sentido horario. Si <direction> es 3, rota
        en sentido antihorario. Si este Bloque no tiene hijos, no hagas nada.

        """
        if len(self.children) != 4:
            return
        if direction == 1:
            self.children = [self.children[1], self.children[2], self.children[3], self.children[0]]
        elif direction == 3:
            self.children = [self.children[3], self.children[0], self.children[1], self.children[2]]

        self.update_block_locations(self.position, self.size)


    def smash(self) -> bool:
        """Destruye este bloque.

        Si este Bloque puede ser destruido,
        genera aleatoriamente cuatro nuevos Bloques hijos para él. (Si ya tenía
        Bloques hijos, descártalos).
        Asegúrate de que se mantengan satisfechas las Invariantes de Representación (RI) de los Bloques.

        Un Bloque puede ser destruido si y solo si no es el Bloque de nivel superior y
        no está ya en el nivel de profundidad máxima.

        Devuelve True si este Bloque fue destruido y False en caso contrario.

        """
        if self.level == 0 or self.level == self.max_depth:
            return False
        self.children = [random_init(self.level + 1, self.max_depth) for _ in range(4)]
        for child in self.children:
            child.parent = self
            child.max_depth = self.max_depth
        self.colour = None
        self.update_block_locations(self.position, self.size)
        return True


    def update_block_locations(self, top_left: Tuple[int, int], size: int) -> None:
        """
        Actualice la posición y el tamaño de cada uno de los bloques dentro de este bloque.

        Asegúrese de que cada uno coincida con la posición y el tamaño de su bloque principal.

        <top_left> son las coordenadas (x, y) de la esquina superior izquierda de este bloque. <size> es la altura

        y el ancho de este bloque.
        """

        self.position = top_left
        self.size = size
        if len(self.children):
            x, y = top_left
            child_size = size // 2
            positions = [
                (x + child_size, y),
                (x, y),
                (x, y + child_size),
                (x + child_size, y + child_size)
            ]
            for i in range(4):
                self.children[i].update_block_locations(positions[i], child_size)

    def get_selected_block(self, location: Tuple[int, int], level: int) -> "Block":
        """
        Actualiza la posición (esquina superior izquierda) y el tamaño del bloque actual.
        Si el bloque tiene hijos, divide su área en cuatro sub-bloques iguales y calcula la posición y tamaño de cada uno a partir de las coordenadas del bloque padre.
        Esto garantiza que todos los sub-bloques estén correctamente ubicados dentro de su bloque padre, manteniendo la estructura jerárquica del tablero.
        """
        x, y = location

        if not (self.position[0] <= x < self.position[0] + self.size and
                self.position[1] <= y < self.position[1] + self.size):
            return self

        if self.level == level or not self.children:
            return self

        for child in self.children:
            if (child.position[0] <= x < child.position[0] + child.size and
                    child.position[1] <= y < child.position[1] + child.size):
                return child.get_selected_block(location, level)

        return self


    def flatten(self) -> List[List[Tuple[int, int, int]]]:
        """Devuelve una lista bidimensional que representa este Bloque como filas
        y columnas de celdas unitarias.

        Devuelve una lista de listas L, donde,
        para 0 <= i, j < 2^{max_depth - self.level}
            - L[i] representa la columna i y
            - L[i][j] representa la celda unitaria en la columna i y fila j.
        Cada celda unitaria está representada por 3 enteros que indican el color
        del bloque en la ubicación de la celda [i][j].

        L[0][0] representa la celda unitaria en la esquina superior izquierda del Bloque.
        """
        size = int(2 ** (self.max_depth - self.level))

        # Si el bloque es una hoja (sin hijos), retorna una matriz de su color
        if not self.children:
            return [[self.colour for _ in range(size)] for _ in range(size)]

        child_size = size // 2

        # Obtenemos los cuadrantes
        superior_izquierdo = self.children[1].flatten()
        superior_derecho = self.children[2].flatten()
        inferior_izquierdo = self.children[0].flatten()
        inferior_derecho = self.children[3].flatten()

        # Verificamos que todos los cuadrantes tienen el tamaño correcto
        expected_size = child_size
        if (len(superior_izquierdo) != expected_size or
                len(superior_derecho) != expected_size or
                len(inferior_izquierdo) != expected_size or
                len(inferior_derecho) != expected_size):
            # Si algún cuadrante no tiene el tamaño esperado, creamos una matriz en negro como fallback
            return [[(0, 0, 0) for _ in range(size)] for _ in range(size)]

        # Combinamos los cuadrantes
        resultado = []


        for i in range(child_size):
            fila_superior = []
            fila_superior.extend(superior_izquierdo[i])
            fila_superior.extend(superior_derecho[i])
            resultado.append(fila_superior)


        for i in range(child_size):
            fila_inferior = []
            fila_inferior.extend(inferior_izquierdo[i])
            fila_inferior.extend(inferior_derecho[i])
            resultado.append(fila_inferior)

        return resultado


def random_init(level: int, max_depth: int) -> 'Block':
    """Devuelve un Bloque generado aleatoriamente con nivel <level> y subdividido
    hasta una profundidad máxima de <max_depth>.

    En todo el Bloque generado, asigna valores apropiados para todos los atributos,
    excepto la posición y el tamaño. Estos pueden ser establecidos por el cliente
    utilizando el método update_block_locations.

    Precondición:
        level <= max_depth
    """
    # Caso base
    if level == max_depth:
        b = Block(level, random.choice(COLOUR_LIST))
        b.max_depth = max_depth
        return b

    # Decide si crear un bloque padre o un bloque hoja
    # Crea bloques hijos solo si no hemos alcanzado la profundidad máxima de 1
    if level < max_depth and random.random() < 0.7:
        # Crear un bloque padre con 4 hijos
        children = [random_init(level + 1, max_depth) for _ in range(4)]
        b = Block(level, children=children)
        for child in b.children:
            child.parent = b
    else:
        b = Block(level, random.choice(COLOUR_LIST))

    b.max_depth = max_depth
    return b


def attributes_str(b: Block, verbose) -> str:
    """Return a str that is a concise representation of the attributes of <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Note: These are attributes that every Block has.
    """
    answer = f'pos={b.position}, size={b.size}, level={b.level}, '
    if verbose:
        answer += f'highlighted={b.highlighted}, max_depth={b.max_depth}'
    return answer


def print_block(b: Block, verbose=False) -> None:
    """Print a text representation of Block <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    print_block_indented(b, 0, verbose)


def print_block_indented(b: Block, indent: int, verbose) -> None:
    """Print a text representation of Block <b>, indented <indent> steps.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    if len(b.children) == 0:
        # b a leaf.  Print its colour and other attributes
        print(f'{"  " * indent}{colour_name(b.colour)}: ' +
              f'{attributes_str(b, verbose)}')
    else:
        # b is not a leaf, so it doesn't have a colour.  Print its
        # other attributes.  Then print its children.
        print(f'{"  " * indent}{attributes_str(b, verbose)}')
        for child in b.children:
            print_block_indented(child, indent + 1, verbose)

if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['print_block_indented'],
    #     'allowed-import-modules': [
    #         'doctest', 'python_ta', 'random', 'typing',
    #         'block', 'goal', 'player', 'renderer', 'math'
    #     ],
    #     'max-attributes': 15
    # })

    # This tiny tree with one node will have no children, highlighted False,
    # and will have the provided values for level and colour; the initializer
    # sets all else (position, size, and max_depth) to 0.
    b0 = Block(0, COLOUR_LIST[2])
    # Now we update position and size throughout the tree.
    b0.update_block_locations((0, 0), 750)
    print("=== tiny tree ===")
    # We have not set max_depth to anything meaningful, so it still has the
    # value given by the initializer (0 and False).
    print_block(b0, True)

    b1 = Block(0, children=[
        Block(1, children=[
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, COLOUR_LIST[2]),
        Block(1, children=[
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, children=[
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[1])
        ])
    ])
    b1.update_block_locations((0, 0), 750)
    print("\n=== handmade tree ===")
    # Similarly, max_depth is still 0 in this tree.  This violates the
    # representation invariants of the class, so we shouldn't use such a
    # tree in our real code, but we can use it to see what print_block
    # does with a slightly bigger tree.
    print_block(b1, True)

    # Now let's make a random tree.
    # random_init has the job of setting all attributes except position and
    # size, so this time max_depth is set throughout the tree to the provided
    # value (3 in this case).
    b2 = random_init(0, 3)
    # Now we update position and size throughout the tree.
    # b2.update_block_locations((0, 0), 750)
    print("\n=== random tree ===")
    # All attributes should have sensible values when we print this tree.
    print_block(b2, True)