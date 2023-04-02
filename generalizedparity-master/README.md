(c) Clement Tamines @ University of Mons, 2019

(c) Guillermo A. Perez @ University of Antwerp, 2019

These Python modules were coded as a proof-of-concept of the algorithms
present in a Reachability Problems 2019 submission concerning generalized
parity games. They implement several complete and partial algorithms for
classical parity games as well as generalized version of them for generalized
parity games --- i.e. games with multiple priority funcitions in which a
player has to satisfy a conjunction of parity objectives w.r.t. all priority
functions.

The Excel tables with the data from our experiments is also
present here (see rp-experiments-tables). To generate the tables yourself,
you can make use of the experiments.py script with partial, partial-gen,
complete, and complete-gen, as parameters (they can be launched in parallel).
The script will generate pickle files (extension .pkl) which can then be
translated into Excel-friendly comma-separated-value files (.csv) using
pkl2csv.py.

* Submission: Partial Solvers for Generalized Parity Games
