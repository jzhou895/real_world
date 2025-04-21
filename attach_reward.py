import sys

with open("reward_averaged.txt", "r") as f:
    for line in f:
        split = line.split(":")
        f2 = open(sys.argv[1] + "/sum-" + split[0], "a")
        f2.write("Reward: " + split[1])
        f2.close()