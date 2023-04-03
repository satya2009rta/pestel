# PeSTel-**Pe**rmissive-**S**trategy-**Te**mp**l**ate

PeSTel is a tool for computing strategy templates for two player graph games with generalized parity objective, i.e., finite conjunction of parity objectives.

## Requirements

- <a href='https://gcc.gnu.org/install/'>GCC</a>
- <a href='https://www.openmp.org/'>OpenMP</a>
- <a href='https://www.python.org/download/releases/2.7/'>Python2</a> (optional, only if you want to use GenZiel tool)

## Installation

Run the following commands to build all executable files

```
make build
```

## Usage
The executable files are generated and stored in the folder `./build/`. Usage of each executables are described below.

`compute.o` computes a winning strategy template for a parity game. It requires one command-line argument which is a filename that contains description of a parity game in pgsolver format; and outputs the result to stdout.

`compose.o` computes a (partial) winning region and a winning strategy template for that region for a generalized parity game. It requires one command-line argument which is a filename that contains description of a generalized parity game in pgsolver format; and outputs the result to stdout.

`hoa2pg.o` converts a parity game in extended HOA format to pgsolver format. It requires one stdin input which is the description of a parity game in extended HOA format; and outputs the game in pgsolver format to stdout.

`pg2gpg.o` converts a parity game to genralized parity game by using standard method to convert parity games to Streett games. It requires one command-line argument which is a filename that contains description of a parity game in pgsolver format; and outputs the result game in pgsolver format to stdout.

`pg2randgpg.o` converts a parity game to several genralized parity games by adding a number of random parity objective to a game graph. It requires three command-line arguments: (1) filename that contains description of a parity game in pgsolver format, (2) number of parity objectives, (3) maximum priority of the parity objectives; and outputs the result game in pgsolver format to stdout.
