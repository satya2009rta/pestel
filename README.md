# PeSTel-**Pe**rmissive-**S**trategy-**Te**mp**l**ate

PeSTel is a tool for computing strategy templates for two player graph games with generalized parity objective, i.e., finite conjunction of parity objectives, presented in the paper [Synthesizing Permissive Winning Strategy Templates for Parity Games](https://arxiv.org/abs/2305.14026) (CAV'23).

## Requirements

- <a href='https://gcc.gnu.org/install/'>GCC</a>

## Installation

Run the following commands to build all executable files

```
make build
```

## Usage
The executable files are generated and stored in the folder `./build/`. Usage of each executable are described below.

\- `pestel` computes a winning strategy template for a parity or generalized parity game. It requires stdin input which is one of the follows:
- description of a parity game in extended HOA or pgsolver format,
- description of a generalized parity game in pgsolver format.

It outputs the winning strategy template to stdout.

Example usage:
```
./build/pestel < ./examples/ltl2dpa01.tlsf.gm
```

\- `pg2gpg` converts a parity game to generalized parity game by using standard method to convert parity games to Streett games. It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the resulting game in pgsolver format to stdout.

Example usage:
```
./build/pg2gpg < ./examples/test_gpg_02.gpg
```

\- `pg2randgpg` converts a parity game to a generalized parity game by adding a number of random parity objective to a game graph. It requires three command-line arguments: (1) filename that contains description of a parity game in extended HOA or pgsolver format, (2) number of parity objectives, (3) maximum priority of the parity objectives; and outputs the resulting game in pgsolver format to stdout.

Example usage:
```
./build/pg2randgpg ./examples/test_pg_01.gm 4 2
```

