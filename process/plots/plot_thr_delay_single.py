"""
Read the log files and plot throughput vs delay.
"""

import sys
import matplotlib.pyplot as plt
from utils import *

files = sys.argv[1:]

# Plot formatting
plt.rcParams["font.size"] = 14

colors = ["#82B366", "#D79B00", "#B85450", "#6C8EBF", "#9673A6", "#D6B656"]
markers = ["o", "P", "^", "s", "v", "^"]
styles = ["-", "--", "-.", ":", "-", "--"]

# Read the sum files.
for index, file in enumerate(files):
    util, avg, p95 = read_sum_file(file)

    label = file.split("/")[-1].split("-")[1]
    label = label.replace("_", " ")    
    label = " ".join([word.capitalize() for word in label.split(' ')])

    # Add a marker at (avg, util)
    plt.plot(
        avg,
        util,
        label=label,
        color=colors[index],
        marker=markers[index],
        linestyle=styles[index],
        markersize=10,
    )

    # Draw a line from (avg, util) to (p95, util)
    plt.plot(
        [avg, p95],
        [util, util],
        color=colors[index],
        linestyle=styles[index],
        linewidth=2,
    )


plt.ylim(90, 101)
plt.xlabel("Average Delay (ms)")
plt.ylabel("Utilization (%)")
plt.grid()
plt.legend()
plt.savefig("thr_delay_single.png", bbox_inches="tight")
