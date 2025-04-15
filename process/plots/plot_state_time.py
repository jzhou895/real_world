"""
Analyze and plot the evaluation states/rewards/actions for multiple traces.
Used when timestamps are available in the eval file.
"""

import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

from utils import *


def get_forced_cwnd(alpha, tcp_cwnd):
    """
    Get the forced cwnd from the alpha and the tcp_cwnd. cwnd = int(math.pow(4, action) * 100) * cwnd_TCP / 100.
    The same as the env.map_action(action) and the cwnd update in orca-server-mahimahi.
    alpha: float. The alpha value.
    tcp_cwnd: float. The tcp_cwnd value.

    return: float. The forced cwnd value.
    """
    out = math.pow(4, alpha)
    out *= 100
    out = int(out)
    target_ratio = out * tcp_cwnd / 100  # follow the orca-server-mahimahi
    return target_ratio


def read_state_action(file):
    state_action_pairs = []
    start_time = None

    with open(file, "r") as f:
        for line in f.readlines():
            line_details = line.split("; ")
            curr_time = float(line_details[0].split(": ")[1].split(", ")[0])
            if start_time is None:
                start_time = curr_time

            state = float(line_details[1].split(": ")[1].split(",")[5])
            action = float(line_details[2].split(": ")[1])
            tcp_cwnd = float(line_details[3].split(": ")[1])
            resulting_cwnd = get_forced_cwnd(action, tcp_cwnd)

            state_action_pairs.append(
                (curr_time - start_time, state, resulting_cwnd, tcp_cwnd)
            )

    return state_action_pairs


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <start-time> <end-time> <offset> <path-to-eval1> <path-to-eval2> ..."
        )
        sys.exit(1)

    start_time = float(sys.argv[1])
    end_time = float(sys.argv[2])
    offset = int(sys.argv[3])
    eval_files = sys.argv[4:]

    # Plot formatting
    plt.rcParams["font.size"] = 16
    fig, ax = plt.subplots(2, 1, figsize=(10, 4.8), sharex=True)
    fig.subplots_adjust(hspace=0)

    colors = ["#82B366", "#D79B00", "#B85450", "#6C8EBF", "#9673A6", "#D6B656"]
    markers = ["o", "P", "^", "s", "v", "^"]
    styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]

    for index, file in enumerate(eval_files):
        if not os.path.exists(file):
            print(f"Eval file {file} does not exist.")
            sys.exit(1)

        state_action_pairs = read_state_action(file)

        time = [x[0] for x in state_action_pairs]
        states = [x[1] for x in state_action_pairs]
        resulting_cwnd = [x[2] for x in state_action_pairs]
        tcp_cwnd = [x[3] for x in state_action_pairs]

        if end_time == -1:
            end_time = time[-1]

        # Keep only the states and actions within the start and end time
        time, states, resulting_cwnd = zip(
            *[
                (t, s, a)
                for t, s, a in zip(time, states, resulting_cwnd)
                if start_time <= t <= end_time
            ]
        )

        if "tcp" in file:
            label = file.split("/")[-1].split("-")[1]
            label = label.replace("_", " ").split(" ")[1].capitalize()
        else:
            if "c3" in file:
                label = "C3"
            else:
                label = file.split("/")[-2]
                label = " ".join([word.capitalize() for word in label.split("-")])

                if "Baseline" in label:
                    label = label.replace("Baseline", "Orca")
                elif "Noise" in label:
                    label = label.replace("Noise", "Uniform")

        style_id = -2 if "uniform" in label.lower() else index

        ax[0].plot(
            time,
            states,
            label=label,
            color=colors[style_id],
            linestyle=styles[style_id],
            marker=markers[style_id],
            linewidth=2,
            markersize=10,
        )
        ax[1].plot(
            time,
            resulting_cwnd,
            label=label,
            color=colors[style_id],
            linestyle=styles[style_id],
            marker=markers[style_id],
            linewidth=2,
            markersize=10,
        )

    ax[1].set_xticks([x for x in np.arange(start_time, end_time + 0.1, 0.25)])
    ax[1].set_xticklabels(
        [f"{(x-offset):.3f}" for x in np.arange(start_time, end_time + 0.1, 0.25)]
    )
    ax[1].set_xlabel("Time (s)", fontsize=20)

    ax[0].set_ylabel("invRTT", fontsize=20)
    ax[1].set_ylabel("CWND\n(pkts)", fontsize=20)

    ax[0].axvline(x=offset+11.25, color="red", linestyle="-.", linewidth=2)
    ax[1].axvline(x=offset+11.25, color="red", linestyle="-.", linewidth=2)

    ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.4), ncol=2, fontsize=20, frameon=False)
    plt.subplots_adjust(top=0.88, bottom=0.15, left=0.12, right=0.98)
    plt.savefig("states_actions.png")
