import sys

sys.path.append('./../../tool/generalizedparity-master/')
sys.path.append('tool/generalizedparity-master/')
sys.path.append('generalizedparity-master/')
sys.path.append('../generalizedparity-master/')
sys.path.append('../../generalizedparity-master/')
sys.path.append('../../../generalizedparity-master/')
sys.path.append('../../../../generalizedparity-master/')

import file_handler as io
import generalized_parity_recursive as gpr
import generalized_zielonka_with_partials as genpartial

filename = sys.argv[1]
print (filename)
g = io.load_generalized_from_file(filename)

if (len(sys.argv) == 3):
    method = sys.argv[2]
    if method == "1":
        print "1:Gen Ziel + Gen psolB"
        W0, W1 = genpartial.generalized_with_psolB(g)
    elif method == "2":
        print "2:Gen Ziel + Gen psolQ"
        W0, W1 = genpartial.generalized_zielonka_with_psolQ(g)
    elif method == "3":
        print "3:Gen Ziel + Gen psolC"
        W0, W1 = genpartial.generalized_zielonka_with_psolC(g)
    else:
        print "0:Gen Zielonka"
        W0, W1 = gpr.generalized_parity_solver(g)
else:
    print "0:Gen Zielonka"
    W0, W1 = gpr.generalized_parity_solver(g)

init = ""
if 0 in W0:
    init = " (INIT)"
print "#winning_vertices:"+str(len(W0))+"/"+str(len(W0)+len(W1))+init



import file_handler as io
import generalized_zielonka_with_partials as genpartial
g = io.load_generalized_from_file(<gpg_file_path>)
W0, W1 = genpartial.generalized_with_psolB(g)
print(len(W0))