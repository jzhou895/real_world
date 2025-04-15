# Arguments: $1 = directory name

RESULTS_DIR=$1

for resultfile in `find "$RESULTS_DIR/$dir" -type f -name 'down-*'`; do
    # Replace down- with trimmed- in the resultfile name
    trimmedname=`echo $resultfile | sed 's/down-/trimmed-/'`
    sumname=`echo $resultfile | sed 's/down-/trimmedsum-/'`
    if [ ! -f "$sumname" ]; then
        # python3 process_down_files.py $resultfile
        $HOME/Orca/rl-module/mm-thr 500 $resultfile 1>tmp 2>$sumname
        rm -rfv tmp
    else
        echo "Skipping $resultfile since final sumfile exists"
    fi
done