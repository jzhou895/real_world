# [Num Runs] [Link Name] [Log Name]

rm -rf logs
ssh $2 "mkdir logs"
rm -rf reward_averaged.txt # Temporary Line
for i in $(seq 1 $1);
do
    rm -rf reward.txt # Temporary Line
    ./orca.sh 4 1111 $2 "${3}-run-${i}"
    # ./orca-off.sh 4 1111 $2 "${3}-off-run-${i}"
    reward=$(python average.py reward.txt) # Temporary Line
    echo "${3}-run-${i}:$reward" >> reward_averaged.txt # Temporary Line
done
ssh $2 "cd ~/logs; find -type f -name '*timestamp*' -delete;"
