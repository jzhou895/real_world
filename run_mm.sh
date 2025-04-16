logname=$1
port=$2
ip=`echo $SSH_CLIENT | cut -d ' ' -f1`

sudo -u $USER mm-delay 0 mm-link /users/jeffreyz/Orca/traces/wired192 /users/jeffreyz/Orca/traces/wired192 --downlink-log=/users/jeffreyz/logs/down-${logname} -- sh -c "sudo -u $USER /users/jeffreyz/Orca/client $ip 1 $port" &