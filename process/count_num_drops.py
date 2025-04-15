"""
Read the log files and plot throughput vs delay.
"""

import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from plots.utils import *

trace_family = sys.argv[1]  # Can be one of {stable, synthetic, real}
directories = sys.argv[2:]

traces_to_plot = {
    "stable": ["wired"],
    "synthetic": ["bump", "sawtooth", "mountain"],
    "real": ["ATT", "Verizon", "TMobile", "step"],
    "all": ["wired", "bump", "sawtooth", "mountain", "ATT", "Verizon", "TMobile", "step"]
}

# Plotting hyperparameters
NUM_RUNS = 5
NUM_TCP_RUNS = 3

# Plot formatting
plt.rcParams["font.size"] = 16
plt.figure(figsize=(6, 4))

colors = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "B85450", "#BF5700"]
# colors = ["#82B366", "#6C8EBF", "#B85450", "#D79B00", "#BF5700", "#BF5700"]
markers = ["o", "P", "^", "s", "p", "D", "v"]
styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 10)), (0, (5, 1))]

# Construct arrays for analysis of utilization and delay (w.r.t the last scheme)
scheme_utils = []
scheme_delays = []
scheme_delays_p95 = []

# Read the sum files.
for index, directory in enumerate(directories):
    # If directory has 'v{version}' in its name or 'c3' -- then it is a learned CC.
    learned_cc = True if ('c3' in directory or re.search(r'v\d+', directory)) else False
    
    file_count = 0
    utilizations = []
    total_drops = 0

    runs = NUM_RUNS if learned_cc else NUM_TCP_RUNS
    for run in range(runs):
        # Read all files in directory/run{run} and choose the one which has trace in its name.
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

            if "sum" not in file:
                # If the file does not have any data, skip it.
                if os.stat(f"{directory}/run{run}/{file}").st_size == 0:
                    continue

                # It is a down file. Compute utilization and continue.
                _, departures, capacity, running_duration, drops = read_down_file(
                    f"{directory}/run{run}/{file}", 500
                )
                total_drops += drops

                if running_duration is None:
                    print(f"{directory}/run{run}/{file}")

                for bin in range(ms_to_bins(running_duration, 500)):
                    departure = departures.get(bin, 0) / (10**3 * 500)
                    total_capacity = capacity.get(bin, 0) / (10**3 * 500)

                    if total_capacity == 0:
                        continue

                    if departure > total_capacity:
                        departure = total_capacity
                    elif departure > 1.25 * total_capacity:
                        print(f"Departure: {departure}, Capacity: {total_capacity}")

                    utilizations.append(departure / total_capacity)

    print(total_drops)
    util_25p = 100 * np.percentile(utilizations, 25)
    util_75p = 100 * np.percentile(utilizations, 75)
    print(util_25p, util_75p, np.percentile(utilizations, 50))

