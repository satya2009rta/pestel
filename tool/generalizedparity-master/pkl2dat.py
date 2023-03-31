import pickle

f = open("all_data.pkl", "r")
(game_parameters, x, y, z) = pickle.load(f)
avg = sum([prts for (_, prts) in game_parameters]) /\
    float(len(game_parameters))
print("average no. of colours = " + str(avg))

algorithms = ["psol", "psolB", "psolB Buchi-coBuchi", "psolQ", "psolC"]
print("algorithms    " + "    ".join(algorithms))
for j in range(len(z[0])):
    (n, prts) = game_parameters[j]
    print(str(j + 1) +
          " (n=" + str(n) + ",d=" + str(prts) + ")"
          "    " + "    ".join([format(z[i][j], "06.2f") +
                                " (" + format(y[i][j], "07.3f") + " s)"
                                for i in range(len(z))]))
