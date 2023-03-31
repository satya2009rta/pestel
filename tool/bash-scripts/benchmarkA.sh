# !/bin/bash

# file paths
cd "./benchmarks/SYNTCOMP/all"
PRJ="./../../../tool"
BIN="$PRJ/build"
AFILES="$PRJ/../benchmarks/benchmarkA"

###########################################
# generate benchmark from one hoa file
###########################################
genA () {
    local f=$1
    echo "Converting $f to pgsolver format..."
    timeout $conversion_time $BIN/hoa2pg.o <$f >$f.gm; retVal=$?
    if [ $retVal == 0 ]; then
        echo "$f:conversion to pg successful"
        echo "$f:converting to gpg format"
        $BIN/pg2gpg.o $f.gm >$AFILES/$f.gpg; retVal2=$?
        if [ $retVal2 == 0 ]; then
            echo "$f:conversion to gpg successful"
        else 
            echo "$f:conversion to gpg failed"
        fi
    else 
        echo "$f:conversion to pg failed"
    fi
    rm $f.gm
}


conversion_time=10

for f in *ehoa
do
    genA $f
done
