# !/bin/bash

# file paths
cd $1
PRJ="./../../tool"
BIN="$PRJ/build"
OUTPUT="$PRJ/../output/$2.csv"

conflictsPUF () {
    local f=$1
    local p=$2
    local c=$3
    
    timeout $time_limit $BIN/conflictsPUF.o $f $p $c >> $OUTPUT; retVal2=$?
}

conversion_time=5
time_limit=60
c=5

echo "Name,#vertices,#edges,#priorities,#faulty_edges,% of faulty edges,% of conflicted vertices" > $OUTPUT

for p in $(seq 1 1 5)
do 
    counter=1
    for f in *gm
    do
        conflictsPUF $f $p $c
        echo "### $p-$counter done ###"
        ((counter=counter+1))
    done
    echo "####### $p done #######"
done

for p in $(seq 10 5 30)
do 
    counter=1
    for f in *gm
    do
        conflictsPUF $f $p $c
        echo "### $p-$counter done ###"
        ((counter=counter+1))
    done
    echo "####### $p done #######"
done

