# We want to study the macro behavior of this kind of world, analyzing itin the time and in the space dimensions. We
# want to know the influence of the initial density of wood sticks and of ants. Also, we intent to clarify the
# importance of the type of neighborhood considered (i.e., Moore, Von Neumann or other). Suppose that you introduce a
# limit for the capacity of each cell to keep the wood sticks. What is the result? Suppose that we may

import simcx
import random
import numpy as np
import pyglet


class AntsAndSticks(simcx.Simulator):

    def __init__(self, width=50, height=50, initial_ants=1):
        super(AntsAndSticks, self).__init__()

        self.width = width
        self.height = height
        self.values = np.zeros((self.height, self.width))
        self.initial_ants = initial_ants
        self.dirty = False

        i = 0;
        while i < initial_ants:
            new_x = round(random.uniform(0, self.width - 1))

            new_y = round(random.uniform(0, self.height - 1))
            if self.values[new_x, new_y] == 0:
                self.values[new_x, new_y] = 1
                i = i + 1

    def movement_VonNeumann(self, y, x):
        dir = random.randint(1, 4)
        if dir == 1:  # Up
            if y + 1 == self.height:
                y = -1
            self.values[y + 1, x] = 1
            return [y + 1, x]

        elif dir == 2:  # Down
            if y - 1 == -1:
                y = self.height - 1
            self.values[y - 1, x] = 1
            return [y - 1, x]

        elif dir == 3:  # Left
            if x - 1 == -1:
                x = self.width - 1
            self.values[y, x - 1] = 1
            return [y, x - 1]

        else:  # Right
            if x + 1 == self.height:
                x = -1
            self.values[y, x + 1] = 1
            return [y, x + 1]

    def step(self, delta=0):
        moved = []
        for y in range(self.height):
            for x in range(self.width):
                if [y, x] not in moved and self.values[y, x] == 1:
                    self.values[y, x] = 0
                    moved.append(self.movement_VonNeumann(y, x))
                elif [y, x] in moved:
                    self.values[y, x] = 1
                else:
                    self.values[y, x] = 0

        self.dirty = True


class Grid2D(simcx.Visual):
    QUAD_STICK = (255, 0, 0) * 4
    QUAD_PILE = (0, 0, 255) * 4
    QUAD_ANT = (0, 0, 0) * 4
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
                if self.sim.values[y, x] == 1:
                    self._grid[y][x].colors[:] = self.QUAD_ANT
                else:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE


if __name__ == '__main__':
    # Example patterns

    gol = AntsAndSticks(75, 75)
    vis = Grid2D(gol, 7)

    display = simcx.Display(interval=0.1)
    display.add_simulator(gol)
    display.add_visual(vis)
simcx.run()
