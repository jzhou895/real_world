ip=`echo $SSH_CLIENT | cut -d ' ' -f1`
scp $HOME/logs ip:$HOME/Orca