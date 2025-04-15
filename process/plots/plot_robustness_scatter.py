import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt

pickles = sys.argv[1:]

# Plot formatting.
plt.rcParams["font.size"] = 16
colors = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "B85450", "#BF5700"]

# Make as many subplots as the number of pickles.
fig, ax = plt.subplots(1, len(pickles), figsize=(4 * len(pickles), 3.2))

plot_scheme = {}
metrics = ["avg", "p95", "util"]
labels = ["Avg", "p95", "% Util"]
schemes = ["orca", "c3"]

bar_width = 0.5
x = np.arange(len(metrics))

for i, pickle_file in enumerate(pickles):
    with open(pickle_file, "rb") as f:
        diff = pickle.load(f)

    for scheme in schemes:
        # diff[scheme][metric] is an array of differences for each metric.
        plot_scheme[scheme] = [np.array(diff[scheme][metric])*100 for metric in metrics]

    # Add a scatter plot for each metric at x.
    for x_i in x:
        # for data_point in plot_scheme["orca"][x_i]:
        ax[i].scatter(
            [2 * x_i] * len(plot_scheme["orca"][x_i]),
            plot_scheme["orca"][x_i],
            color=colors[0],
            marker="o",
            s=100,
            alpha=0.6
        )
        # for data_point in plot_scheme["c3"][x_i]:
        ax[i].scatter(
            [2 * x_i + bar_width] * len(plot_scheme["c3"][x_i]),
            plot_scheme["c3"][x_i],
            color=colors[-1],
            marker="P",
            s=100,
            alpha=0.6
        )

    ax[i].set_xticks(2 * x + bar_width / 2)
    ax[i].set_xticklabels(labels)

    pickle_name = pickle_file.split("/")[-1].split(".")[0].split("_")[-1]
    ax[i].set_xlabel(pickle_name.capitalize())
    ax[i].yaxis.grid()
    if i == 0:
        ax[i].set_ylabel("Percent Difference")
        ax[i].set_yticks(np.arange(-30, 22, 10))
    else:
        ax[i].set_yticks(np.arange(-40, 11, 10))

# Add legend patch.
orca_patch = plt.plot([], [], marker="o", markersize=15, ls="", color=colors[0], label="Orca", alpha=0.8)[0]
c3_patch = plt.plot([], [], marker="P", markersize=15, ls="", color=colors[-1], label="C3", alpha=0.8)[0]

plt.legend(handles=[orca_patch, c3_patch], loc="upper center", bbox_to_anchor=(-0.1, 1.25), ncol=2, frameon=False)
plt.subplots_adjust(top=0.85, bottom=0.18, left=0.12, right=0.98)
plt.savefig(f"robustness_scatter.png")
plt.close()