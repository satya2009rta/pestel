# !/bin/bash

# file paths
cd "./benchmarks/SYNTCOMP/ltl2dba"
PRJ="./../../../tool"
BIN="$PRJ/build"
BFILES="$PRJ/../benchmarks/benchmarkB/"

###########################################
# generate benchmark from one hoa file
###########################################
genB() {
    local f=$1
    local g=$2
    local c=$3
    echo "Converting $f to pgsolver format..."
    timeout $conversion_time $BIN/hoa2pg.o <$f >$f.gm; retVal=$?
    if [ $retVal == 0 ]; then
        echo "$f:conversion to pg successful"
        echo "$f:converting to gpg format"
        $BIN/pg2randgpg.o $f.gm $g $c $BFILES; retVal2=$?
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

benchmark () {
    local g=$1
    local c=$2

    for f in *ehoa
    do 
        genB "$f" "$g" "$c"; retVal=$?
    done
    echo "$g-$c:coversion done"
}


conversion_time=10
g=8
for c in $(seq 3 1 8)
    do
        benchmark "$g" "$c"
    done

