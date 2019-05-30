# We want to study the macro behavior of this kind of world, analyzing itin the time and in the space dimensions. We
# want to know the influence of the initial density of wood sticks and of ants. Also, we intent to clarify the
# importance of the type of neighborhood considered (i.e., Moore, Von Neumann or other). Suppose that you introduce a
# limit for the capacity of each cell to keep the wood sticks. What is the result? Suppose that we may

import simcx
import random
import pyglet
import os

MAX_PILE = 5
MIN_STICK = 1
MAX_STICK = 1
step_count = 0


class Place:
    def __init__(self, x, y, occupant):
        self.x = x
        self.y = y
        self.occupant = occupant
        self.neighbour = [None] * 4
        self.pher_level = 0
        self.trail = 0
        self.freq = 0

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

    def get_moves(self, move_neig, pick_neig, ant, backwards):
        moves = []
        available_sticks = []
        available_piles = []
        for i in range(4):
            if self.neighbour[i] != None:
                if self.neighbour[i].get_name() == "pile" and MAX_STICK >= self.neighbour[i].occupant.size >= MIN_STICK:
                    available_sticks.append(i)
                if self.neighbour[i].get_name() == "pile" and MIN_STICK <= self.neighbour[i].occupant.size < MAX_PILE:
                    available_piles.append(i)
                elif self.neighbour[i].get_name() == "empty":
                    if backwards == 0:
                        if ant.last_visited != self.neighbour[i]:
                            moves.append(i)
                    else:
                        moves.append(i)

        if pick_neig == 1:
            for i in range(2):
                if self.neighbour[i].neighbour[2] is not None:
                    if self.neighbour[i].neighbour[2].get_name() == "pile" and MAX_STICK >= self.neighbour[i].neighbour[
                        2].occupant.size >= MIN_STICK:
                        available_sticks.append(i + 4)
                    if self.neighbour[i].neighbour[2].get_name() == "pile" and MIN_STICK <= self.neighbour[i].neighbour[
                        2].occupant.size < MAX_PILE:
                        available_piles.append(i + 4)
                if self.neighbour[i].neighbour[3] is not None:
                    if self.neighbour[i].neighbour[3].get_name() == "pile" and MAX_STICK >= self.neighbour[i].neighbour[
                        3].occupant.size >= MIN_STICK:
                        available_sticks.append(i + 6)
                    if self.neighbour[i].neighbour[3].get_name() == "pile" and MIN_STICK <= self.neighbour[i].neighbour[
                        3].occupant.size < MAX_PILE:
                        available_piles.append(i + 6)

        if move_neig == 1:
            for i in range(2):
                if self.neighbour[i] is not None:
                    if self.neighbour[i].neighbour[2] is not None:

                        if self.neighbour[i].neighbour[2].get_name() == "empty" and ant.last_visited != \
                                self.neighbour[i].neighbour[2]:
                            if backwards == 0:
                                if ant.last_visited != self.neighbour[i].neighbour[2]:
                                    moves.append(i + 4)
                            else:
                                moves.append(i + 4)
                    if self.neighbour[i].neighbour[3] is not None:
                        if self.neighbour[i].neighbour[3].get_name() == "empty" and ant.last_visited != \
                                self.neighbour[i].neighbour[3]:
                            if backwards == 0:
                                if ant.last_visited != self.neighbour[i].neighbour[3]:
                                    moves.append(i + 6)
                            else:
                                moves.append(i + 6)

        return moves, available_sticks, available_piles


class Ant:
    def __init__(self, carrying, place, used):
        self.name = "ant"
        self.carrying = carrying
        self.place = place
        self.used = used
        self.last_visited = None


class Pile:
    def __init__(self, size, place):
        self.name = "pile"
        self.size = size
        self.place = place


class AntsAndSticks(simcx.Simulator):

    def __init__(self, moveType, pickType, width=50, height=50, initial_ants=1, initial_sticks=1, backwards=1, warp=1,
                 zones=None, pheromone=0):
        super(AntsAndSticks, self).__init__()

        self.moveType = moveType
        self.pickType = pickType
        self.width = width
        self.height = height
        self.pheromone = pheromone
        self.backwards = backwards

        # create world
        self.values = [[Place(i, j, 0) for i in range(self.width)] for j in range(self.height)]

        # neighbour set up
        for x in range(self.width):
            for y in range(self.height):

                if x > 0:
                    self.values[x - 1][y].set_right(self.values[x][y])
                    self.values[x][y].set_left(self.values[x - 1][y])
                if y > 0:
                    self.values[x][y - 1].set_down(self.values[x][y])
                    self.values[x][y].set_up(self.values[x][y - 1])
                if warp == 1:
                    if x == self.width - 1:
                        self.values[0][y].set_left(self.values[x][y])
                        self.values[x][y].set_right(self.values[0][y])
                    if y == self.height - 1:
                        self.values[x][0].set_up(self.values[x][y])
                        self.values[x][y].set_down(self.values[x][0])

        self.initial_ants = initial_ants
        self.initial_sticks = initial_sticks
        self.dirty = False

        if zones is None:
            # randomly sets up ants
            i = 0
            while i < initial_ants:
                new_x = round(random.uniform(0, self.width - 1))
                new_y = round(random.uniform(0, self.height - 1))
                if self.values[new_x][new_y].occupant == 0:
                    new_ant = Ant(0, self.values[new_x][new_y], 0)
                    self.values[new_x][new_y].occupant = new_ant
                    i = i + 1

            # randomly sets up sticks
            i = 0
            while i < initial_sticks:
                new_x = round(random.uniform(0, self.width - 1))
                new_y = round(random.uniform(0, self.height - 1))
                if self.values[new_x][new_y].occupant == 0:
                    new_stick = Pile(1, self.values[new_x][new_y])
                    self.values[new_x][new_y].occupant = new_stick
                    i = i + 1
        else:
            w = [0, self.width // 3, 2 * (self.width // 3), 3 * ((self.width // 3) + (self.width % 3)) - 1]
            h = [0, self.height // 3, 2 * (self.height // 3), 3 * ((self.height // 3) + (self.height % 3)) - 1]

            for j in range(3):
                for k in range(3):
                    i = 0
                    rand1w = w[(k % 3)]
                    rand2w = w[(k % 3) + 1]
                    rand1h = h[(j % 3)]
                    rand2h = h[(j % 3) + 1]
                    while i < zones[0][k + j * 3]:
                        new_x = round(random.uniform(rand1w, rand2w))
                        new_y = round(random.uniform(rand1h, rand2h))
                        if self.values[new_x][new_y].occupant == 0:
                            new_ant = Ant(0, self.values[new_x][new_y], 0)
                            self.values[new_x][new_y].occupant = new_ant
                            i = i + 1

            for j in range(3):
                for k in range(3):
                    i = 0
                    rand1w = w[(k % 3)]
                    rand2w = w[(k % 3) + 1]
                    rand1h = h[(j % 3)]
                    rand2h = h[(j % 3) + 1]
                    while i < zones[1][k + j * 3]:
                        new_x = round(random.uniform(rand1w, rand2w))
                        new_y = round(random.uniform(rand1h, rand2h))
                        if self.values[new_x][new_y].occupant == 0:
                            new_stick = Pile(1, self.values[new_x][new_y])
                            self.values[new_x][new_y].occupant = new_stick
                            i = i + 1

        # predefined spots

        # spots = [[x0, y0],[x1,y1]....]
        # i = 0
        # while i < n:
        #     new_x = spots[i][0]
        #     new_y = spots[i][1]
        #     if self.values[new_x][new_y].occupant == 0:
        #         new_ant = Ant(0, self.values[new_x][new_y], 0)
        #         self.values[new_x][new_y].occupant = new_ant
        #         i = i + 1

        # spots = [[x0, y0],[x1,y1]....]
        # i = 0
        # while i < n:
        #     new_x = spots[i][0]
        #     new_y = spots[i][1]
        #     if self.values[new_x][new_y].occupant == 0:
        #         new_stick = Pile(1, self.values[new_x][new_y])
        #         self.values[new_x][new_y].occupant = new_stick
        #         i = i + 1

    def check_pher(self, moves, x, y):
        random.shuffle(moves)
        for i in range(len(moves)):
            if moves[i] == 0:
                this_y = y
                if this_y - 1 == -1:
                    this_y = self.height
                if self.values[x][this_y - 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 1:
                this_y = y
                if this_y + 1 == self.height:
                    this_y = -1
                if self.values[x][this_y + 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 2:
                this_x = x
                if this_x - 1 == -1:
                    this_x = self.width

                if self.values[this_x - 1][y].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 3:
                this_x = x
                if this_x + 1 == self.width:
                    this_x = -1
                if self.values[this_x + 1][y].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 4:
                this_y = y
                this_x = x
                if this_y - 1 == -1:
                    this_y = self.height
                if this_x - 1 == -1:
                    this_x = self.width
                if self.values[this_x - 1][this_y - 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 5:
                this_y = y
                this_x = x
                if this_y + 1 == self.height:
                    this_y = -1
                if this_x - 1 == -1:
                    this_x = self.width
                if self.values[this_x - 1][this_y + 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 6:
                this_y = y
                this_x = x
                if this_y - 1 == -1:
                    this_y = self.height
                if this_x + 1 == self.width:
                    this_x = -1
                if self.values[this_x + 1][this_y - 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            if moves[i] == 7:
                this_y = y
                this_x = x
                if this_y + 1 == self.height:
                    this_y = -1
                if this_x + 1 == self.width:
                    this_x = -1
                if self.values[this_x + 1][this_y + 1].pher_level > 0 or random.random() < 0.1:
                    dir = moves[i]
                    break

            else:
                dir = random.choice(moves)

        return dir

    def movement(self, y, x, ant, moves_neig, pick_neig):
        moves, available_sticks, available_piles = self.values[x][y].get_moves(moves_neig, pick_neig, ant, self.backwards)

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

        if self.pheromone == 0:
            dir = random.choice(moves)
        else:
            dir = self.check_pher(moves, x, y)

        ant.last_visited = ant.place

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
        global step_count
        step_count = step_count + 1
        available_piles = 0
        available_sticks = 0
        carrying_ants = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.values[x][y].pher_level != 0:
                    new_pher = self.values[x][y].pher_level - 5
                    if new_pher < 0:
                        new_pher = 0
                    self.values[x][y].pher_level = new_pher

                if self.values[x][y].get_name() == "pile" and MAX_STICK >= self.values[x][y].occupant.size:
                    available_sticks = available_sticks + 1

                if self.values[x][y].get_name() == "pile" and MAX_STICK < self.values[x][y].occupant.size < MAX_PILE:
                    available_piles = available_piles + 1

                if self.values[x][y].get_name() == "ant" and self.values[x][y].occupant.carrying == 1:
                    carrying_ants = carrying_ants + 1

        if (available_sticks > 0 or (available_piles > 0 and carrying_ants > 0)) or step_count == 1000:
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
                        # set pheromone
                        if self.pheromone == 1 or (self.pheromone == 2 and ant.carrying == 1):
                            self.values[x][y].pher_level = 255

                        if ant.carrying == 1:
                            self.values[x][y].trail = 255

                        self.values[x][y].freq += 2

                        if self.moveType == "moore":
                            if self.pickType == "moore":
                                moved.append(self.movement(y, x, ant, 1, 1))

                            elif self.pickType == "von":
                                moved.append(self.movement(y, x, ant, 1, 0))

                        elif self.moveType == "von":
                            if self.pickType == "moore":
                                moved.append(self.movement(y, x, ant, 0, 1))

                            elif self.pickType == "von":
                                moved.append(self.movement(y, x, ant, 0, 0))

            self.dirty = True

        else:
            average_size = 0
            n_piles = 0
            for x in range(self.width):
                for y in range(self.height):
                    if self.values[x][y].get_name() == "pile":
                        n_piles = n_piles + 1
                    if self.values[x][y].get_name() == "ant" and self.values[x][y].occupant.carrying == 1:
                        carrying_ants = carrying_ants + 1

            for x in range(self.width):
                for y in range(self.height):
                    if self.values[x][y].get_name() == "pile":
                        average_size = average_size + self.values[x][y].occupant.size
            if n_piles != 0:
                print("average pile size -> " + str(average_size / n_piles))
            else:
                print("average pile size -> 0")
            print("number of steps -> " + str(step_count))
            print("number of ants carrying sticks -> " + str(carrying_ants))
            print("number of piles in the last instance -> " + str(n_piles))
            os.system("pause")


class Grid2D(simcx.Visual):
    QUAD_ANT_STICK = (0, 0, 0) * 4
    QUAD_ANT = (0, 155, 155) * 4
    QUAD_WHITE = (255, 255, 255) * 4

    def __init__(self, sim: simcx.Simulator, cell_size=20, pheromone=0, trail=0, freq=0):
        super(Grid2D, self).__init__(sim, width=sim.width * cell_size, height=sim.height * cell_size)
        self.pheromone = pheromone
        self.trail = trail
        self.freq = freq
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
                if self.pheromone == 1:
                    self._grid[y][x].colors[:] = (self.sim.values[x][y].pher_level, 0, self.sim.values[x][y].pher_level) * 4
                if self.trail == 1:
                    self._grid[y][x].colors[:] = (self.sim.values[x][y].trail, self.sim.values[x][y].trail // 2, 0) * 4
                if self.freq == 1:
                    fcolor = self.sim.values[x][y].freq
                    self._grid[y][x].colors[:] = (255 - fcolor, 255 - fcolor, 255 - fcolor) * 4

                if self.sim.values[x][y].get_name() == "ant":
                    if self.sim.values[x][y].occupant.carrying == 1:
                        self._grid[y][x].colors[:] = self.QUAD_ANT_STICK
                    else:
                        self._grid[y][x].colors[:] = self.QUAD_ANT
                elif self.sim.values[x][y].get_name() == "pile":
                    color_gradient = self.sim.values[x][y].occupant.size * round(255 / MAX_PILE)
                    QUAD_STICK = (255 - color_gradient, 255 - color_gradient, color_gradient) * 4
                    self._grid[y][x].colors[:] = QUAD_STICK

                elif self.pheromone == 1 and self.sim.values[x][y].pher_level == 0:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE

                elif self.trail == 1 and self.sim.values[x][y].trail == 0:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE

                elif self.freq == 1 and self.sim.values[x][y].freq == 0:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE
                else:
                    self._grid[y][x].colors[:] = self.QUAD_WHITE




if __name__ == '__main__':
    move_type = "von"
    pick_type = "von"
    map_x = 30
    map_y = 30
    initial_ants = 30
    initial_sticks = 30
    backwards = 0  # 1-> can go backwards || 0 -> cannot go backwards
    warp = 1  # 1-> map warps || 0 -> map does not warp
    zones = None
    # zones = [[0, 0, 0, 0, 0, 0, 20, 0, 0], [0, 0, 20, 0, 0, 0, 0, 0, 0]]
    pheromone = 2  # -> 0 no pheromone | 1 -> pheromone allways | 2 -> pheromone only when carrying

    aas = AntsAndSticks(move_type, pick_type, map_x, map_y, initial_ants, initial_sticks, backwards, warp, zones, pheromone)
    vis = Grid2D(aas, 5, trail=0, pheromone=0, freq=0)

    display = simcx.Display(interval=0.1)
    display.add_simulator(aas)
    display.add_visual(vis)
simcx.run()
