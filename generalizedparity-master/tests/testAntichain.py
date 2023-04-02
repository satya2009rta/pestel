import unittest
from antichain import Antichain


class TestAntichainMethods(unittest.TestCase):

    def test_natvectors(self):
        print("Testing natural vector antichains")

        def compare_lists(t1, t2):
            return len(t1) == len(t2) and\
                all(map(lambda x: x[0] <= x[1], zip(t1, t2)))

        def meet_lists(t1, t2):
            assert len(t1) == len(t2)
            return map(lambda x: max(x[0], x[1]), zip(t1, t2))

        ac = Antichain(compare_lists, meet_lists)
        ac.insert([1, 2])  # this should enter
        self.assertTrue(ac.contains([1, 2]))
        ac.insert([1, 3])  # this is larger than the previous one
        self.assertFalse(ac.contains([1, 2]))
        self.assertTrue(ac.contains([1, 3]))
        ac.insert([2, 1])  # this should enter too
        self.assertTrue(ac.contains([2, 1]))
        self.assertTrue(ac.contains([1, 3]))


if __name__ == '__main__':
    unittest.main()
