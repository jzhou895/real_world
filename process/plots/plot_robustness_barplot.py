import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt

pickles = sys.argv[1:]

# Plot formatting.
plt.rcParams["font.size"] = 16
colors = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "B85450", "#BF5700"]

# Make as many subplots as the number of pickles.
fig, ax = plt.subplots(1, len(pickles), figsize=(4 * len(pickles), 3))

plot_scheme = {}
metrics = ["avg", "p95", "util"]
schemes = ["orca", "c3"]

bar_width = 0.75
x = np.arange(len(metrics))

for i, pickle_file in enumerate(pickles):
    with open(pickle_file, "rb") as f:
        diff = pickle.load(f)

    for scheme in schemes:
        plot_scheme[scheme] = [diff[scheme][metric]*100 for metric in metrics]

    print(plot_scheme["orca"], plot_scheme["c3"])
    ax[i].bar(2 * x, plot_scheme["c3"], width=bar_width, label="C3", color=colors[-1], hatch="/")
    ax[i].bar(2 * x + bar_width, plot_scheme["orca"], width=bar_width, label="Orca", color=colors[0], hatch="+")

    ax[i].set_xticks(2 * x + bar_width / 2)
    ax[i].set_xticklabels([m.capitalize() for m in metrics])

    pickle_name = pickle_file.split("/")[-1].split(".")[0].split("_")[-1]
    ax[i].set_xlabel(pickle_name.capitalize())
    ax[i].yaxis.grid()
    if i == 0:
        ax[i].set_ylabel("Average %-age\nDifference")
        ax[i].set_yticks(np.arange(0, 9, 2))
    else:
        ax[i].set_yticks(np.arange(0, 25, 6))

plt.legend(loc="upper center", bbox_to_anchor=(-0.1, 1.3), ncol=2, frameon=False)
plt.subplots_adjust(top=0.85, bottom=0.2, left=0.1, right=0.98)
plt.savefig(f"robustness_bar.png")
plt.close()
