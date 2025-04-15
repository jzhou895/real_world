"""
Analyze and plot the evaluation states/rewards/actions for multiple traces.
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
    curr_epoch = 0
    last_epoch = 0

    with open(file, "r") as f:
        for line in f.readlines():
            line_details = line.split("; ")
            epoch = int(line_details[0].split(": ")[1])

            if epoch > last_epoch:
                for _ in range(epoch - last_epoch):
                    state_action_pairs.append((curr_epoch, 0, 0, 0))
                    curr_epoch += 1
                last_epoch = epoch

            state = float(line_details[1].split(": ")[1].split(",")[5])
            action = float(line_details[2].split(": ")[1])
            tcp_cwnd = float(line_details[3].split(": ")[1])
            resulting_cwnd = get_forced_cwnd(action, tcp_cwnd)

            state_action_pairs.append((curr_epoch, state, resulting_cwnd, tcp_cwnd))
            curr_epoch += 1

    return state_action_pairs


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            f"Usage: {sys.argv[0]} <start-epoch> <end-epoch> <start-time> <end-time> <path-to-eval1>"
        )
        sys.exit(1)

    start_epoch = int(sys.argv[1])
    end_epoch = int(sys.argv[2])
    start_time = int(sys.argv[3])
    end_time = int(sys.argv[4])
    file = sys.argv[5]

    plot_TCP = True

    # Plot formatting
    plt.rcParams["font.size"] = 16

    fig, ax = plt.subplots(3, 1, figsize=(10, 6.4), sharex=True)
    fig.subplots_adjust(hspace=0)

    colors = ["#82B366", "#D79B00", "#B85450", "#6C8EBF", "#9673A6", "#D6B656"]
    markers = ["o", "P", "^", "s", "v", "^"]
    styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]

    if not os.path.exists(file):
        print(f"Eval file {file} does not exist.")
        sys.exit(1)

    state_action_pairs = read_state_action(file)

    epochs = [x[0] for x in state_action_pairs]
    states = [x[1] for x in state_action_pairs]
    resulting_cwnd = [x[2] for x in state_action_pairs]
    tcp_cwnd = [x[3] for x in state_action_pairs]

    if end_epoch == -1:
        end_epoch = epochs[-1]

    # Keep only the states and actions within the start and end time
    epoch, states, resulting_cwnd, tcp_cwnd = zip(
        *[
            (e, s, a, c)
            for e, s, a, c in zip(epochs, states, resulting_cwnd, tcp_cwnd)
            if start_epoch <= e <= end_epoch
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

    ax[0].plot(
        epoch,
        states,
        label=label,
        color="black",
        linestyle=styles[3],
        marker=markers[2],
        linewidth=2,
        markersize=10,
    )
    ax[1].plot(
        epoch,
        resulting_cwnd,
        label=label,
        color=colors[0],
        linestyle=styles[0],
        marker=markers[0],
        linewidth=2,
        markersize=10,
    )
    ax[2].plot(
        epoch,
        tcp_cwnd,
        label=label,
        color=colors[1],        # Using style 1 for TCP
        linestyle=styles[1],    # Using style 1 for TCP
        marker=markers[1],      # Using style 1 for TCP
        linewidth=2,
        markersize=10,
    )

    xlabels = [x for x in np.linspace(start_time, end_time, 5)]
    ax[2].set_xticks([x for x in np.linspace(start_epoch, end_epoch + 0.1, 5)])
    ax[2].set_xticklabels(xlabels)
    ax[2].set_xlabel("Time (s)", fontsize=20)

    ax[0].set_ylabel("invRTT", fontsize=20)
    ax[1].set_ylabel("Orca CWND", fontsize=20)
    ax[2].set_ylabel("TCP CWND", fontsize=20)

    ax[0].axvline(x=608, color="red", linestyle="-.", linewidth=2)
    ax[1].axvline(x=608, color="red", linestyle="-.", linewidth=2)
    ax[2].axvline(x=608, color="red", linestyle="-.", linewidth=2)

    # ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.4), ncol=2)
    plt.subplots_adjust(top=0.95, bottom=0.12, left=0.11, right=0.98)
    plt.savefig("states_epochs.png")
