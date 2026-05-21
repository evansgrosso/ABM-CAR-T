import numpy as np
import matplotlib.pyplot as plt
from simulation import run

def main():
    ticks = []
    kills = []
    exhaustion = []
    alive_count = []

    pockets_acessed = []
    visited_pockets = set()

    def track(t, env, agents, kills_this_tick):
        ticks.append(t)
        kills.append(kills_this_tick)
        
        alive = [a for a in agents if a.state != "dead"]
        alive_count.append(len(alive))
        
        if alive:
            exhaustion.append(np.mean([a.exhaustion for a in alive]))
        else:
            exhaustion.append(0)

        for a in alive:
            visited_pockets.add(a.position)

        pockets_acessed.append(len(visited_pockets))
            

    run(on_step=track)

    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    
    axs[0].plot(ticks, kills, color='red')
    axs[0].set_ylabel('Kills / Tick')
    axs[0].set_title('Simulation Metrics') 

    axs[1].plot(ticks, alive_count, color='blue')
    axs[1].set_ylabel('Alive Agents')

    axs[2].plot(ticks, exhaustion, color='green')
    axs[2].set_ylabel('Average Exhaustion')
    axs[2].set_xlabel('Time (ticks)')

    axs[3].plot(ticks, pockets_acessed, color='purple')
    axs[3].set_ylabel('Pockets Accessed')
    axs[3].set_xlabel('Time (ticks)')

    plt.savefig("sim_metrics.png")

    #TODO: Add project relevant visualizations. Spatial penetration.

if __name__ == "__main__":
    main()