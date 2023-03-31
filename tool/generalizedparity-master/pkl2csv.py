import pickle


def timetable(game_parameters, x, y, z, algorithms, psolvers, filename):
    f = open(filename, "w")
    f.write("benchmark name; number of vertices; number of priorities;")
    f.write(";".join(algorithms) + ";" +
            ";".join(map(lambda s: s + " (proportion);" + s + " (time)",
                     psolvers)) + "\n")

    def to_string(a):
        if a >= 60.0 or abs(a - 60.0) <= 2.0:
            return "T/O"
        else:
            return format(a, "09.5f").replace(".", ",")

    for j in range(len(x[0])):
        (name, n, prts) = game_parameters[j]
        f.write(name + ";")
        f.write(str(n) + ";")
        f.write(str(prts) + ";")
        f.write(";".join([to_string(x[i][j]) for i in range(len(x))]))
        f.write(";")
        f.write(";".join([(format(z[i][j], "06.2f").replace(".", ",") +
                           ";" +
                           to_string(y[i][j])) for i in range(len(z))]))
        f.write("\n")
    f.close()


def main():
    # First, we deal with parity games
    psolvers = ["psolB", "psolQ", "psolC"]
    f = open("all_data.pkl", "r")
    (game_parameters, _, y, z) = pickle.load(f)
    algorithms = ["Zielonka",
                  "Ziel + psolB",
                  "Ziel + psolQ",
                  "Ziel + psolC"]
    f = open("ziel_combo.pkl", "r")
    (_, _, x) = pickle.load(f)
    timetable(game_parameters, x, y, z, algorithms,
              psolvers, "onedim.csv")
    # Then, we deal with generalized parity games
    psolvers = ["psolB", "psolQ", "psolC"]
    f = open("allgen_data.pkl", "r")
    (game_parameters, _, y, z) = pickle.load(f)
    algorithms = ["Gen Zielonka",
                  "Gen Ziel + Gen psolB",
                  "Gen Ziel + Gen psolQ",
                  "Gen Ziel + Gen psolC"]
    f = open("genziel_combo.pkl", "r")
    (_, _, x) = pickle.load(f)
    timetable(game_parameters, x, y, z, algorithms,
              psolvers, "gen.csv")
    # Finally, we look at hard examples
    psolvers = ["psolB", "psolQ", "psolC"]
    f = open("abo_part.pkl", "r")
    (game_parameters, _, y, z) = pickle.load(f)
    algorithms = ["Zielonka",
                  "Ziel + psolB",
                  "Ziel + psolQ",
                  "Ziel + psolC"]
    f = open("abo_ziel.pkl", "r")
    (_, _, x) = pickle.load(f)
    timetable(game_parameters, x, y, z, algorithms,
              psolvers, "abo.csv")


if __name__ == "__main__":
    main()
