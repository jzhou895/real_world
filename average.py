import sys

total = 0
count = 0

with open(sys.argv[1], 'r') as file:
    for line in file:
        total += float(line)
        count += 1

print(total / count)