#### CART-MVT-ABM
An agent based model of CAR T cells in a 2D desmoplastic tumor. Created to investigate for which environmental/agent parameters live immunotherapy treatment is viable.

#### Key Components
- **Environment**: 100 x 100 grid
	- **Stromal Density between Neighboring Pockets**: Each segment represents a layer of stroma
	- **Pocket Malignant Population**: Each square represents a pocket of malignant cells
- **CAR-T Agents**: An Agent Class to serve as the CAR-T cells
	- **Receptor-Binding Affinity**: Each agent will have variable receptor-binding affinity, which will determine its migratory/predatory behavior.
	- **Exhaustion**: Each agent will have a variable representing its exhaustion state, which will be determined by its interactions with other agents and its predatory activity
- **Time Ticks**: Represents the passage of time
	- One time tick = 1 hour.
#### Environment Logic
- **Density Value**: Each grid segment will have a randomly generated "density" value, which will determine the time-cost for a CAR-T cell to penetrate it.
- **Malignant Population**: Each grid square will have a randomly generated initial population value.
#### Agent Behavior States
- **Behavior States**
	- **Searching state**: The agent is within a malignant pocket, migratory/predatory action pending
	- **Handling state**: The agent is undergoing a cytotoxic interaction.
		- *Successful Kill*: Malignant Cell dies. Malignant population drops by one. Exhaustion increases moderately. Lasts 2 ticks. 
		- *Unsuccessful Kill*: Malignant Cell does not die. Malignant population remains the same. Exhaustion increases moderately. Lasts 4 ticks.
	- **Traversal State**: The agent is traveling through a stroma to enter a new pocket of malignant cells (grid square).
- **Exhaustion**: An agent's exhaustion value will be incorporated into the state-probability equations to account for the relative slowing of immune activity of a given agent per its increasing exhaustion.
	- **Terminal Exhaustion**: Exhaustion variable reaches threshold value of $\epsilon = 1$. All functions stop. Agent is functionally "dead". 
#### ABM Key Variables
- **Time Ticker ($t$)**
- **Agent Receptor Binding Affinity** ($\alpha$) 
- **Malignant Pocket Population** ($p$) 
- **Inter-Pocket Stromal Density** ($d$) 
- **Agent Exhaustion Variable** ($\epsilon$)
- **Handling Time Parameter** ($\tau_c$) 
- **Malignant Growth Rate** (r)
- **Malignant Carrying Capacity**: ($K$) (minimum value: 1)
#### ABM Environmental Logic
- **Generating Initial Population**: $\mathbf{P}_p (x,y)$
- **Generating Stromal Densities**: $H(x,y); V(x,y)$
- **Generating Malignant Pocket Carrying Capacity**: $\mathbf{P}_K (x,y)$
- **Generating Malignant Growth ($p(t+1)$): $p(t+1) = p(t) + [r*p(t)]\frac{1-p(t)}{K_{(x,y)}} - kills(t)$
	- $p(t)$: The current population of the pocket
	- $r$: Malignant growth rate (aggressiveness). Uniform across all pockets (0.010 for a 72 hour doubling rate). 
	- $K_{(x,y)}$: Malignant population carrying capacity of the pocket
	- $kills(t)$: Number of kills that occur in the current tick
#### ABM Agent Behavior Logic
- **Generating Receptor Binding Affinities**: $\alpha_i = N(\mu_\alpha, \sigma_\alpha)$
- **Time to Cross Stroma**: $\tau_t = max(1, round(d*m))$
	- $m$: A time multiplier (12)
	- Max time to cross: 12 ticks
	- Min time to cross: 1 tick
- **Computing Agent Behavior**
	- **Probability of Searching State ($Q_s$)**: $Q_s$ = $1 - Q_h - Q_t$
	- **Probability Handling State ($Q_h$)**: $Q_h = \frac{\alpha p}{1 + \alpha \tau_c p}(1-\epsilon)$
		- $\alpha$: Higher affinity increases chance of entering handling state
		- $p$: More malignant cells means more opportunities to engage
		- $\tau_c$: Handling time parameter, averaged to 3 ticks.
		- $(1-\epsilon)$: Higher exhaustion suppresses handling capacity
	- **Probability Traversal State ($Q_t$)**: $Q_t = (1-Q_h)\cdot \frac{1}{1+d_{avg} \cdot s}$
		- $1-Q_h$: A higher probability of handing state should decrease traversal probability
		- $\frac{1}{1+d_{avg}}$: A higher density should decrease probability of traversal, with $Q_t$ approaching $0$ as $d$ goes to infinity
		- $s$: A traversal scaler that adjusts probability traversal state.
		- *Traversal Direction*: Determined by simple weighted probability, each choice's likelihood inversely proportional to its associated stromal density.
	- **Probability of Kill Success ($P_{kill}$)**: $P_{kill} = \alpha \cdot (1-\epsilon)$
- **Computing Agent Exhaustion ($\epsilon$)**: $\epsilon(t+1) = \epsilon(t) + k_c \Delta\tau_c + k_p p(t) - k_l \Delta\tau_l$
	- $\Delta\tau_l$: Time since last handling state
	- $\Delta\tau_{c}$: Time spend in handling state.
	- $p(t)$: Malignant Population of stroma at given time tick
	- $k_c$: Exhaustion gained per unit handling time
	- $k_p$: Exhaustion gained per unit malignant population
	- $k_l$: Recovery effect from time since last handling event
#### Simulation Rules
- **Number of Agents**: 1000
- **Agent Placement**: Agents are placed peripherally with uniform distribution on the border of the grid. 
- **Simulation Runtime**: 672 ticks (28 days)
#### Metrics of Interest
- **Global Efficacy Metrics**
	- Total Malignant Population ($P_{total}$): The total population of malignant cells in the microenvironment, per tick.
	- Total Kills ($K_{total}$): The total number of kills by the agents, per tick.
- **Agent Metrics**
	- Mean Population Exhaustion: The mean exhaustion variable for all agents per tick.
	- Terminal Exhaustion Count: The number of agents terminally exhausted per tick.
	- State Distribution Percentages: The percent of agent population spent in each state, per tick.
	- Kills per Agent, stratified by affinity: The number of kills of agent population, stratified by their receptor binding affinity, per tick.
#### Programming Framework
- **environment.py**
	- Defines microenvironment grid
	- Defines stromal densities for microenvironment grid
- **initial_state.py**
	- Initializes environment
	- Places agents in initial positions
- **agent.py**
	- Defines a CAR-T agent class, including all variables
- **behavior.py**
	- Executes behavioral logic of agent each tick, calculating behavior state probabilities
	- Updates dynamic variables ($\epsilon$)
	- Updates agent positions when necessary
- **simulation.py**
	- Defines time progression logic for 672 ticks
	- Applies agent variable updates, malignant population updates.
- **configuration.py**
	- Defines all relevant adjustable variables
- **experiment.py**
	- Run the simulation and records data, outputting relevant graphs.