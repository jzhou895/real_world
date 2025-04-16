rm -rf logs
ssh $1 "ip=`echo $SSH_CLIENT | cut -d ' ' -f1`; scp -r logs $ip:~/Orca/"