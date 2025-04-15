"""
Iterate over multiple runs of the same experiment and find the robustness issues.
"""

import os
import sys

from plots.utils import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path-to-directory>")
        sys.exit(1)

    directory = sys.argv[1]
    ms_per_bin = 500

    # Iterate through first level of directories.
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            # Read through all files in dir and get the baseline and noisy files.
            baseline_file = None
            noisy_files = []

            for filename in os.listdir(os.path.join(root, dir)):
                if "down-orca" in filename.lower():
                    baseline_file = os.path.join(root, dir, filename)
                elif "down-uniform" in filename.lower():
                    noisy_files.append(os.path.join(root, dir, filename))

            if baseline_file is None:
                continue

            arrivals, departures, capacity, running_duration = read_down_file(
                baseline_file, ms_per_bin
            )

            baseline_util = []
            for bin in range(ms_to_bins(running_duration, ms_per_bin)):
                arrival = arrivals.get(bin, 0) / (10**3 * ms_per_bin)
                unused_capacity = capacity.get(bin, 0) / (10**3 * ms_per_bin)

                if unused_capacity == 0:
                    continue

                baseline_util.append(arrival / unused_capacity)

            # Use only the elements after 60s.
            baseline_util = baseline_util[120:]

            for noisy_file in noisy_files:
                arrivals, departures, capacity, running_duration = read_down_file(
                    noisy_file, ms_per_bin
                )

                noisy_util = []
                for bin in range(ms_to_bins(running_duration, ms_per_bin)):
                    arrival = arrivals.get(bin, 0) / (10**3 * ms_per_bin)
                    unused_capacity = capacity.get(bin, 0) / (10**3 * ms_per_bin)

                    if unused_capacity == 0:
                        continue

                    noisy_util.append(arrival / unused_capacity)

                # Use only the elements after 60s.
                noisy_util = noisy_util[200:]

                # Check if there are sufficient timesteps where the noisy utilization is less than the baseline.
                count = 0
                for i in range(min(len(baseline_util), len(noisy_util))):
                    if baseline_util[i] - noisy_util[i] > 0.1:
                        count += 1
                
                if count > 25:
                    print(f"Robustness issue in {dir} {noisy_file}")