# PeSTel-**Pe**rmissive-**S**trategy-**Te**mp**l**ate

PeSTel is a tool for computing strategy templates for two player graph games with generalized parity objective, i.e., finite conjunction of parity objectives, presented in the paper [Synthesizing Permissive Winning Strategy Templates for Parity Games](https://arxiv.org/abs/2305.14026) (CAV'23).

## Requirements

- <a href='https://gcc.gnu.org/install/'>GCC</a>

## Installation

Run the following commands to build all executable files

```
make
```

## Usage
The executable files are generated and stored in the folder `./build/`. Usage of all the executables are described below.

### - pestel
```
Usage: pestel [OPTION...]
```

Inputs/Outputs:
- STDIN: description of a parity game in extended-HOA/pgsolver format or description of a generalized parity game in pgsolver format
- STDOUT: a winning strategy template 

The possible OPTIONs are as follows:
- --print-game: print the parity game (same format as input)
- --print-game=pg: print the parity game in pgsolver format
- --print-template-size: print size of the templates

Example usage:
```
./build/pestel --print-template-size < ./examples/ltl2dpa01.tlsf.gm
```

### - pg2gpg
```
Usage: pg2gpg 
```

Inputs/Outputs:
- STDIN: description of a parity game in extended-HOA/pgsolver format
- STDOUT: a generalized parity game (in pgsolver format) that is equivalent to the given parity game obtained by using standard conversion from parity games to Streett games

Example usage:
```
./build/pg2gpg < ./examples/test_gpg_02.gpg
```

### - pg2randgpg
```
Usage: pg2randgpg [num_obj] [max_col]
```

Inputs/Outputs:
- num_obj: number of parity objectives to be generated
- max_col: maximum priority of the parity objectives
- STDIN: description of a parity game in extended-HOA/pgsolver format
- STDOUT: a generalized parity game (in pgsolver format) obtained by adding a number of random parity objectives to the given game graph

Example usage:
```
./build/pg2randgpg 4 2 < ./examples/test_pg_01.gm
```

