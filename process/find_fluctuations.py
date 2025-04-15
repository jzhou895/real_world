"""
Read through all trace files from a directory, and print if any file has a fluctuation in the throughput.
"""

import os
import sys

from plots.utils import *


# Check if there is a fluctuation in the bandwidth utilization.
def has_fluctuation(utilization):
    count = 0
    for i in range(1, len(utilization)):
        if abs(utilization[i] - utilization[i-1]) > 0.2 or utilization[i] < 0.8:
            count += 1
    
    if count > 10:
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path-to-directory>")
        sys.exit(1)

    directory = sys.argv[1]
    ms_per_bin = 500

    for filename in os.listdir(directory):
        if "down-orca" in filename.lower():
            log_file = os.path.join(directory, filename)
            arrivals, departures, capacity, running_duration = read_down_file(
                log_file, ms_per_bin
            )

            utilization = []
            for bin in range(ms_to_bins(running_duration, ms_per_bin)):
                arrival = arrivals.get(bin, 0) / (10**3 * ms_per_bin)
                departure = departures.get(bin, 0) / (10**3 * ms_per_bin)
                unused_capacity = capacity.get(bin, 0) / (10**3 * ms_per_bin)

                if unused_capacity == 0:
                    file = filename.split("/")[-1]
                    continue

                utilization.append(arrival/unused_capacity)

            # Check if there is a fluctuation in the throughput -- in the array post 30s.
            if has_fluctuation(utilization[120:]):
                print(f"Fluctuation in throughput in {log_file}")
