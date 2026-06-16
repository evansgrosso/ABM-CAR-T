import numpy as np

from behavior import step
from configuration import SIMULATION_TICKS, TUMOR_GROWTH_RATE
from initial_state import initialize


def run(on_step=None):
    env, agents = initialize()
    kills = 0

    for t in range(SIMULATION_TICKS):
        population_before = env.population_grid.copy()

        for agent in agents:
            step(agent, env)

        kills_grid = population_before - env.population_grid
        kills_this_step = max(0, int(np.sum(kills_grid)))
        kills += kills_this_step

        growth = TUMOR_GROWTH_RATE * population_before * (1 - population_before / env.carrying_capacities)
        env.population_grid = np.clip(np.round(population_before + growth - kills_grid), 0, env.carrying_capacities)

        if on_step:
            on_step(t, env, agents, kills_this_step)

        agents = [a for a in agents if a.state != "dead"]

    return env, agents, kills