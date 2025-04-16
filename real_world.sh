# [Num Runs] [Link Name] [Log Name]

ssh $2 "mkdir logs"
for i in $(seq 1 $1);
do
    ./orca.sh 4 1111 $2 "${3}-run-${i}"
    ./orca-off.sh 4 1111 $2 "${3}-off-run-${i}"
done
ssh $2 "cd ~/logs; find -type f -name '*timestamp*' -delete"