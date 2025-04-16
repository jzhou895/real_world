# Arguments: $1 = directory name

RESULTS_DIR=$1

for resultfile in `find "$RESULTS_DIR/$dir" -type f -name 'down-*'`; do
    sumname=`echo $resultfile | sed 's/down-/sum-/'`
    if [ ! -f "$sumname" ]; then
        $HOME/Orca/rl-module/mm-thr 500 $resultfile 1>tmp 2>$sumname
        rm -rfv tmp
    else
        echo "Skipping $resultfile since final sumfile exists"
    fi
done