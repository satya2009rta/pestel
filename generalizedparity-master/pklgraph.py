import pickle
import matplotlib.pyplot as plt

f = open("all_data.pkl", "r")
(game_parameters, x, y, z) = pickle.load(f)

# game_parameters is a list of pairs (a, b)
# a is the size of the game and b is the
# number of priorities
# in (x, y, z), x is the number of nodes (yes, again)
# y contains times of solving benchmarks and
# z contains percentages of node classification

algorithms = ["psol", "psolB", "psolB Buchi-coBuchi", "psolQ", "psolC"]

# we need to compute how many benchmarks there are
bench_count = range(1, len(x) + 1)
# now we need to sort the running times of the algorithms in increasing order
# and add them
solve_times = [sorted(y[i]) for i in range(len(y))]
tot_solve_times = []
for i in range(len(y)):
    cst = []
    total_time = 0
    for j in range(len(x)):
        total_time += solve_times[i][j]
        cst.append(total_time)
    tot_solve_times.append(cst)

plt.grid(True)
plt.title("Cumulative time graph")
plt.xlabel(u'no. of benchmarks')
plt.ylabel(u'total time spent')
plt.yscale("log")  # allows logatithmic y-axis

colors = ['g.', 'r.', 'b.', 'y.', 'c.']

points = []
for i in range(len(algorithms)):
    points.extend(plt.plot(bench_count, tot_solve_times[i],
                  colors[i], label=algorithms[i]))

plt.legend(loc='lower right', handles=points)
plt.savefig("all_tottime.pdf", bbox_inches='tight')
plt.clf()
plt.close()
