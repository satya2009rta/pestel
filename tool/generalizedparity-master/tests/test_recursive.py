import random
import unittest

import file_handler as io
import generators as gen
import zielonka as zielonka
import generalized_parity_recursive as recursive


class TestRecursive(unittest.TestCase):
    """
    Test cases for the recursive algorithm used to solve generalized parity games.
    """

    def setUp(self):
        # set the random seed to produce reproducible tests
        # random.seed(42) assert problem size 22
        # random.seed(41) assert problem size 18
        random.seed(26)
        self.number_of_random = 100
        self.number_of_random_double = 100

    def test_recursive_single_priority_random(self):
        """
        Check if solution computed by the recursive algorithm is correct.
        We create random parity games and transform them into generalized parity games by using a copy of the first
        priority function as a second priority function.
        """
        print("test recursive single priority random")
        for i in range(5, self.number_of_random + 5):
            g = gen.random(i, i / 2, 1, i / 3)

            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)

            self.assertTrue(set(winning_region_0) == set(computed_winning_0))
            self.assertTrue(set(winning_region_1) == set(computed_winning_1))

    def test_recursive_double_priority_random(self):
        """
        Check if solution computed by the recursive algorithm is correct.
        We create random parity games and transform them into generalized parity games by using a copy of the first
        priority function as a second priority function.
        """
        print("test recursive double priority random")
        for i in range(5, self.number_of_random_double + 5):
            g = gen.random(i, i / 2, 1, i / 3)

            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)

            g_generalized = gen.multiple_priorities(g, 2)

            computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g_generalized)

            self.assertTrue(set(winning_region_0) == set(computed_winning_0))
            self.assertTrue(set(winning_region_1) == set(computed_winning_1))

    def test_recursive_solved_examples(self):
        """
        Checks the solution of the recursive algorithm on examples solved by hand.
        """
        print("test recursive solved examples")
        g = io.load_generalized_from_file("examples/example_0.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 4, 1, 6})
        self.assertTrue(set(computed_winning_1) == {5, 3})

        g = io.load_generalized_from_file("examples/example_1.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 2})
        self.assertTrue(set(computed_winning_1) == set())

        g = io.load_generalized_from_file("examples/example_2.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 4, 2})
        self.assertTrue(set(computed_winning_1) == set())

        g = io.load_generalized_from_file("examples/example_3.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 3, 4})
        self.assertTrue(set(computed_winning_1) == {6, 7, 5})

        g = io.load_generalized_from_file("examples/example_4.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 5})
        self.assertTrue(set(computed_winning_1) == {6, 3, 4})

        g = io.load_generalized_from_file("examples/example_5.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 5})
        self.assertTrue(set(computed_winning_1) == {7, 6, 3, 4})

        # corresponds to counter_example in gamesolver
        g = io.load_generalized_from_file("examples/example_6.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {1, 2, 3})

        # corresponds to simple_example in gamesolver
        g = io.load_generalized_from_file("examples/example_7.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 2, 3})
        self.assertTrue(set(computed_winning_1) == set())

        # corresponds to simple_example2 in gamesolver
        g = io.load_generalized_from_file("examples/example_8.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 2})
        self.assertTrue(set(computed_winning_1) == {3, 4, 5})

        # corresponds to simple_example3 in gamesolver
        g = io.load_generalized_from_file("examples/example_9.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 2, 3, 5, 6})
        self.assertTrue(set(computed_winning_1) == {4})

    def test_recursive_solved_worstcases(self):
        """
        Checks the solution of the recursive algorithm on worst case graphs for the recursive algorithm for regular
        parity games.
        """
        print("test recursive solved worstcases")
        g = io.load_generalized_from_file("examples/worstcase_1.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 4, 2, 0})
        self.assertTrue(set(computed_winning_1) == set())

        g = io.load_generalized_from_file("examples/worstcase_2.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {6, 8, 9, 7, 5, 4, 0, 2, 1, 3})

    def test_recursive_solved_double_priority(self):
        """
        Checks the solution of the recursive algorithm on graphs in which the priority functions are twice the same.
        """
        print("test recursive solved double priority")
        g = io.load_generalized_from_file("examples/double_priority.txt")
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {4, 5, 6, 7, 3, 1, 2})

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_0.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 4, 1, 6})
        self.assertTrue(set(computed_winning_1) == {5, 3})

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_1.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 2})
        self.assertTrue(set(computed_winning_1) == set())

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_2.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 4, 2})
        self.assertTrue(set(computed_winning_1) == set())

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_3.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 3, 4})
        self.assertTrue(set(computed_winning_1) == {6, 7, 5})

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_4.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 5})
        self.assertTrue(set(computed_winning_1) == {6, 3, 4})

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/example_5.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {2, 1, 5})
        self.assertTrue(set(computed_winning_1) == {7, 6, 3, 4})

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/worstcase_1.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == {1, 3, 4, 2, 0})
        self.assertTrue(set(computed_winning_1) == set())

        g = gen.multiple_priorities(io.load_generalized_from_file("examples/worstcase_2.txt"), 2)
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {6, 8, 9, 7, 5, 4, 0, 2, 1, 3})

    def test_recursive_solved_opposite_priority(self):
        """
        Checks the solution of the recursive algorithm on graphs in which the second priority function is the first
        priority function, but complemented. functions are twice the same.
        """
        print("test recursive solved opposite priority")
        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_0.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {2, 4, 1, 6, 5, 3})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_1.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {1, 3, 2})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_2.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {1, 3, 4, 2})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_3.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {2, 1, 3, 4, 6, 7, 5})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_4.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {2, 1, 5, 6, 3, 4})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/example_5.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {2, 1, 5, 7, 6, 3, 4})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/worstcase_1.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {1, 3, 4, 2, 0})

        g = gen.opposite_priorities(io.load_generalized_from_file("examples/worstcase_2.txt"))
        computed_winning_0, computed_winning_1 = recursive.generalized_parity_solver(g)
        self.assertTrue(set(computed_winning_0) == set())
        self.assertTrue(set(computed_winning_1) == {6, 8, 9, 7, 5, 4, 0, 2, 1, 3})


if __name__ == '__main__':
    unittest.main()
