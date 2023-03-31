# !/bin/bash

# file paths
cd "./benchmarks/SYNTCOMP/all"
PRJ="./../../../tool"
BIN="$PRJ/build"
AFILES="$PRJ/../benchmarks/benchmarkP"

###########################################
# generate benchmark from one hoa file
###########################################
genP () {
    local f=$1
    echo "Converting $f to pgsolver format..."
    timeout $conversion_time $BIN/hoa2pg.o <$f >$AFILES/$f.gm; retVal=$?
    if [ $retVal == 0 ]; then
        echo "$f:conversion to pg successful"
    else 
        echo "$f:conversion to pg failed"
    fi
}


conversion_time=10

for f in *ehoa
do
    genP $f
done
