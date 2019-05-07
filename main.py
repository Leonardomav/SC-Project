# We want to study the macro behavior of this kind of world, analyzing itin the time and in the space dimensions. We
# want to know the influence of the initial density of wood sticks and of ants. Also, we intent to clarify the
# importance of the type of neighborhood considered (i.e., Moore, Von Neumann or other). Suppose that you introduce a
# limit for the capacity of each cell to keep the wood sticks. What is the result? Suppose that we may


# TODO
# Moore neighborhood
# Time contabilization
# Frequency of ant per pixel


import simcx
import random
import numpy as np
import pyglet

MAX_PILE = 5
MIN_STICK = 1
MAX_STICK = 2


class Place:
    def __init__(self, x, y, occupant):
        self.x = x
        self.y = y
        self.occupant = occupant
        self.neighbour = [None] * 4

    def set_up(self, place):
        self.neighbour[0] = place

    def set_down(self, place):
        self.neighbour[1] = place

    def set_left(self, place):
        self.neighbour[2] = place

    def set_right(self, place):
        self.neighbour[3] = place

    def get_name(self):
        if self.occupant == 0:
            return "empty"
        elif self.occupant.name == "ant":
            return "ant"
        elif self.occupant.name == "pile":
            return "pile"

        return 0

    def get_moves(self, neig):
        moves = []
        available_sticks = []
        available_piles = []
        for i in range(4):
            if self.neighbour[i].get_name() == "pile" and MAX_STICK >= self.neighbour[i].occupant.size >= MIN_STICK:
                available_sticks.append(i)
            if self.neighbour[i].get_name() == "pile" and MIN_STICK <= self.neighbour[i].occupant.size < MAX_PILE:
                available_piles.append(i)
            elif self.neighbour[i].get_name() == "empty":
                moves.append(i)

        if neig == 1:
            for i in range(2):
                if self.neighbour[i].neighbour[2].get_name() == "pile" and MAX_STICK >= self.neighbour[i].neighbour[
                    2].occupant.size >= MIN_STICK:
                    available_sticks.append(i + 4)
                if self.neighbour[i].neighbour[2].get_name() == "pile" and MIN_STICK <= self.neighbour[i].neighbour[
                    2].occupant.size < MAX_PILE:
                    available_piles.append(i + 4)
                elif self.neighbour[i].neighbour[2].get_name() == "empty":
                    moves.append(i + 4)
                if self.neighbour[i].neighbour[3].get_name() == "pile" and MAX_STICK >= self.neighbour[i].neighbour[
                    3].occupant.size >= MIN_STICK:
                    available_sticks.append(i + 6)
                if self.neighbour[i].neighbour[3].get_name() == "pile" and MIN_STICK <= self.neighbour[i].neighbour[
                    3].occupant.size < MAX_PILE:
                    available_piles.append(i + 6)
                elif self.neighbour[i].neighbour[3].get_name() == "empty":
                    moves.append(i + 6)

        return moves, available_sticks, available_piles


class Ant:
    def __init__(self, carrying, place, used):
        self.name = "ant"
        self.carrying = carrying
        self.place = place
        self.used = used


class Pile:
    def __init__(self, size, place):
        self.name = "pile"
        self.size = size
        self.place = place


class AntsAndSticks(simcx.Simulator):

    def __init__(self, width=50, height=50, initial_ants=1, initial_sticks=1):
        super(AntsAndSticks, self).__init__()

        self.width = width
        self.height = height
        self.values = [[Place(i, j, 0) for i in range(self.width)] for j in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):

                if x > 0:
                    self.values[x - 1][y].set_right(self.values[x][y])
                    self.values[x][y].set_left(self.values[x - 1][y])
                if y > 0:
                    self.values[x][y - 1].set_down(self.values[x][y])
                    self.values[x][y].set_up(self.values[x][y - 1])
                if x == self.width - 1:
                    self.values[0][y].set_left(self.values[x][y])
                    self.values[x][y].set_right(self.values[0][y])
                if y == self.height - 1:
                    self.values[x][0].set_up(self.values[x][y])
                    self.values[x][y].set_down(self.values[x][0])

        self.initial_ants = initial_ants
        self.initial_sticks = initial_sticks
        self.dirty = False

        i = 0
        while i < initial_ants:
            new_x = round(random.uniform(0, self.width - 1))
            new_y = round(random.uniform(0, self.height - 1))
            if self.values[new_x][new_y].occupant == 0:
                new_ant = Ant(0, self.values[new_x][new_y], 0)
                self.values[new_x][new_y].occupant = new_ant
                i = i + 1

        i = 0
        while i < initial_sticks:
            new_x = round(random.uniform(0, self.width - 1))
            new_y = round(random.uniform(0, self.height - 1))
            if self.values[new_x][new_y].occupant == 0:
                new_stick = Pile(1, self.values[new_x][new_y])
                self.values[new_x][new_y].occupant = new_stick
                i = i + 1

    def movement_VonNeumann(self, y, x, ant, moves_neig):
        moves, available_sticks, available_piles = self.values[x][y].get_moves(moves_neig)

        if ant.used == 0 and ant.carrying == 0 and len(available_sticks) > 0:
            dir = random.choice(available_sticks)
            ant.carrying = 1
            ant.used = 1
            self.values[x][y].occupant = ant

            if dir == 0:  # Up
                if y - 1 == -1:
                    y = self.height
                if self.values[x][y - 1].occupant.size - 1 == 0:
                    self.values[x][y - 1].occupant = 0
                else:
                    self.values[x][y - 1].occupant.size = self.values[x][y - 1].occupant.size - 1

            elif dir == 1:  # Down
                if y + 1 == self.height:
                    y = -1
                if self.values[x][y + 1].occupant.size - 1 == 0:
                    self.values[x][y + 1].occupant = 0
                else:
                    self.values[x][y + 1].occupant.size = self.values[x][y + 1].occupant.size - 1

            elif dir == 2:  # Left
                if x - 1 == -1:
                    x = self.width
                if self.values[x - 1][y].occupant.size - 1 == 0:
                    self.values[x - 1][y].occupant = 0
                else:
                    self.values[x - 1][y].occupant.size = self.values[x - 1][y].occupant.size - 1

            elif dir == 3:  # Right
                if x + 1 == self.width:
                    x = -1
                if self.values[x + 1][y].occupant.size - 1 == 0:
                    self.values[x + 1][y].occupant = 0
                else:
                    self.values[x + 1][y].occupant.size = self.values[x + 1][y].occupant.size - 1

            return [y, x]

        elif ant.used == 0 and ant.carrying == 1 and len(available_piles) > 0:
            dir = random.choice(available_piles)
            ant.used = 1
            ant.carrying = 0
            self.values[x][y].occupant = ant

            if dir == 0:  # Up
                if y - 1 == -1:
                    y = self.height
                self.values[x][y - 1].occupant.size = self.values[x][y - 1].occupant.size + 1

            elif dir == 1:  # Down
                if y + 1 == self.height:
                    y = -1
                self.values[x][y + 1].occupant.size = self.values[x][y + 1].occupant.size + 1

            elif dir == 2:  # Left
                if x - 1 == -1:
                    x = self.width
                self.values[x - 1][y].occupant.size = self.values[x - 1][y].occupant.size + 1

            elif dir == 3:  # Right
                if x + 1 == self.width:
                    x = -1
                self.values[x + 1][y].occupant.size = self.values[x + 1][y].occupant.size + 1

            return [y, x]

        ant.used = 0

        if len(moves) == 0:
            self.values[x][y].occupant = ant
            return [y, x]

        dir = random.choice(moves)

        if dir == 0:  # Up
            if y - 1 == -1:
                y = self.height
            ant.place = self.values[x][y - 1]
            self.values[x][y - 1].occupant = ant
            return [y - 1, x]

        elif dir == 1:  # Down
            if y + 1 == self.height:
                y = -1
            ant.place = self.values[x][y + 1]
            self.values[x][y + 1].occupant = ant
            return [y + 1, x]

        elif dir == 2:  # Left
            if x - 1 == -1:
                x = self.width

            ant.place = self.values[x - 1][y]
            self.values[x - 1][y].occupant = ant
            return [y, x - 1]

        elif dir == 3:  # Right
            if x + 1 == self.width:
                x = -1

            ant.place = self.values[x + 1][y]
            self.values[x + 1][y].occupant = ant

            return [y, x + 1]

    def movement_Moore(self, y, x, ant, moves_neig):
        moves, available_sticks, available_piles = self.values[x][y].get_moves(moves_neig)

        if ant.used == 0 and ant.carrying == 0 and len(available_sticks) > 0:
            dir = random.choice(available_sticks)
            ant.carrying = 1
            ant.used = 1
            self.values[x][y].occupant = ant

            if dir == 0:  # Up
                if y - 1 == -1:
                    y = self.height
                if self.values[x][y - 1].occupant.size - 1 == 0:
                    self.values[x][y - 1].occupant = 0
                else:
                    self.values[x][y - 1].occupant.size = self.values[x][y - 1].occupant.size - 1

            elif dir == 1:  # Down
                if y + 1 == self.height:
                    y = -1
                if self.values[x][y + 1].occupant.size - 1 == 0:
                    self.values[x][y + 1].occupant = 0
                else:
                    self.values[x][y + 1].occupant.size = self.values[x][y + 1].occupant.size - 1

            elif dir == 2:  # Left
                if x - 1 == -1:
                    x = self.width
                if self.values[x - 1][y].occupant.size - 1 == 0:
                    self.values[x - 1][y].occupant = 0
                else:
                    self.values[x - 1][y].occupant.size = self.values[x - 1][y].occupant.size - 1

            elif dir == 3:  # Right
                if x + 1 == self.width:
                    x = -1
                if self.values[x + 1][y].occupant.size - 1 == 0:
                    self.values[x + 1][y].occupant = 0
                else:
                    self.values[x + 1][y].occupant.size = self.values[x + 1][y].occupant.size - 1

            elif dir == 4:  # up left
                if y - 1 == -1:
                    y = self.height
                if x - 1 == -1:
                    x = self.width

                if self.values[x - 1][y - 1].occupant.size - 1 == 0:
                    self.values[x - 1][y - 1].occupant = 0
                else:
                    self.values[x - 1][y - 1].occupant.size = self.values[x - 1][y - 1].occupant.size - 1

            elif dir == 5:  # down left
                if y + 1 == self.height:
                    y = -1
                if x - 1 == -1:
                    x = self.width

                if self.values[x - 1][y + 1].occupant.size - 1 == 0:
                    self.values[x - 1][y + 1].occupant = 0
                else:
                    self.values[x - 1][y + 1].occupant.size = self.values[x - 1][y + 1].occupant.size - 1

            elif dir == 6:  # up Right
                if y - 1 == -1:
                    y = self.height
                if x + 1 == self.width:
                    x = -1
                if self.values[x + 1][y - 1].occupant.size - 1 == 0:
                    self.values[x + 1][y - 1].occupant = 0
                else:
                    self.values[x + 1][y - 1].occupant.size = self.values[x + 1][y - 1].occupant.size - 1

            elif dir == 7:  # down Right
                if y + 1 == self.height:
                    y = -1
                if x + 1 == self.width:
                    x = -1
                if self.values[x + 1][y + 1].occupant.size - 1 == 0:
                    self.values[x + 1][y + 1].occupant = 0
                else:
                    self.values[x + 1][y + 1].occupant.size = self.values[x + 1][y + 1].occupant.size - 1

            return [y, x]

        elif ant.used == 0 and ant.carrying == 1 and len(available_piles) > 0:
            dir = random.choice(available_piles)
            ant.used = 1
            ant.carrying = 0
            self.values[x][y].occupant = ant

            if dir == 0:  # Up
                if y - 1 == -1:
                    y = self.height
                self.values[x][y - 1].occupant.size = self.values[x][y - 1].occupant.size + 1

            elif dir == 1:  # Down
                if y + 1 == self.height:
                    y = -1
                self.values[x][y + 1].occupant.size = self.values[x][y + 1].occupant.size + 1

            elif dir == 2:  # Left
                if x - 1 == -1:
                    x = self.width
                self.values[x - 1][y].occupant.size = self.values[x - 1][y].occupant.size + 1

            elif dir == 3:  # Right
                if x + 1 == self.width:
                    x = -1
                self.values[x + 1][y].occupant.size = self.values[x + 1][y].occupant.size + 1

            elif dir == 4:  # up left
                if y - 1 == -1:
                    y = self.height
                if x - 1 == -1:
                    x = self.width

                self.values[x - 1][y - 1].occupant.size = self.values[x - 1][y - 1].occupant.size + 1

            elif dir == 5:  # down left
                if y + 1 == self.height:
                    y = -1
                if x - 1 == -1:
                    x = self.width

                self.values[x - 1][y + 1].occupant.size = self.values[x - 1][y + 1].occupant.size + 1

            elif dir == 6:  # up Right
                if y - 1 == -1:
                    y = self.height
                if x + 1 == self.width:
                    x = -1
                self.values[x + 1][y - 1].occupant.size = self.values[x + 1][y - 1].occupant.size + 1

            elif dir == 7:  # down Right
                if y + 1 == self.height:
                    y = -1
                if x + 1 == self.width:
                    x = -1
                self.values[x + 1][y + 1].occupant.size = self.values[x + 1][y + 1].occupant.size + 1

            return [y, x]

        ant.used = 0

        if len(moves) == 0:
            self.values[x][y].occupant = ant
            return [y, x]

        dir = random.choice(moves)

        if dir == 0:  # Up
            if y - 1 == -1:
                y = self.height
            ant.place = self.values[x][y - 1]
            self.values[x][y - 1].occupant = ant
            return [y - 1, x]

        elif dir == 1:  # Down
            if y + 1 == self.height:
                y = -1
            ant.place = self.values[x][y + 1]
            self.values[x][y + 1].occupant = ant
            return [y + 1, x]

        elif dir == 2:  # Left
            if x - 1 == -1:
                x = self.width

            ant.place = self.values[x - 1][y]
            self.values[x - 1][y].occupant = ant
            return [y, x - 1]

        elif dir == 3:  # Right
            if x + 1 == self.width:
                x = -1

            ant.place = self.values[x + 1][y]
            self.values[x + 1][y].occupant = ant

            return [y, x + 1]

        elif dir == 4:  # up left
            if y - 1 == -1:
                y = self.height
            if x - 1 == -1:
                x = self.width

            ant.place = self.values[x - 1][y - 1]
            self.values[x - 1][y - 1].occupant = ant

            return [y - 1, x - 1]

        elif dir == 5:  # down left
            if y + 1 == self.height:
                y = -1
            if x - 1 == -1:
                x = self.width

            ant.place = self.values[x - 1][y + 1]
            self.values[x - 1][y + 1].occupant = ant

            return [y + 1, x - 1]

        elif dir == 6:  # up Right
            if y - 1 == -1:
                y = self.height
            if x + 1 == self.width:
                x = -1

            ant.place = self.values[x + 1][y - 1]
            self.values[x + 1][y - 1].occupant = ant

            return [y - 1, x + 1]

        elif dir == 7:  # down Right
            if y + 1 == self.height:
                y = -1
            if x + 1 == self.width:
                x = -1

            ant.place = self.values[x + 1][y + 1]
            self.values[x + 1][y + 1].occupant = ant

            return [y + 1, x + 1]

    def step(self, delta=0):
        moved = []
        rand_x = list(range(0, self.height))
        rand_y = list(range(0, self.width))
        random.shuffle(rand_x)
        random.shuffle(rand_y)
        for y in rand_y:
            for x in rand_x:
                if [y, x] not in moved and self.values[x][y].get_name() == "ant":
                    ant = self.values[x][y].occupant
                    self.values[x][y].occupant = 0
                    moved.append(self.movement_Moore(y, x, ant, 1))

        self.dirty = True


class Grid2D(simcx.Visual):
    QUAD_ANT_STICK = (0, 0, 0) * 4
    QUAD_ANT = (155, 155, 155) * 4
    QUAD_WHITE = (255, 255, 255) * 4

    def __init__(self, sim: simcx.Simulator, cell_size=20):
        super(Grid2D, self).__init__(sim, width=sim.width * cell_size, height=sim.height * cell_size)

        self._grid_width = sim.width
        self._grid_height = sim.height

        # create graphics objects
        self._batch = pyglet.graphics.Batch()
        self._grid = []
        for y in range(self._grid_height):
            self._grid.append([])
            for x in range(self._grid_width):
                vertex_list = self._batch.add(4, pyglet.gl.GL_QUADS, None,
                                              ('v2i',
                                               (x * cell_size, y * cell_size,
                                                x * cell_size + cell_size,
                                                y * cell_size,
                                                x * cell_size + cell_size,
                                                y * cell_size + cell_size,
                                                x * cell_size,
                                                y * cell_size + cell_size)),
                                              ('c3B', self.QUAD_WHITE))
                self._grid[y].append(vertex_list)

    def draw(self):
        if self.sim.dirty:
            self._update_graphics()
        self._batch.draw()

    def _update_graphics(self):
        for y in range(self._grid_height):
            for x in range(self._grid_width):
                if self.sim.values[x][y].get_name() == "ant":
                    if self.sim.values[x][y].occupant.carrying == 1:
                        self._grid[y][x].colors[:] = self.QUAD_ANT_STICK
                    else:
                        self._grid[y][x].colors[:] = self.QUAD_ANT
                elif self.sim.values[x][y].get_name() == "pile":
                    color_gradient = self.sim.values[x][y].occupant.size * round(255 / MAX_PILE)
                    QUAD_STICK = (255 - color_gradient, 255 - color_gradient, color_gradient) * 4
                    self._grid[y][x].colors[:] = QUAD_STICK
                else:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE


if __name__ == '__main__':
    aas = AntsAndSticks(75, 75, 500, 500)
    vis = Grid2D(aas, 7)

    display = simcx.Display()
    display.add_simulator(aas)
    display.add_visual(vis)
simcx.run()
