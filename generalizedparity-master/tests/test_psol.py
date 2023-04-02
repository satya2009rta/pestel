import random
import unittest

import file_handler as io
import generators as gen
import zielonka as zielonka
from fatalattractors import psol as fatal


class TestPSOL(unittest.TestCase):
    """
    Test cases for the PSOL partial solver.
    """

    def setUp(self):
        # set the random seed to produce reproducible tests
        random.seed(42)

        self.fully_solved_ladder = 0
        self.er_fully_solved_ladder = 0
        self.number_of_ladder = 50

        self.fully_solved_worstcase = 0
        self.er_fully_solved_worstcase = 0
        self.number_of_worstcase = 12

        self.fully_solved_random = 0
        self.er_fully_solved_random = 0
        self.number_of_random = 400

    def test_PSOL_paper_example(self):
        """
        Check if solution computed by PSOL is correct on an example provided in the paper 'Fatal Attractors in Parity
        Games: Building Blocks for Partial Solvers'. Note : priorities were inverted since we work with max parity
        and the paper works with min parity.
        """

        print("test psol paper example")

        g = io.load_from_file("examples/fatal_attractors_paper_example.txt")

        winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
        resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol(g, [], [])

        expected_region_0, expected_region_1 = {2, 4, 6, 8, 0, 1, 9, 10, 11}, set()
        should_remain = {3, 5, 7}

        self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
        self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

        self.assertTrue(should_remain == set(resulting_arena.get_nodes()))

        self.assertTrue(expected_region_0 == set(fatal_region_0))
        self.assertTrue(expected_region_1 == set(fatal_region_1))

    def test_PSOL_ladder(self):
        """
        Check if solution computed by PSOL is included in the full solution computed by Zielonka's algorithm.
        """
        print("test psol ladder")
        for i in range(self.number_of_ladder):
            g = gen.ladder(i)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.fully_solved_ladder += 1

        print("Number of ladder games fully solved by PSOL = " + str(self.fully_solved_ladder) + "\n")

    def test_PSOL_worstcase(self):
        """
        Check if solution computed by PSOL is included in the full solution computed by Zielonka's algorithm.
        """
        print("test psol worstcase")
        for i in range(self.number_of_worstcase):
            g = gen.strong_parity_worst_case(i)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.fully_solved_worstcase += 1

        print("Number of worst case games fully solved by PSOL = " + str(self.fully_solved_worstcase) + "\n")

    def test_PSOL_random(self):
        """
        Check if solution computed by PSOL + edge removal is included in the full solution computed by
        Zielonka's algorithm.
        """
        print("test psol random")
        not_solved_size = []
        for i in range(5, self.number_of_random + 5):
            g = gen.random(i, i / 2, 1, i / 3)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.fully_solved_random += 1
            else:
                not_solved_size.append(i)

        print("Number of random games fully solved by PSOL = " + str(self.fully_solved_random))
        print("Size of games not solved = " + str(not_solved_size) + "\n")

    def test_PSOL_edge_removal_paper_example(self):
        """
        Check if solution computed by PSOL + edge removal is correct on an example provided in the paper 'Fatal
        Attractors in Parity Games: Building Blocks for Partial Solvers'. Note : priorities were inversed since we work
        with max parity and the paper works with min parity.
        """
        print("test psol edge removal paper example")
        g = io.load_from_file("examples/fatal_attractors_paper_example.txt")

        winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
        resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol_edge_removal(g, [], [])

        expected_region_0, expected_region_1 = {2, 4, 6, 8, 0, 1, 9, 10, 11}, set()
        should_remain = {3, 5, 7}

        self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
        self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

        self.assertTrue(should_remain == set(resulting_arena.get_nodes()))

        self.assertTrue(expected_region_0 == set(fatal_region_0))
        self.assertTrue(expected_region_1 == set(fatal_region_1))

    def test_PSOL_edge_removal_ladder(self):
        """
        Check if solution computed by PSOL + edge removal is included in the full solution computed by Zielonka's
        algorithm.
        """
        print("test psol edge removal ladder")
        for i in range(self.number_of_ladder):
            g = gen.ladder(i)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol_edge_removal(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.er_fully_solved_ladder += 1

        print("Number of ladder games fully solved by PSOL with edge removal = " + str(
            self.er_fully_solved_ladder) + "\n")

    def test_PSOL_edge_removal_worstcase(self):
        """
        Check if solution computed by PSOL + edge removal is included in the full solution computed by
        Zielonka's algorithm.
        """
        print("test psol edge removal worstcase")
        for i in range(self.number_of_worstcase):
            g = gen.strong_parity_worst_case(i)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol_edge_removal(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.er_fully_solved_worstcase += 1

        print("Number of worst case games fully solved by PSOL with edge removal = " + str(
            self.er_fully_solved_worstcase) + "\n")

    def test_PSOL_edge_removal_random(self):
        """
        Check if solution computed by PSOL +edge removal is included in the full solution computed by
        Zielonka's algorithm.
        """
        print("test psol edge removal random")
        not_solved_size = []
        for i in range(5, self.number_of_random + 5):
            g = gen.random(i, i / 2, 1, i / 3)
            winning_region_0, winning_region_1 = zielonka.strong_parity_solver_no_strategies(g)
            resulting_arena, fatal_region_0, fatal_region_1 = fatal.psol_edge_removal(g, [], [])

            self.assertTrue(elem in winning_region_0 for elem in fatal_region_0)
            self.assertTrue(elem in winning_region_1 for elem in fatal_region_1)

            # if the game is completely solved by PSOL
            if set(winning_region_0) == set(fatal_region_0) and set(winning_region_1) == set(fatal_region_1):
                self.er_fully_solved_random += 1
            else:
                not_solved_size.append(i)

        print("Number of random games fully solved by PSOL with edge removal= " + str(self.er_fully_solved_random))
        print("Size of games not solved = " + str(not_solved_size) + "\n")


if __name__ == '__main__':
    unittest.main()
