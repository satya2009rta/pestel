# !/bin/bash

# function to solve generalized parity games of gpgsolver format using composition
compare () {
    local f=$1
    echo " Solving $f"
    timeout $Nmethod_time $BIN/compare.o $f 0 $method_time; retVal=$?
    timeout $time_limit $BIN/compare.o $f $retVal $method_time $PYPATH >> $OUTPUT; retVal2=$?
    echo "$f: DONE"
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
    compare $f
done
