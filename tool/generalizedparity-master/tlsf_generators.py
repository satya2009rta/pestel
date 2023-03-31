import file_handler

_ltl2dba_pgs = ["ltl2dba" + format(i, "02") + ".tlsf.pg"
                for i in range(1, 28)]
_ltl2dba_gpgs = ["ltl2dba" + format(i, "02") + ".tlsf.gpg"
                 for i in range(1, 28)]
_ltl2dpa_pgs = ["ltl2dpa" + format(i, "02") + ".tlsf.pg"
                for i in range(1, 22)]
_ltl2dpa_gpgs = ["ltl2dpa" + format(i, "02") + ".tlsf.gpg"
                 for i in range(1, 22)]


def ltl2dba_pg_gen_n():
    return len(_ltl2dba_pgs)


def ltl2dba_gpg_gen_n():
    return len(_ltl2dba_gpgs)


def ltl2dpa_pg_gen_n():
    return len(_ltl2dpa_pgs)


def ltl2dpa_gpg_gen_n():
    return len(_ltl2dpa_gpgs)


def ltl2dba_pg(i):
    assert(i < len(_ltl2dba_pgs))
    return file_handler.load_from_file("examples/" + _ltl2dba_pgs[i])


def ltl2dba_gpg(i):
    assert(i < len(_ltl2dba_gpgs))
    return file_handler.load_generalized_from_file("examples/" + _ltl2dba_gpgs[i])


def ltl2dpa_pg(i):
    assert(i < len(_ltl2dpa_pgs))
    return file_handler.load_from_file("examples/" + _ltl2dpa_pgs[i])


def ltl2dpa_gpg(i):
    assert(i < len(_ltl2dpa_gpgs))
    return file_handler.load_generalized_from_file("examples/" + _ltl2dpa_gpgs[i])


def main():
    print(str(ltl2dba_pg(2)))
    print(str(ltl2dpa_gpg(5)))


if __name__ == "__main__":
    main()
