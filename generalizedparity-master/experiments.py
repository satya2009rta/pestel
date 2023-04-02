#!/usr/bin/env python


import sys
import os
import fnmatch
import zielonka
import generalized_parity_recursive as gpg
import generalized_zielonka_with_partials as genpartial
import generators
import fatalattractors.psolB as psolB
import fatalattractors.psolC as psolC
import fatalattractors.psolQ as psolQ
import fatalattractors.psolB_generalized as psolB_generalized
import fatalattractors.psolQ_generalized as psolQ_generalized
import fatalattractors.psolC_generalized as psolC_generalized
import file_handler
from benchmarks.compare_algorithms import compare_partial_algorithms,\
    compare_complete_algorithms_LTLbenchmarks, set_timeout


def random_games(i):
    # for some reason this does not work for indices < 5
    j = i + 5
    return generators.random(j, j, 1, j / 3)


sample_files = filter(lambda f: fnmatch.fnmatch(f, "*.pg"),
                      os.listdir("./examples"))
num_examples = len(sample_files)


def all_examples(i):
    g = file_handler.load_from_file(
        os.path.join("examples", sample_files[i]))
    g.name = sample_files[i]
    return g


gen_sample_files = filter(lambda f: fnmatch.fnmatch(f, "*.gpg"),
                          os.listdir("./examples"))
num_gen_examples = len(gen_sample_files)


def all_generalized_examples(i):
    g = file_handler.load_generalized_from_file(
        os.path.join("examples", gen_sample_files[i]))
    g.name = gen_sample_files[i]
    assert(len(g.get_nbr_priorities()) > 1)
    return g


def complete():
    # Zielonka + partial solvers now
    algorithms_partial_zielonka =\
        [zielonka.strong_parity_solver_no_strategies,
         zielonka.zielonka_with_psolB,
         zielonka.zielonka_with_psolQ,
         zielonka.zielonka_with_psolC]

    labels_partial_zielonka = ["Zielonka",
                               "Ziel + psolB",
                               "Ziel + psolQ",
                               "Ziel + psolC"]

    compare_complete_algorithms_LTLbenchmarks(
        algorithms_partial_zielonka,
        all_examples,
        num_examples,
        preprocess=[None] * len(labels_partial_zielonka),
        iterations=2,
        step=1,
        check_solution=False,
        plot=True,
        path="all_ziel.pdf",
        path_tot="all_ziel_cumulative.pdf",
        title="Comparison of Zielonka + partial solver on LTL benchmarks",
        pkl_path="ziel_combo.pkl",
        labels=labels_partial_zielonka)


def complete_gen():
    algorithms_partial_genzielonka =\
        [gpg.generalized_parity_solver,
         genpartial.generalized_with_psolB,
         genpartial.generalized_zielonka_with_psolQ,
         genpartial.generalized_zielonka_with_psolC]

    labels_partial_genzielonka = ["Gen Zielonka",
                                  "Gen Ziel + Gen psolB",
                                  "Gen Ziel + Gen psolQ",
                                  "Gen Ziel + Gen psolC"]

    compare_complete_algorithms_LTLbenchmarks(
        algorithms_partial_genzielonka,
        all_generalized_examples,
        num_gen_examples,
        preprocess=[None] * len(labels_partial_genzielonka),
        iterations=2,
        step=1,
        check_solution=False,
        plot=True,
        path="genziel+partials-time.pdf",
        path_tot="genziel+partials-cumulative.pdf",
        title="Comparison of Gen Zielonka + partial solver on LTL benchmarks",
        pkl_path="genziel_combo.pkl",
        labels=labels_partial_genzielonka)


def partial():
    labels = ["psolB", "psolQ", "psolC"]
    algorithms_partial = [psolB.psolB_set,
                          psolQ.psolQ,
                          psolC.psolC]

    print("Running experiments for all files in ./examples")

    compare_partial_algorithms(
        algorithms_partial,
        all_examples,
        num_examples,
        preprocess=[None, None, None, None, None],
        iterations=2,
        step=1,
        labels=labels,
        plot=True,
        path_time="all_time.pdf",
        path_proportion="all_prop.pdf",
        path_bulkprop="all_bulkprop.pdf",
        path_tottime="all_tottime.pdf",
        # control_algorithm=zielonka.strong_parity_solver_no_strategies,
        pkl_path="all_data.pkl")


def partial_gen():
    # generalized parity games now
    labels = ["psolB", "psolQ", "psolC"]
    algorithms_general = [psolB_generalized.psolB_generalized_inline,
                          psolQ_generalized.psolQ_generalized,
                          psolC_generalized.psolC_generalized]

    print("experiments for generalized parity games: all files in ./examples")

    compare_partial_algorithms(algorithms_general,
                               all_generalized_examples,
                               num_gen_examples,
                               preprocess=[None, None, None, None, None],
                               iterations=2,
                               step=1,
                               labels=labels,
                               plot=True,
                               path_time="allgen_time.pdf",
                               path_proportion="allgen_prop.pdf",
                               path_bulkprop="allgen_bulkprop.pdf",
                               path_tottime="allgen_tottime.pdf",
                               # control_algorithm=gpg.generalized_parity_solver,
                               pkl_path="allgen_data.pkl")


abo_sample_files = filter(lambda f: fnmatch.fnmatch(f, "*.pg"),
                          os.listdir("./hardexamples"))
num_abo_examples = len(abo_sample_files)


def abo_examples(i):
    g = file_handler.load_from_file(
        os.path.join("hardexamples", abo_sample_files[i]))
    g.name = abo_sample_files[i]
    print("Experiments with " + g.name)
    return g


def fatal_abo():
    set_timeout(1500)

    labels = ["psolB", "psolQ", "psolC"]
    algorithms_partial = [psolB.psolB_set,
                          psolQ.psolQ,
                          psolC.psolC]

    print("Running experiments for PGSolver hard examples")

    compare_partial_algorithms(
        algorithms_partial,
        abo_examples,
        num_abo_examples,
        preprocess=[None, None, None, None, None],
        iterations=1,
        step=1,
        labels=labels,
        plot=True,
        path_time="abo_time.pdf",
        path_proportion="abo_prop.pdf",
        path_bulkprop="abo_bulkprop.pdf",
        path_tottime="abo_tottime.pdf",
        # control_algorithm=zielonka.strong_parity_solver_no_strategies,
        pkl_path="abo_part.pkl")


def fatal_abo_complete():
    set_timeout(1500)

    algorithms_partial_zielonka =\
        [zielonka.strong_parity_solver_no_strategies,
         zielonka.zielonka_with_psolB,
         zielonka.zielonka_with_psolQ,
         zielonka.zielonka_with_psolC]

    labels_partial_zielonka = ["Zielonka",
                               "Ziel + psolB",
                               "Ziel + psolQ",
                               "Ziel + psolC"]

    compare_complete_algorithms_LTLbenchmarks(
        algorithms_partial_zielonka,
        abo_examples,
        num_abo_examples,
        preprocess=[None] * len(labels_partial_zielonka),
        iterations=1,
        step=1,
        check_solution=False,
        plot=True,
        path="abo_ziel.pdf",
        path_tot="abo_ziel_cumulative.pdf",
        title="Comparison of Zielonka + partial solver on LTL benchmarks",
        labels=labels_partial_zielonka,
        pkl_path="abo_ziel.pkl")


def specific_example_gen():
    set_timeout(120)
    specific_file_names = ["./examples/amba_decomposed_tincr.tlsf.gpg",
                           "./examples/load_balancer_2.tlsf.gpg"]

    def specific_generator(i):
        game = file_handler.load_generalized_from_file(specific_file_names[i])
        game.name = specific_file_names[i][11:]
        return game

    labels = ["psolB", "psolQ", "psolC"]
    algorithms_general = [psolB_generalized.psolB_generalized_inline,
                          psolQ_generalized.psolQ_generalized,
                          psolC_generalized.psolC_generalized]

    compare_partial_algorithms(algorithms_general,
                               specific_generator,
                               2,
                               preprocess=[None, None, None, None, None],
                               iterations=4,
                               step=1,
                               labels=labels,
                               plot=True,
                               path_time="allgen_time.pdf",
                               path_proportion="allgen_prop.pdf",
                               path_bulkprop="allgen_bulkprop.pdf",
                               path_tottime="allgen_tottime.pdf",
                               # control_algorithm=gpg.generalized_parity_solver,
                               pkl_path="allgen_data.pkl")

    algorithms_partial_genzielonka =\
        [gpg.generalized_parity_solver,
         genpartial.generalized_with_psolB,
         genpartial.generalized_zielonka_with_psolQ,
         genpartial.generalized_zielonka_with_psolC]

    labels_partial_genzielonka = ["Gen Zielonka",
                                  "Gen Ziel + Gen psolB",
                                  "Gen Ziel + Gen psolQ",
                                  "Gen Ziel + Gen psolC"]

    compare_complete_algorithms_LTLbenchmarks(
        algorithms_partial_genzielonka,
        specific_generator,
        2,
        preprocess=[None] * len(labels_partial_genzielonka),
        iterations=4,
        step=1,
        check_solution=False,
        plot=True,
        path="genziel+partials-time.pdf",
        path_tot="genziel+partials-cumulative.pdf",
        title="Comparison of Gen Zielonka + partial solver on LTL benchmarks",
        pkl_path="genziel_combo.pkl",
        labels=labels_partial_genzielonka)


def specific_example():
    set_timeout(120)
    specific_file_name = "./examples/ltl2dba_E_10.tlsf.pg"

    def specific_generator(i):
        game = file_handler.load_from_file(specific_file_name)
        game.name = specific_file_name[10:]
        return game

    # first, the complete algorithms for one dimension

    algorithms_partial_zielonka_specific =\
        [zielonka.strong_parity_solver_no_strategies,
         zielonka.zielonka_with_psolB,
         zielonka.zielonka_with_psolQ,
         zielonka.zielonka_with_psolC]

    labels_partial_zielonka_specific = ["Zielonka",
                                        "Ziel + psolB",
                                        "Ziel + psolQ",
                                        "Ziel + psolC"]

    compare_complete_algorithms_LTLbenchmarks(
        algorithms_partial_zielonka_specific,
        specific_generator,
        1,
        preprocess=[None] * len(labels_partial_zielonka_specific),
        iterations=4,
        step=1,
        check_solution=False,
        plot=True,
        path="all_ziel.pdf",
        path_tot="all_ziel_cumulative.pdf",
        title="Comparison of Zielonka + partial solver on LTL benchmarks",
        pkl_path="ziel_combo.pkl",
        labels=labels_partial_zielonka_specific)

    # then only the partials for one dimension

    labels_partial_specific = ["psolB", "psolQ", "psolC"]
    algorithms_partial_specific = [psolB.psolB_set,
                                   psolQ.psolQ,
                                   psolC.psolC]

    compare_partial_algorithms(
        algorithms_partial_specific,
        specific_generator,
        1,
        preprocess=[None] * len(labels_partial_specific),
        iterations=4,
        step=1,
        labels=labels_partial_specific,
        plot=True,
        path_time="all_time.pdf",
        path_proportion="all_prop.pdf",
        path_bulkprop="all_bulkprop.pdf",
        path_tottime="all_tottime.pdf",
        # control_algorithm=zielonka.strong_parity_solver_no_strategies,
        pkl_path="all_data.pkl")


if __name__ == "__main__":
    assert(len(sys.argv) == 2)
    sys.setrecursionlimit(100000)
    if sys.argv[1] == "complete":
        complete()
    if sys.argv[1] == "complete-gen":
        complete_gen()
    elif sys.argv[1] == "partial":
        partial()
    elif sys.argv[1] == "partial-gen":
        partial_gen()
    elif sys.argv[1] == "fatal-abo":
        fatal_abo()
    elif sys.argv[1] == "fatal-abo-complete":
        fatal_abo_complete()
    elif sys.argv[1] == "specific-ex":
        specific_example()
    elif sys.argv[1] == "specific-ex-gen":
        specific_example_gen()
    else:
        assert(False)
    print("Experiments done!")
