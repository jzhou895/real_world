#!/bin/bash

if [ $# != 3 ]
then
    echo -e "usage:$0 [path to train_dir & d5.py] [first_time==1]"
    echo "$@"
    echo "$#"
    exit
fi

path=$1
first_time=$2
delay=$3
##Bring up the learner:
if [ $first_time -eq 1 ];
then
    /users/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path --delay=$3 &
elif [ $first_time -eq 4 ]
then
    /users/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path --load --eval --delay=$3 &
else
    /users/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path --load --delay=$3 &
fi
