# PeSTel-Permissive-Strategy-Template

PeSTel is a tool for computing strategy templates for two player graph games with generalized parity objective, i.e., finite conjunction of parity objectives.

## Installation

Run the following commands to build all executable files

```
make build
```

## Usage
The executable files are generated and stored in the folder `./tool/build/`. Usage of each executables are described below.

`compute.o` computes a winning strategy template for a parity game. It requires one command-line argument which is a filename that contains description of a parity game in pgsolver format; and outputs outputs the result to stdout.

`compose.o` computes a (partial) winning region and a winning strategy template for that region for a generalized parity game. It requires one command-line argument which is a filename that contains description of a generalized parity game in pgsolver format; and outputs the result to stdout.

`hoa2pg.o` converts a parity game in extended HOA format to pgsolver format. It requires one stdin input which is the description of a parity game in extended HOA format; and outputs the game in pgsolver format to stdout.

`pg2gpg.o` converts a parity game to genralized parity game by using standard method to convert parity games to Streett games. It requires one command-line argument which is a filename that contains description of a parity game in pgsolver format; and outputs the result game in pgsolver format to stdout.

`pg2randgpg.o` converts a parity game to several genralized parity games by adding a number of random parity objective to a game graph. It requires three command-line arguments: (1) filename that contains description of a parity game in pgsolver format, (2) number of parity objectives, (3) maximum priority of the parity objectives; and outputs the result game in pgsolver format to stdout.

## Reproducibility Instructions
The experimental results of our paper can be reproduced using the following commands.

The benchmark examples are stored in the folder `./benchmarks/`. To re-generate the examples of `Benchmark A` and `Benchmark B`, run the following command
```
make gen-benchmark-A
make gen-benchmark-B
```

The experimental results related to Incremental Synthesis (i.e., `Table 1`, `Fig. 1`, and `Fig. 5` of the paper) are performed on `Benchmark A` (one shot), `Benchmark B1` (one shot), and `Benchmark B2` (incremental). The experimental results related to Fault-tolerant Control (i.e., `Fig. 4` of the paper) are performed on `Benchmark P` and `Benchmark Q`. Details of these results can be reproduced using the following commands

```
make run-benchmark-A
make run-benchmark-B1
make run-benchmark-B2
make run-benchmark-P
make run-benchmark-Q
```
This produces an experiment table for each benchmark as CSV files in the folder `./output/`.
