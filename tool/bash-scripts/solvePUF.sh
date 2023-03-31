# !/bin/bash

# file paths
cd $1
PRJ="./../../tool"
BIN="$PRJ/build"
OUTPUT="$PRJ/../output/$2.csv"

solvePUFgame () {
    local f=$1
    local p=$2
    
    echo "$f:solving game with $p% PUF edges"
    timeout $time_limit $BIN/solvePUF.o $f $p >> $OUTPUT; retVal2=$?
    if [ $retVal2 == 0 ]; then
        echo "$f:completed:success"
    else 
        echo "$f:completed:failed"
    fi
}

conversion_time=5
time_limit=60

echo "Name,#vertices,#edges,#priorities,#faulty_edges,% of faulty edges,needs_computation" > $OUTPUT

for c in $(seq 1 1 5)
do  
for p in $(seq 1 1 5)
do 
    counter=1
    for f in *gm
    do
        solvePUFgame $f $p
        echo "### $c-$p-$counter done ###"
        ((counter=counter+1))
    done
    echo "####### $c-$p done #######"
done 
for p in $(seq 10 5 30)
do 
    counter=1
    for f in *gm
    do
        solvePUFgame $f $p
        echo "### $c-$p-$counter done ###"
        ((counter=counter+1))
    done
    echo "####### $c-$p done #######"
done
done
