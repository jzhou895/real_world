# [Log Dir]

import os
import sys
import re
import matplotlib.pyplot as plt
import pandas as pd

def process_off_data(delay_dir):
    total_throughput = 0
    total_packet_delay = 0
    count = 0
    for run in os.listdir(delay_dir):
        with open(os.path.join(delay_dir, run), "r") as f:
            for line in f:
                if "throughput" in line:
                    total_throughput += float(re.findall(r"[-+]?(?:\d*\.*\d+)", line)[1])
                elif "per packet delay" in line:
                    total_packet_delay += float(re.findall(r"[-+]?(?:\d*\.*\d+)", line)[0])

        count += 1.0

    return total_throughput / count, total_packet_delay / count

def plot_data(x, y, xlabel, ylabel, filename):
    xy = pd.DataFrame({'x': x, 'y': y})
    xy.sort_values('x', inplace=True)
    plt.plot(xy['x'], xy['y'], marker='o', label='Orca On')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.savefig(os.path.join(sys.argv[1], filename), format='png', dpi=750)
    plt.clf()

def plot_data_with_baseline(x, y, xlabel, ylabel, baseline, filename):
    xy = pd.DataFrame({'x': x, 'y': [baseline] * len(x)})
    xy.sort_values('x', inplace=True)
    plt.plot(xy['x'], xy['y'], marker='o', label='Orca Off')
    plot_data(x, y, xlabel, ylabel, filename)

def process_results():
    log_dir = sys.argv[1]
    delays = []
    throughput = []
    packet_delay = []
    reward = []

    off_throughput = 0
    off_packet_delay = 0

    for delay in os.listdir(log_dir):
        delay_dir = os.path.join(log_dir, delay)
        
        if not os.path.isdir(delay_dir):
            continue

        if delay == "off":
            off_throughput, off_packet_delay = process_off_data(delay_dir)
            continue

        delays.append(int(delay))

        total_throughput = 0
        total_packet_delay = 0
        total_reward = 0
        count = 0.0
        for run in os.listdir(delay_dir):
            with open(os.path.join(delay_dir, run), "r") as f:
                for line in f:
                    if "throughput" in line:
                        total_throughput += float(re.findall(r"[-+]?(?:\d*\.*\d+)", line)[1])
                    elif "per packet delay" in line:
                        total_packet_delay += float(re.findall(r"[-+]?(?:\d*\.*\d+)", line)[0])
                    elif "Reward" in line:
                        total_reward += float(re.findall(r"[-+]?(?:\d*\.*\d+)", line)[0])

            count += 1.0

        throughput.append(total_throughput / count)
        packet_delay.append(total_packet_delay / count)
        reward.append(total_reward / count)

    plot_data_with_baseline(delays, throughput, "Delay (ms)", "Throughput (%)", off_throughput, "Throughput_Compare.png")
    plot_data(delays, throughput, "Delay (ms)", "Throughput (%)", "Throughput.png")
    plot_data_with_baseline(delays, packet_delay, "Delay (ms)", "Packet_Delay (ms)", off_packet_delay, "Per_Packet_Delay_Compare.png")
    plot_data(delays, packet_delay, "Delay (ms)", "Packet_Delay (ms)", "Per_Packet_Delay.png")
    plot_data(delays, reward, "Delay (ms)", "Reward", "Reward.png")

process_results()