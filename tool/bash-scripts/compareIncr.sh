# !/bin/bash

# function to solve generalized parity games of gpgsolver format using composition
compareIncr () {
    local f=$1
    echo " Solving $f"
    timeout $time_limit $BIN/compareIncr.o $f $method_time $PYPATH >> $OUTPUT; retVal=$?
    if [ $retVal -eq 124 ]; then
        timeout $time_limit $BIN/compareIncr.o $f $method_time $PYPATH 1 >> $OUTPUT; retVal2=$?
    fi
    echo "$f DONE"
}


###########################################
# Main script
###########################################

# file paths
cd $1
PRJ="./../../tool"
BIN="$PRJ/build"
OUTPUT="$PRJ/../output/$2.csv"
PYPATH="$PRJ/lib/solveGenParity.py"

echo "Name,#vertices,#edges,#priorities,#objectives,PeSTel: running time,PeSTel: incomplete result,GenZiel: running time,Faster than GenZiel,GenZiel&GenBuchi: running time,GenZiel&GenBuchi: incomplete result,Faster than GenZiel&GenBuchi,GenZiel&GenGoodEp: running time,GenZiel&GenGoodEp: incomplete result,Faster than GenZiel&GenGoodEp,GenZiel&GenLay: running time,GenZiel&GenLay: incomplete result,Faster than GenZiel&GenLay" > $OUTPUT

time_limit=120
conversion_time=5
method_time=10
Nmethod_time=20


for f in *gpg
do 
    compareIncr $f
done
