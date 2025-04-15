"""
Read the log files and plot throughput vs delay.
"""

import os
import re
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import *

trace_family = sys.argv[1]  # Can be one of {stable, synthetic, real, all}
noise = sys.argv[2]  # Can be one of {0.05, 0.1}
directories = sys.argv[3:]

traces_to_plot = {
    "stable": ["wired"],
    "synthetic": ["bump", "sawtooth", "mountain"],
    "real": ["ATT", "Verizon", "TMobile", "step"],
    "all": ["bump", "sawtooth", "mountain", "ATT", "Verizon", "TMobile", "step"],
}

# Plot formatting
plt.rcParams["font.size"] = 16
plt.figure(figsize=(6, 4))

colors = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "B85450", "#BF5700"]
# colors = ["#82B366", "#6C8EBF", "#B85450", "#D79B00", "#BF5700", "#BF5700"]
markers = ["o", "P", "^", "s", "p", "D", "v"]
styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 10)), (0, (5, 1))]

avg = {}
p95 = {}
util = {}
schemes = ["orca", "c3"]
for scheme in schemes:
    avg[scheme] = {"baseline": {}, "noise": {}}
    p95[scheme] = {"baseline": {}, "noise": {}}
    util[scheme] = {"baseline": {}, "noise": {}}

# Read the sum files.
for index, directory in enumerate(directories):
    if "c3" in directory:
        scheme = "c3"
    elif re.search(r'v\d+', directory):
        scheme = "orca"
    else:
        print(f"Unknown scheme in {directory}")
        continue

    # Iterate through directories in the given directory -- these store results from the SUM-* files.
    for run_dir in os.listdir(directory):
        for dir in os.listdir(f"{directory}/{run_dir}"):
            # Check if the directory is a relevant trace family.
            for t in traces_to_plot[trace_family]:
                if t in dir:
                    for file in os.listdir(f"{directory}/{run_dir}/{dir}"):
                        # Read only the SUM files.
                        if "SUM" in file:
                            trace_util, trace_avg, trace_p95 = read_sum_file(
                                f"{directory}/{run_dir}/{dir}/{file}"
                            )

                            # Check whether to save in the noise dictionary.
                            file_type = "baseline"
                            if noise in file:
                                file_type = "noise"
                            elif "uniform" in file.lower():
                                # Some other noise configuration -- skip.
                                continue

                            if dir not in avg[scheme][file_type]:
                                avg[scheme][file_type][dir] = [trace_avg]
                                p95[scheme][file_type][dir] = [trace_p95]
                                util[scheme][file_type][dir] = [trace_util]
                            else:
                                avg[scheme][file_type][dir].append(trace_avg)
                                p95[scheme][file_type][dir].append(trace_p95)
                                util[scheme][file_type][dir].append(trace_util)

# Create a dictionary to make a bar plot later.
# The bar plot will show the average absolute difference in avg, p95, and util between baseline and noise.
diff = {}

# Calculate the average values and make the plot.
index = 0
for scheme in schemes:
    diff[scheme] = {"avg": 0, "p95": 0, "util": 0}

    # Compute the per-dir average values.
    for file_type in ["baseline", "noise"]:
        for trace in avg[scheme][file_type].keys():
            avg[scheme][file_type][trace] = np.mean(avg[scheme][file_type][trace])
            p95[scheme][file_type][trace] = np.mean(p95[scheme][file_type][trace])
            util[scheme][file_type][trace] = np.mean(util[scheme][file_type][trace])

    # First get for baseline.
    print(scheme, len(avg[scheme]["baseline"].keys()))
    baseline_avg = np.mean(list(avg[scheme]["baseline"].values()))
    baseline_p95 = np.mean(list(p95[scheme]["baseline"].values()))
    baseline_util = np.mean(list(util[scheme]["baseline"].values()))
    baseline_label = scheme.capitalize()
    print(baseline_avg, baseline_util)

    # Then get for noise.
    noise_avg = np.mean(list(avg[scheme]["noise"].values()))
    noise_p95 = np.mean(list(p95[scheme]["noise"].values()))
    noise_util = np.mean(list(util[scheme]["noise"].values()))
    noise_label = f"{scheme.capitalize()} under noise"
    print(noise_avg, noise_util)

    style_id = 0 if scheme == "orca" else -1

    # Plot the baseline values -- color and marker based on scheme, and line style fixed 0.
    # Add a marker at (avg, util)
    plt.plot(
        baseline_avg,
        baseline_util,
        label=baseline_label,
        color=colors[style_id],
        marker=markers[style_id],
        linestyle=styles[0],
        markersize=15,
    )

    # Draw a line from (avg, util) to (p95, util)
    plt.plot(
        [baseline_avg, baseline_p95],
        [baseline_util, baseline_util],
        color=colors[style_id],
        linestyle=styles[0],
        linewidth=3,
    )

    # Plot the noise values -- color and marker based on scheme, and line style fixed 1.
    # Add a marker at (avg, util)
    plt.plot(
        noise_avg,
        noise_util,
        label=noise_label,
        color=colors[style_id],
        marker=markers[style_id],
        linestyle=styles[1],
        markersize=15,
    )

    # Draw a line from (avg, util) to (p95, util)
    plt.plot(
        [noise_avg, noise_p95],
        [noise_util, noise_util],
        color=colors[style_id],
        linestyle=styles[1],
        linewidth=3,
    )

    # Compute the per trace absolute difference between baseline and noise.
    count = 0
    total_diff_util = []
    total_diff_avg = []
    total_diff_p95 = []
    for trace in avg[scheme]["baseline"].keys():
        baseline_util = util[scheme]["baseline"][trace]
        noise_util = util[scheme]["noise"][trace]
        total_diff_util.append((noise_util - baseline_util)/baseline_util)
        
        baseline_avg = avg[scheme]["baseline"][trace]
        noise_avg = avg[scheme]["noise"][trace]
        total_diff_avg.append((noise_avg - baseline_avg)/baseline_avg)

        baseline_p95 = p95[scheme]["baseline"][trace]
        noise_p95 = p95[scheme]["noise"][trace]
        total_diff_p95.append((noise_p95 - baseline_p95)/baseline_p95)

        count += 1

    # print(scheme)
    # print(f"Average difference in util: {total_diff_util/count}")
    # print(f"Average difference in avg: {total_diff_avg/count}")
    # print(f"Average difference in p95: {total_diff_p95/count}")

    diff[scheme]["avg"] = total_diff_avg
    diff[scheme]["p95"] = total_diff_p95
    diff[scheme]["util"] = total_diff_util

    index += 1

plt.ylim(60, 101)
plt.xlabel("Average Queueing Delay (ms)", fontsize=20)
plt.ylabel("Utilization (%)", fontsize=20)
plt.grid()
plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.35), ncol=2, columnspacing=0.5, frameon=False)
plt.subplots_adjust(top=0.8, bottom=0.18, left=0.15, right=0.95)
plt.savefig(f"robustness_{trace_family}.png")
plt.close()

print(diff)

# Write diff to a pickle file
with open(f"robustness_{trace_family}.pkl", "wb") as f:
    pickle.dump(diff, f)
