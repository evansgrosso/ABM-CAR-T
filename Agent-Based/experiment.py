from pathlib import Path

import matplotlib
import numpy as np

from simulation import run

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = Path(__file__).resolve().parents[1] / "Simulation Results"


def run_and_collect_data():
    data = {
        "time": [],  # Current simulation tick
        "tumor_population": [],  # Total tumor cells at each tick
        "total_kills": [],  # Running total of successful kills
        "alive_agents": [],  # List of CAR T cells still alive
        "mean_exhaustion": [],  # Average exhaustion among living agents
        "searching_pct": [],  # Percent of living agents in searching state
        "handling_pct": [],  # Percent of living agents undergoing cytotoxic interaction
        "traversing_pct": [],  # Percent of living agents undergoing traversal
        "agent_results": {},  # Final affinity and kill count for each agent
    }
    total_kills = 0

    def record_step(t, env, agents, kills_this_tick):
        nonlocal total_kills
        total_kills += kills_this_tick

        alive_agents = []
        searching_count = 0
        handling_count = 0
        traversing_count = 0

        for agent in agents:
            data["agent_results"][id(agent)] = {
                "affinity": agent.affinity,
                "kills": agent.kills,
            }

            if agent.state == "dead":
                continue

            alive_agents.append(agent)

            if agent.state == "searching":
                searching_count += 1
            elif agent.state == "handling":
                handling_count += 1
            elif agent.state == "traversing":
                traversing_count += 1

        alive_count = len(alive_agents)

        if alive_count > 0:
            mean_exhaustion = np.mean(
                [agent.exhaustion for agent in alive_agents]
            )
            searching_pct = 100 * searching_count / alive_count
            handling_pct = 100 * handling_count / alive_count
            traversing_pct = 100 * traversing_count / alive_count
        else:
            mean_exhaustion = 0
            searching_pct = 0
            handling_pct = 0
            traversing_pct = 0

        data["time"].append(t)
        data["tumor_population"].append(np.sum(env.population_grid))
        data["total_kills"].append(total_kills)
        data["alive_agents"].append(alive_count)
        data["mean_exhaustion"].append(mean_exhaustion)
        data["searching_pct"].append(searching_pct)
        data["handling_pct"].append(handling_pct)
        data["traversing_pct"].append(traversing_pct)

    run(on_step=record_step)
    return data


def save_plot(filename):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(RESULTS_DIR / filename, dpi=300)
    plt.close()


def plot_population_and_kills(data):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    line1 = ax1.plot(
        data["time"],
        data["tumor_population"],
        linewidth=2,
        color="tab:red",
        label="Total malignant population",
    )

    line2 = ax2.plot(
        data["time"],
        data["total_kills"],
        linewidth=2,
        color="tab:blue",
        label="Cumulative kills",
    )

    ax1.set_ylabel("Malignant cells", color="tab:red")
    ax2.set_ylabel("Cumulative kills", color="tab:blue")

    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    ax1.legend(
        line1 + line2,
        ["Total malignant population", "Cumulative kills"],
    )

    ax2.spines["top"].set_visible(False)
    save_plot("population_and_kills.png")


def plot_agent_survival(data):
    plt.figure(figsize=(10, 5))
    plt.plot(
        data["time"],
        data["alive_agents"],
        linewidth=2,
    )
    plt.title("Agent Survival")
    plt.xlabel("Time (ticks)")
    plt.ylabel("Alive agents")
    plt.grid(True, alpha=0.25)
    save_plot("agent_survival.png")


def plot_mean_exhaustion(data):
    plt.figure(figsize=(10, 5))
    plt.plot(
        data["time"],
        data["mean_exhaustion"],
        linewidth=2,
    )
    plt.title("Mean Agent Exhaustion")
    plt.xlabel("Time (ticks)")
    plt.ylabel("Mean exhaustion")
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.25)
    save_plot("mean_exhaustion.png")


def plot_agent_state_mix(data):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.stackplot(
        data["time"],
        data["searching_pct"],
        data["handling_pct"],
        data["traversing_pct"],
        labels=["Searching", "Handling", "Traversing"],
        alpha=0.85,
    )

    ax.set_title("Agent State Mix")
    ax.set_xlabel("Time (ticks)")
    ax.set_ylabel("Alive agents (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", ncol=3, frameon=False)

    save_plot("agent_state_mix.png")


def plot_affinity_vs_kills(data):
    affinity = []
    kills = []

    for result in data["agent_results"].values():
        affinity.append(result["affinity"])
        kills.append(result["kills"])

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.scatter(
        affinity,
        kills,
        s=16,
        alpha=0.5,
    )

    if len(affinity) >= 2 and len(set(affinity)) > 1:
        slope, intercept = np.polyfit(affinity, kills, 1)

        x_values = np.linspace(
            min(affinity),
            max(affinity),
            100,
        )

        y_values = slope * x_values + intercept

        ax.plot(
            x_values,
            y_values,
            linewidth=2,
            color = "black",
        )

    ax.set_title("Affinity vs. Kills")
    ax.set_xlabel("Receptor binding affinity")
    ax.set_ylabel("Total kills")

    save_plot("affinity_vs_kills.png")


def make_all_plots():
    data = run_and_collect_data()

    plot_population_and_kills(data)
    plot_agent_survival(data)
    plot_mean_exhaustion(data)
    plot_agent_state_mix(data)
    plot_affinity_vs_kills(data)

    return data


if __name__ == "__main__":
    make_all_plots()