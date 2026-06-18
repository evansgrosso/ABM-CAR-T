import random

import numpy as np

from configuration import (
    HANDLING_TIME_PARAM,
    TRAVERSAL_SCALE,
    TRAVERSAL_TIME_MULTIPLIER,
    KILL_DURATION_SUCCESS,
    KILL_DURATION_FAIL,
    EXHAUSTION_K_C,
    EXHAUSTION_K_P,
    EXHAUSTION_K_L,
)


def compute_probabilities(agent, environment):
    row, col = agent.position
    p = environment.population_grid[row, col] # Fetches population of agent's current position

    junctions = {}
    if row > 0:
        junctions["west"] = environment.stroma_horizontal[row, col]
    if row < environment.n - 1:
        junctions["east"] = environment.stroma_horizontal[row + 1, col]
    if col > 0:
        junctions["south"] = environment.stroma_vertical[row, col]
    if col < environment.n - 1:
        junctions["north"] = environment.stroma_vertical[row, col + 1]

    d_avg = sum(junctions.values())/len(junctions.values()) # Finds average of agent's surrounding stromal densities

    probability_handling = (1 - agent.exhaustion) * (agent.affinity * p) / (1 + (agent.affinity * HANDLING_TIME_PARAM * p)) # Determines probability of entering handling state
    probability_traversing = (1 - probability_handling) / (1 + TRAVERSAL_SCALE * d_avg) # Determines probability of entering traversal state
    probability_searching = 1 - probability_handling - probability_traversing # Determines probability of entering searching state

    return probability_handling, probability_traversing, probability_searching


def draw_state(probability_handling, probability_traversing, probability_searching):
    state_choices = ["handling", "traversing", "searching"]
    return random.choices(state_choices, [probability_handling, probability_traversing, probability_searching], k=1)[0] # Makes weighted decision on behavior state


def update_exhaustion(agent, environment):
    row, col = agent.position
    p = environment.population_grid[row, col]
    if agent.state == "handling":
        agent.exhaustion = max(0, min(1, agent.exhaustion + (EXHAUSTION_K_P * p) + (EXHAUSTION_K_C * agent.t_spent) - (EXHAUSTION_K_L * agent.t_since)))
    else:
        agent.exhaustion = max(0, min(1, agent.exhaustion + (EXHAUSTION_K_P * p) - (EXHAUSTION_K_L * agent.t_since)))


def resolve_handling(agent, environment):
    row, col = agent.position
    if agent.pending_kill == True:
        if agent.t_spent < KILL_DURATION_SUCCESS:
            agent.t_spent += 1
            agent.t_since = 0
        else:
            environment.population_grid[row, col] -= 1
            agent.kills += 1
            agent.t_spent = 0
            agent.t_since = 0
            agent.state = "searching"
    if agent.pending_kill == False:
        if agent.t_spent < KILL_DURATION_FAIL:
            agent.t_spent += 1
            agent.t_since = 0
        else:
            agent.t_spent = 0
            agent.t_since = 0
            agent.state = "searching"


def resolve_traversal(agent, environment):
    row, col = agent.position
    junctions = {}
    if row > 0:
        junctions["west"] = environment.stroma_horizontal[row, col]
    if row < environment.n - 1:
        junctions["east"] = environment.stroma_horizontal[row + 1, col]
    if col > 0:
        junctions["south"] = environment.stroma_vertical[row, col]
    if col < environment.n - 1:
        junctions["north"] = environment.stroma_vertical[row, col + 1]

    directions = list(junctions.keys())
    densities = list(junctions.values())

    weights = [1.0 / (d + 1e-6) for d in densities] # 1e-6 to avoid divide by zero error; #TODO: Check that stromal density and agent traversal direction choice is inversely proportional or some other relationship 

    chosen_direction = random.choices(directions, weights, k=1)[0]

    chosen_stroma = junctions[chosen_direction]
    time_cross = max(1, round(chosen_stroma * TRAVERSAL_TIME_MULTIPLIER))

    if chosen_direction == "west":
        agent.position = (agent.position[0] - 1, agent.position[1])
    elif chosen_direction == "east":
        agent.position = (agent.position[0] + 1, agent.position[1])
    elif chosen_direction == "south":
        agent.position = (agent.position[0], agent.position[1] - 1)
    elif chosen_direction == "north":
        agent.position = (agent.position[0], agent.position[1] + 1)

    if agent.t_spent < time_cross:
        agent.t_spent += 1
        agent.t_since += 1
    else:
        agent.t_spent = 0
        agent.state = "searching"

def step(agent, environment):
    if agent.exhaustion >= 1:
        agent.state = "dead"
        return
    if agent.state == "searching":
        probability_handling, probability_traversing, probability_searching = compute_probabilities(agent, environment)
        next_state = draw_state(probability_handling, probability_traversing, probability_searching)
        if next_state == "handling":
            probability_kill = agent.affinity
            agent.pending_kill = random.choices([True, False], [probability_kill, 1 - probability_kill], k=1)[0]
            agent.t_spent = 0
            agent.state = "handling"
        if next_state == "traversing":
            agent.t_spent = 0
            agent.state = "traversing"
    if agent.state == "handling":
        resolve_handling(agent, environment)
    if agent.state == "traversing":
        resolve_traversal(agent, environment)
    update_exhaustion(agent, environment)
