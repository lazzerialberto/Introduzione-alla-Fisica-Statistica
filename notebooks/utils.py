import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation
import copy

plt.rcParams["animation.html"] = "jshtml"

def plot_patterns(patterns: dict):
    """A function to plot patterns stored in a dictionary, on a grid.
    Args:
        • patterns (dict): a dictionary of patterns
    Returns:
        • fig, axs (tuple): a tuple of the figure and axes objects
    """
    # just calculate the grid shape
    N = patterns.__len__()  # number of patterns
    grid_size = max(i for i in range(1, int(np.sqrt(N) + 1)) if N % i == 0)
    grid_shape = [grid_size, int(N / grid_size)]
    grid_shape.sort()
    grid_shape = tuple(grid_shape)  # calculates the grid shape
    # plots the patterns onto the grid
    fig, axs = plt.subplots(
        grid_shape[0], grid_shape[1], figsize=(2 * grid_shape[1], 2 * grid_shape[0])
    )
    axs = axs.reshape(tuple(grid_shape))
    for i in range(grid_shape[0]):
        for j in range(grid_shape[1]):
            name = list(patterns.keys())[i * grid_shape[1] + j]
            pattern = patterns[name]
            im = axs[i, j].imshow(pattern, cmap="Greys_r")
            im.axes.get_xaxis().set_visible(False)
            im.axes.get_yaxis().set_visible(False)
            axs[i, j].set_title(name)
    # makes a colorbar
    fig.colorbar(im, ax=axs.ravel().tolist(), shrink=0.95)
    return fig, axs


def visualise_hopfield_network(
    HopfieldNetwork, steps_back=0, fig=None, ax=None, title=None
):
    """Displays the state of the Hopfield network and a bar chart of similarites to all the stored patterns.
    Args:
        • HopfieldNetwork (HopfieldNetwork): the Hopfield network class storing the data to visualise
        • steps_back (int, optional): the number of steps back in the history to visualise. Defaults to 0 i.e. current state.
        • fig, ax: option fig and ax objects to plot onto. If None, new ones are created.
        • title (str, optional): the title of the figure. Defaults to None.
    """

    """Get the data to plot"""
    state = HopfieldNetwork.history["state"][-steps_back - 1]
    similarities = HopfieldNetwork.history["similarities"][-steps_back - 1]
    pattern_names = HopfieldNetwork.pattern_names
    pattern_shape = HopfieldNetwork.pattern_shape
    N_patterns = HopfieldNetwork.N_patterns

    """Create figure"""
    if ax is None:
        fig = plt.figure(figsize=(16, 4))
        ax0 = fig.add_axes([0, 0.02, 1 / 2, 0.88])
        ax1 = fig.add_axes([1 / 2, 1 / 3, 0.95 / 2, 0.9 - 1 / 3])
        ax = np.array([ax0, ax1])

    """Displays the state of the Hopfield network"""
    im = ax[0].imshow(state.reshape(pattern_shape), cmap="Greys_r")

    ax[0].set_title(title or "Network activity pattern", fontweight="bold")
    im.axes.get_xaxis().set_visible(False)
    im.axes.get_yaxis().set_visible(False)

    """Displays the similarity of the Hopfield network state  """
    ax[1].set_title("Similarity to stored patterns")
    bars = ax[1].bar(np.arange(N_patterns), similarities)
    best_pattern_id = np.argmax(np.abs(similarities))
    best_pattern = HopfieldNetwork.patterns_dict[
        HopfieldNetwork.pattern_names[best_pattern_id]
    ]
    ax[1].set_xticks(np.arange(N_patterns))
    ax[1].set_xticklabels(pattern_names)
    ax[1].tick_params(axis="x", labelrotation=60)
    ax[1].axhline(0, color="black", lw=1)
    colors = ["C0"] * N_patterns
    colors[best_pattern_id] = "blue"
    ax[1].tick_params(axis="x", which="major", pad=2)
    ax[1].set_ylim(top=1, bottom=-1)
    for i, (bar, tick) in enumerate(zip(bars, ax[1].get_xticklabels())):
        bar.set_facecolor(colors[i])
        tick.set_ha("right")
        if i == best_pattern_id:
            tick.set_color("blue")

    """Display a small inset of the "best pattern" in the similarity bar chart"""
    width = HopfieldNetwork.N_patterns / 10
    inset_ax = ax[1].inset_axes(
        [best_pattern_id + 0.5, 0.5 - (1 - similarities[best_pattern_id]), width, 0.4],
        transform=ax[1].transData,
    )
    best_pattern = HopfieldNetwork.patterns_dict[
        HopfieldNetwork.pattern_names[best_pattern_id]
    ]
    inset_ax.imshow(best_pattern, cmap="Greys_r")
    plt.setp(inset_ax, xticks=[], yticks=[])
    for spine in list(inset_ax.spines.keys()):
        inset_ax.spines[spine].set_color("blue")
        inset_ax.spines[spine].set_linewidth(2)

    return fig, ax

def plot_energy(HopfieldNetwork, n_steps=None):
    """Plots the energy of the Hopfield network over time"""
    fig, ax = plt.subplots(figsize=(5, 5))
    print("n_steps:", n_steps)
    if n_steps is None:
        n_steps = len(HopfieldNetwork.history["energy"]) - 2
        print("n_steps:", n_steps)
    energy = HopfieldNetwork.history["energy"][-n_steps - 1 :]
    t = np.arange(-n_steps - 1, 0)
    ax.scatter(t, energy, c=t, cmap="viridis", alpha=0.5)
    ax.plot(t, energy, c="k", lw=0.5, linestyle="-", zorder=0)
    ax.set_xlabel("Step")
    ax.set_ylabel("Energy")
    ax.set_ylim(bottom=min(energy) - 5, top=max(energy) + 5)
    ax.set_xticks([-n_steps - 1, 0])
    ax.set_xticklabels([f"-{n_steps}", "0"])
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    y_range = np.ptp(ax.get_ylim())
    first_inset_ax = ax.inset_axes(
        [
            -n_steps - 1 + 0.05 * n_steps,
            energy[0] + 0.05 * y_range,
            0.2 * n_steps,
            0.2 * y_range,
        ],
        transform=ax.transData,
    )
    first_inset_ax.imshow(
        HopfieldNetwork.history["state"][-n_steps - 1].reshape(
            HopfieldNetwork.pattern_shape
        ),
        cmap="Greys_r",
    )
    plt.setp(first_inset_ax, xticks=[], yticks=[])
    for spine in list(first_inset_ax.spines.keys()):
        first_inset_ax.spines[spine].set_color(matplotlib.colormaps["viridis"](0))
        first_inset_ax.spines[spine].set_linewidth(2.5)

    count = np.argmin(np.abs(np.array(energy) - (max(energy) - np.ptp(energy) / 3)))
    if count == 0:
        count = int(n_steps / 3)
    second_inset_ax = ax.inset_axes(
        [
            -n_steps - 1 + count + 0.05 * n_steps,
            energy[count] + 0.05 * y_range,
            0.2 * n_steps,
            0.2 * y_range,
        ],
        transform=ax.transData,
    )
    second_inset_ax.imshow(
        HopfieldNetwork.history["state"][-n_steps - 1 + count].reshape(
            HopfieldNetwork.pattern_shape
        ),
        cmap="Greys_r",
    )
    plt.setp(second_inset_ax, xticks=[], yticks=[])
    for spine in list(second_inset_ax.spines.keys()):
        second_inset_ax.spines[spine].set_color(
            matplotlib.colormaps["viridis"](count / n_steps)
        )
        second_inset_ax.spines[spine].set_linewidth(2.5)

    count = np.argmin(np.abs(np.array(energy) - (max(energy) - 2 * np.ptp(energy) / 3)))
    if count == 0:
        count = int(2 * n_steps / 3)
    third_inset_ax = ax.inset_axes(
        [
            -n_steps - 1 + count + 0.05 * n_steps,
            energy[count] + 0.05 * y_range,
            0.2 * n_steps,
            0.2 * y_range,
        ],
        transform=ax.transData,
    )
    third_inset_ax.imshow(
        HopfieldNetwork.history["state"][-n_steps - 1 + count].reshape(
            HopfieldNetwork.pattern_shape
        ),
        cmap="Greys_r",
    )
    plt.setp(third_inset_ax, xticks=[], yticks=[])
    for spine in list(third_inset_ax.spines.keys()):
        third_inset_ax.spines[spine].set_color(
            matplotlib.colormaps["viridis"](count / n_steps)
        )
        third_inset_ax.spines[spine].set_linewidth(2.5)

    last_inset_ax = ax.inset_axes(
        [0 + 0.05 * n_steps, energy[-1] + 0.05 * y_range, 0.2 * n_steps, 0.2 * y_range],
        transform=ax.transData,
    )
    last_inset_ax.imshow(
        HopfieldNetwork.history["state"][-1].reshape(HopfieldNetwork.pattern_shape),
        cmap="Greys_r",
    )
    plt.setp(last_inset_ax, xticks=[], yticks=[])
    for spine in list(last_inset_ax.spines.keys()):
        last_inset_ax.spines[spine].set_color(matplotlib.colormaps["viridis"](0.9999))
        last_inset_ax.spines[spine].set_linewidth(2.5)
    return fig, ax


def animate_hopfield_network(
    HopfieldNetwork, n_steps=10, fps=10, animation_length_secs=5
):
    """Makes an animation of the last n states (drawn from the history) of the Hopfield network
    Args:
        • HopfieldNetwork (HopfieldNetwork): the Hopfield network class storing the data to animate
        • n_steps (int, optional): _description_. Defaults to 10.
    """

    n_frames = int(animation_length_secs * fps)
    steps_back_to_plot = np.linspace(0, n_steps, n_frames, dtype=int)

    fig, ax = HopfieldNetwork.visualise()

    def animate(i, fig, ax):
        """The function that is called at each step of the animation.
        This just clears the axes and revisualises teh state of the network at the next step.
        """
        ax[0].clear()
        ax[1].clear()
        steps_back = n_steps - steps_back_to_plot[i]
        fig, ax = HopfieldNetwork.visualise(steps_back=steps_back, fig=fig, ax=ax)
        fig.suptitle("Step %d" % steps_back_to_plot[i])
        # fig.set_tight_layout(True)
        plt.close()

    anim = matplotlib.animation.FuncAnimation(
        fig, animate, fargs=(fig, ax), frames=n_frames, interval=1000 / fps, blit=False
    )
    return anim


def mask_pattern(pattern):
    """Masks all but the top left hand corner of a pattern"""
    mask = np.zeros_like(pattern)
    mask[: pattern.shape[0] // 2, : pattern.shape[1] // 2] = 1
    return pattern * mask


def merge_patterns(pattern1, pattern2):
    """Merges two patterns together by taking the left half of pattern1 and the right half of pattern2"""
    pattern1 = copy.deepcopy(pattern1)
    pattern2 = copy.deepcopy(pattern2)
    pattern1[:, pattern1.shape[1] // 2 :] = 0
    pattern2[:, : pattern2.shape[1] // 2] = 0
    return pattern1 + pattern2
