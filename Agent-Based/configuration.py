# Environment

GRID_SIZE = 100

CARRYING_CAPACITY_MAX = 100

CARRYING_CAPACITY_MIN = 1

PERLIN_SCALE = 25

DENSITY_MULTIPLIER = 0.2

# Seeds for each independently generated noise layer
SEED_STROMA_HORIZONTAL = 42
SEED_STROMA_VERTICAL   = 43
SEED_CARRYING_CAPACITY = 44
SEED_POPULATION        = 45

# Agents

NUM_AGENTS = 10000 #TODO: Verify that expected effector:malignant ratio is defensible

AFFINITY_MEAN = 0.05
AFFINITY_STD  = 0.001

# Behavior

HANDLING_TIME_PARAM = 3

TRAVERSAL_SCALE = 1

TRAVERSAL_TIME_MULTIPLIER = 12 #TODO: Verify that traversal time multiplier is defensible. Determine spatial scale of simulated environment and compare it to in-vivo data of T-cell traversal

KILL_DURATION_SUCCESS = 2
KILL_DURATION_FAIL    = 4

EXHAUSTION_K_C = 0.01

EXHAUSTION_K_P = 0.001

EXHAUSTION_K_L = 0.001

# Simulation Rules

SIMULATION_TICKS = 672

TUMOR_GROWTH_RATE = 0.010
