logname=$1
port=$2
ip=`echo $SSH_CLIENT | cut -d ' ' -f1`

sudo -u $USER mm-delay 0 mm-link $HOME/Orca/traces/wired192 $HOME/Orca/traces/wired192 --downlink-log=$HOME/logs/down-${logname} -- sh -c "sudo -u $USER $HOME/Orca/client $ip 1 $port" &