We implement algorithms to solve generalized parity games.

== Antichains ==
As a data structure to manipulate games symbollicaly, we use antichains.
The antichain module is rather abstract but still imposes that following
intuition:

To represent downward-closed sets of elements in a partially-ordered set, only
maximal incomparable elements are stored.

The user must provide a "comparator" function x, y -> bool which,
essentially, lets the structure determine whether x <= y for the partial
order. Furthermore, the user gives a "meet" function which allows the
framework to compute the intersection of two sets.

== Tests ==
We are using the Python unittest framework. To run the tests
please call:

python -m unittest discover

or run checks.sh which also verifies the code conforms to PEP8 (a.k.a.
pycodestyle) and pyflakes to catch some simple, local, errors.
