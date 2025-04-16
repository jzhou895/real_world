rm -rf logs
ssh $1 "scp -r logs $2:~/Orca/"