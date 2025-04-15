"""
Read the log files and plot throughput vs delay.
"""

import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from utils import *

trace_family = sys.argv[1]  # Can be one of {stable, synthetic, real}
directories = sys.argv[2:]

traces_to_plot = {
    "stable": ["wired"],
    "synthetic": ["bump", "sawtooth", "mountain"],
    "real": ["ATT", "Verizon", "TMobile", "step"],
    "all": ["bump", "sawtooth", "mountain", "ATT", "Verizon", "TMobile", "step"]
}

# Plotting hyperparameters
NUM_RUNS = 4
NUM_TCP_RUNS = 3

# Plot formatting
plt.rcParams["font.size"] = 20
plt.figure(figsize=(6, 4))

# # Use below for sensitivity plot
# plt.figure(figsize=(8, 4))

colors = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "#B85450", "#BF5700"]
# colors = ["#82B366", "#6C8EBF", "#B85450", "#D79B00", "#BF5700", "#BF5700"]
markers = ["o", "P", "^", "s", "p", "d", "v"]
styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (2, 1)), (0, (5, 1))]

# Construct arrays for analysis of utilization and delay (w.r.t the last scheme)
scheme_utils = []
scheme_delays = []
scheme_delays_p95 = []

# Read the sum files.
for index, directory in enumerate(directories):
    # If directory has 'v{version}' in its name or 'c3' -- then it is a learned CC.
    learned_cc = True # if ('c3' in directory or re.search(r'v\d+', directory)) else False
    
    count = 0
    file_count = 0
    utilizations = []

    avg = 0
    p95 = 0
    util = 0

    util_25p = 0
    util_75p = 0

    total_drops = 0

    runs = NUM_RUNS if learned_cc else NUM_TCP_RUNS
    print(f"{index} {directory}")
    for run in range(runs):
        # Read all files in directory/run{run} and choose the one which has trace in its name.
        run_avg = 0
        run_p95 = 0 
        run_util = 0 
        run_count = 0

        for file in os.listdir(f"{directory}/run{run}"):
            # Only consider trimmed files if it is a learned_cc -- as we need to trim the last 60s.
            if learned_cc and "trimmed" not in file:
                continue

            # First replace wired192-10 in order to avoid confusion with the downlink wired.
            check_name = file.replace("wired192-10", "uplink-delay")
            to_plot = any([t in check_name for t in traces_to_plot[trace_family]])
            
            # Check if any of the terms from traces_to_plot[trace_family] is in the file name.
            if not to_plot:
                continue

            if "sum" in file:
                trace_util, trace_avg, trace_p95 = read_sum_file(f"{directory}/run{run}/{file}")
                # if trace_util == 0:
                #     print(f"Trace not long enough. Skipping {file}")
                #     continue

                avg += trace_avg
                p95 += trace_p95
                util += trace_util
                count += 1
                file_count += 1

                run_avg += trace_avg
                run_p95 += trace_p95
                run_util += trace_util
                run_count += 1
        
        run_avg /= run_count
        run_p95 /= run_count
        run_util /= run_count

        print(f"\tRun #{run}: avg={run_avg}, util={run_util}:")

    if "/proj/verifiedmlsys-PG0/sigcomm_results/new_result_dir" in directory:
        label = os.path.relpath(directory, start="/proj/verifiedmlsys-PG0/sigcomm_results/new_result_dir")
    
    elif learned_cc:
        # Get the label from the directory name.
        label = directory.split("/")[-2].split("_")[0]
        if "c3" not in label:
            if "session1" in directory:
                label = "Orca"
            else:
                label = "Orca 250k"
        else:
            if "sensitivity" not in directory:
                label = label.replace("c3", "C3")
                # label = label.replace("c3", "N5 $\lambda$0.25")
            else:
                sensitivity_type = directory.split("/")[-3].split("_")[-1]
                if sensitivity_type == "ksc":
                    label_index = 1
                elif sensitivity_type == "lambda":
                    label_index = 3
                label = directory.split("/")[-2].split("_")[label_index]
                if sensitivity_type == "ksc":
                    label = label.replace("k", "N") + " $\lambda$0.25"
                elif sensitivity_type == "lambda":
                    label = "N5 " + label.replace("lambda", "$\lambda$")
    else:
        # Get the label from the file name.
        label = file.split("/")[-1].split("-")[1]
        label = label.replace("_", " ")    
        label = " ".join([word.capitalize() for word in label.split(' ')])

        if "tcp" in label.lower():
            label = label.split(' ')[1]
        if "bbr" in label.lower():
            label = label.replace("Bbr", "BBR")

    avg /= count
    p95 /= count
    util /= count
    scheme_delays.append(avg)
    scheme_delays_p95.append(p95)
    scheme_utils.append(util)

    print("heyo", avg, p95, util)
    style_id = -1 if ("c3" in label.lower() and "sensitivity" not in directory) else index

    # Add a marker at (avg, util)
    plt.plot(
        avg,
        util,
        label=label,
        color=colors[style_id % len(colors)],
        marker=markers[style_id % len(markers)],
        linestyle=styles[style_id % len(styles)],
        markersize=16,
    )

    # Draw a line from (avg, util) to (p95, util)
    plt.plot(
        [avg, p95],
        [util, util],
        color=colors[style_id%len(colors)],
        linestyle=styles[style_id%len(styles)],
        linewidth=4,
    )

    # if ERROR_BARS:
    #     plt.errorbar(
    #         avg,
    #         util,
    #         yerr=[[util-util_25p], [util_75p-util]],
    #         fmt="o",
    #         color=colors[index],
    #         markersize=12,
    #         linestyle=styles[index],
    #     )

# Print the relative delays and utilizations (w.r.t the last scheme)
relative_delays = [(1 - delay / scheme_delays[0]) for delay in scheme_delays]
relative_utils = [scheme_utils[0] - util for util in scheme_utils]
relative_delays_p95 = [(1 - delay / scheme_delays_p95[0]) for delay in scheme_delays_p95]

np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
print("Avg delays:", relative_delays)
print("p95 delays:", relative_delays_p95)
print("Util:", relative_utils)
print("count:", count)

# plt.ylim(80, 101)
# plt.gca().invert_xaxis()
# plt.xscale("log")
plt.xlabel("Average Queueing Delay (ms)", fontsize=24)
plt.ylabel("Utilization (%)", fontsize=24)
plt.grid()

plt.legend(loc="lower right", ncol=1, columnspacing=0.5, bbox_to_anchor=(1.2, -1.5))
# plt.subplots_adjust(top=0.95, bottom=0.21, left=0.18, right=0.98)

# # Use below for sensitivity plot
# plt.legend(loc="center right", bbox_to_anchor=(1.62, 0.5), ncol=1, columnspacing=0.5)
# plt.subplots_adjust(top=0.95, bottom=0.2, left=0.15, right=0.68)

plt.savefig(f"thr_delay_{trace_family}.png", bbox_inches="tight")
