import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from simulation import run


COLORS = {
    "malignant": "#1f77b4",
    "kills": "#d62728",
    "agents": "#9467bd",
    "exhaustion": "#2ca02c",
    "endpoint": "#333333",
    "searching": "#4c78a8",
    "handling": "#f58518",
    "traversing": "#54a24b",
}


def new_history():
    return {
        "time": [],
        "total_malignant_population": [],
        "total_kills": [],
        "mean_exhaustion": [],
        "alive_agents": [],
        "dead_agents": [],
        "searching_count": [],
        "handling_count": [],
        "traversing_count": [],
        "searching_pct": [],
        "handling_pct": [],
        "traversing_pct": [],
        "agent_endpoints": {},
    }


def collect_simulation_history():
    """Run the simulation once and collect reusable time-series data."""
    history = new_history()
    cumulative_kills = 0
    initial_agent_count = None

    def track(t, env, agents, kills_this_tick):
        nonlocal cumulative_kills, initial_agent_count

        if initial_agent_count is None:
            initial_agent_count = len(agents)
        cumulative_kills += kills_this_tick

        alive_agents = [agent for agent in agents if agent.state != "dead"]
        alive_count = len(alive_agents)
        dead_count = initial_agent_count - alive_count

        state_counts = {
            "searching": 0,
            "handling": 0,
            "traversing": 0,
        }
        for agent in alive_agents:
            if agent.state in state_counts:
                state_counts[agent.state] += 1

        for agent in agents:
            agent_id = id(agent)
            endpoint = history["agent_endpoints"].setdefault(
                agent_id,
                {
                    "affinity": agent.affinity,
                    "total_kills": 0,
                    "terminal_exhaustion_tick": None,
                },
            )
            endpoint["total_kills"] = agent.kills
            if agent.exhaustion >= 1 and endpoint["terminal_exhaustion_tick"] is None:
                endpoint["terminal_exhaustion_tick"] = t

        if alive_count:
            mean_exhaustion = np.mean([agent.exhaustion for agent in alive_agents])
            searching_pct = 100 * state_counts["searching"] / alive_count
            handling_pct = 100 * state_counts["handling"] / alive_count
            traversing_pct = 100 * state_counts["traversing"] / alive_count
        else:
            mean_exhaustion = np.nan
            searching_pct = 0
            handling_pct = 0
            traversing_pct = 0

        history["time"].append(t)
        history["total_malignant_population"].append(np.sum(env.population_grid))
        history["total_kills"].append(cumulative_kills)
        history["mean_exhaustion"].append(mean_exhaustion)
        history["alive_agents"].append(alive_count)
        history["dead_agents"].append(dead_count)
        history["searching_count"].append(state_counts["searching"])
        history["handling_count"].append(state_counts["handling"])
        history["traversing_count"].append(state_counts["traversing"])
        history["searching_pct"].append(searching_pct)
        history["handling_pct"].append(handling_pct)
        history["traversing_pct"].append(traversing_pct)

    run(on_step=track)
    return history


def style_axis(ax):
    ax.grid(True, alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_figure(fig, output_path):
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_regression(ax, x, y, line_color):
    if len(x) >= 2 and len(set(x)) > 1:
        sns.regplot(
            x=x,
            y=y,
            ax=ax,
            scatter_kws={"s": 18, "alpha": 0.55, "color": COLORS["endpoint"]},
            line_kws={"color": line_color, "linewidth": 2},
            ci=None,
        )
    else:
        sns.scatterplot(
            x=x,
            y=y,
            ax=ax,
            s=18,
            alpha=0.55,
            color=COLORS["endpoint"],
        )
        ax.text(
            0.5,
            0.5,
            "Regression unavailable",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )


def plot_macroscopic_timeseries(history, output_path="timeseries_macroscopic.png"):
    """Save malignant burden, kills, exhaustion, and agent state summaries."""
    time = history["time"]

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(10, 12),
        sharex=True,
        constrained_layout=True,
    )

    ax_pop = axes[0]
    ax_kills = ax_pop.twinx()
    pop_line = ax_pop.plot(
        time,
        history["total_malignant_population"],
        color=COLORS["malignant"],
        linewidth=2,
        label="Total malignant population",
    )
    kill_line = ax_kills.plot(
        time,
        history["total_kills"],
        color=COLORS["kills"],
        linewidth=2,
        label="Total kills",
    )
    ax_pop.set_ylabel("Malignant cells", color=COLORS["malignant"])
    ax_kills.set_ylabel("Cumulative kills", color=COLORS["kills"])
    ax_pop.tick_params(axis="y", labelcolor=COLORS["malignant"])
    ax_kills.tick_params(axis="y", labelcolor=COLORS["kills"])
    ax_pop.legend(pop_line + kill_line, [line.get_label() for line in pop_line + kill_line], loc="best")

    axes[1].plot(
        time,
        history["alive_agents"],
        color=COLORS["agents"],
        linewidth=2,
    )
    axes[1].set_ylabel("Alive agents")
    axes[1].set_ylim(bottom=0)

    axes[2].plot(
        time,
        history["mean_exhaustion"],
        color=COLORS["exhaustion"],
        linewidth=2,
    )
    axes[2].set_ylabel("Mean exhaustion")
    axes[2].set_ylim(0, 1)

    axes[3].stackplot(
        time,
        history["searching_pct"],
        history["handling_pct"],
        history["traversing_pct"],
        labels=["Searching", "Handling", "Traversal"],
        colors=[COLORS["searching"], COLORS["handling"], COLORS["traversing"]],
        alpha=0.85,
    )
    axes[3].set_ylabel("Agent state (%)")
    axes[3].set_xlabel("Time (ticks)")
    axes[3].set_ylim(0, 100)
    axes[3].legend(loc="upper right", ncol=3, frameon=False)

    for ax in axes:
        style_axis(ax)

    ax_kills.spines["top"].set_visible(False)

    fig.suptitle("Macroscopic Simulation Dynamics", fontsize=14)
    save_figure(fig, output_path)


def plot_agent_endpoint_analysis(history, output_path="agent_endpoint_analysis.png"):
    """Save endpoint relationships between affinity, kills, and exhaustion time."""
    endpoints = list(history["agent_endpoints"].values())
    affinity = [endpoint["affinity"] for endpoint in endpoints]
    kills = [endpoint["total_kills"] for endpoint in endpoints]
    exhausted = [
        endpoint
        for endpoint in endpoints
        if endpoint["terminal_exhaustion_tick"] is not None
    ]

    sns.set_theme(style="whitegrid", context="paper")
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5),
        constrained_layout=True,
    )

    plot_regression(axes[0], affinity, kills, COLORS["kills"])
    axes[0].set_title("Affinity vs. Efficacy")
    axes[0].set_xlabel("Receptor binding affinity (alpha)")
    axes[0].set_ylabel("Total kills")

    exhausted_affinity = [endpoint["affinity"] for endpoint in exhausted]
    exhaustion_tick = [endpoint["terminal_exhaustion_tick"] for endpoint in exhausted]
    plot_regression(axes[1], exhausted_affinity, exhaustion_tick, COLORS["exhaustion"])
    axes[1].set_title("Affinity vs. Survivability")
    axes[1].set_xlabel("Receptor binding affinity (alpha)")
    axes[1].set_ylabel("Terminal exhaustion tick")

    for ax in axes:
        style_axis(ax)

    fig.suptitle("Agent Endpoint Analysis", fontsize=14)
    save_figure(fig, output_path)


DEFAULT_PLOTTERS = (
    plot_macroscopic_timeseries,
    plot_agent_endpoint_analysis,
)


def generate_visualizations(history=None, plotters=DEFAULT_PLOTTERS):
    """Generate all experiment plots from one simulation history."""
    if history is None:
        history = collect_simulation_history()

    for plotter in plotters:
        plotter(history)

    return history


if __name__ == "__main__":
    generate_visualizations()
