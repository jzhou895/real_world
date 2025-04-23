# [Num Runs] [Link Name] [Log Name] [ip]

delays=(0 10 50 100)

rm -rf results
mkdir results
for delay in ${delays[@]};
do
    rm -rf logs
    ssh $2 "rm -rf logs; mkdir logs"
    rm -rf reward_averaged.txt
    for i in $(seq 1 $1);
    do
        rm -rf reward.txt
        ./orca.sh 4 1111 $2 "${3}-delay-${delay}-run-${i}" $delay
        # ./orca-off.sh 4 1111 $2 "${3}-off-run-${i}"
        reward=$(python average.py reward.txt)
        echo "${3}-delay-${delay}-run-${i}:$reward" >> reward_averaged.txt
    done
    ssh $2 "cd ~/logs; find -type f -name '*timestamp*' -delete; cd ..; scp -r logs jeffreyz@${4}:~/Orca"
    ./process_down_files.sh logs
    mkdir results/$delay
    cp ./logs/*sum* results/$delay
done  
