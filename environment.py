import numpy as np
from noise import pnoise2

from configuration import (
    GRID_SIZE,
    CARRYING_CAPACITY_MAX,
    CARRYING_CAPACITY_MIN,
    PERLIN_SCALE,
    SEED_STROMA_HORIZONTAL,
    SEED_STROMA_VERTICAL,
    SEED_CARRYING_CAPACITY,
    SEED_POPULATION,
)


class Environment: #TODO: Professor Shuai mentioned there may be a more efficient way to create the environment
    def __init__(self):
        self.n = GRID_SIZE

        self.population_grid = np.zeros((self.n, self.n))
        self.carrying_capacities = np.zeros((self.n, self.n))
        self.stroma_horizontal = np.zeros((self.n + 1, self.n))
        self.stroma_vertical = np.zeros((self.n, self.n + 1))

        for i in range(self.n + 1):
            for j in range(self.n):
                self.stroma_horizontal[i][j] = pnoise2(i/PERLIN_SCALE, j/PERLIN_SCALE, 1, 0.5, 2, SEED_STROMA_HORIZONTAL)
        self.stroma_horizontal = (self.stroma_horizontal + 1) / 2

        for i in range(self.n):
            for j in range(self.n + 1):
                self.stroma_vertical[i][j] = pnoise2(i/PERLIN_SCALE, j/PERLIN_SCALE, 1, 0.5, 2, SEED_STROMA_VERTICAL)
        self.stroma_vertical = (self.stroma_vertical + 1) / 2

        for i in range(self.n):
            for j in range(self.n):
                self.carrying_capacities[i][j] = pnoise2(i/PERLIN_SCALE, j/PERLIN_SCALE, 1, 0.5, 2, SEED_CARRYING_CAPACITY)
        self.carrying_capacities = (self.carrying_capacities + 1) / 2
        self.carrying_capacities = np.maximum(np.round(self.carrying_capacities * CARRYING_CAPACITY_MAX), CARRYING_CAPACITY_MIN)

        for i in range(self.n):
            for j in range(self.n):
                self.population_grid[i][j] = self.carrying_capacities[i][j] * ((pnoise2(i/PERLIN_SCALE, j/PERLIN_SCALE, 1, 0.5, 2, SEED_POPULATION) + 1) / 2)
        self.population_grid = np.round(self.population_grid)
