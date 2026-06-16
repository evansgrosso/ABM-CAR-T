import random

import numpy as np

from agent import Agent
from configuration import NUM_AGENTS, AFFINITY_MEAN, AFFINITY_STD
from environment import Environment


def initialize():
    env = Environment()
    n = env.n
    
    border_cells = []
    for i in range(n):
        border_cells.append((0, i))
    for i in range(n):
        border_cells.append((n - 1, i))
    for i in range(1, n - 1):
        border_cells.append((i, 0))
    for i in range(1, n - 1):
        border_cells.append((i, n - 1))

    initial_positions = random.choices(border_cells, k=NUM_AGENTS)
    affinities = np.random.normal(AFFINITY_MEAN, AFFINITY_STD, NUM_AGENTS)

    agents = [Agent(initial_positions[i], affinities[i]) for i in range(NUM_AGENTS)]

    return env, agents
