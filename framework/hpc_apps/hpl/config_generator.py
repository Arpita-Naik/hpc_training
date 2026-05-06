def generate_hpl_dat(parser, output_path):
    problem = parser.get_problem()
    grid = parser.get_process_grid()

    Ns = problem["Ns"]
    NB = problem["NB"]

    P = grid["P"]
    Q = grid["Q"]

    content = f"""HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout)
1            # of problems sizes (N)
{Ns}         Ns
1            # of NBs
{NB}         NBs
0            PMAP process mapping (0=Row-major)
1            # of process grids (P x Q)
{P}          Ps
{Q}          Qs
16.0         threshold
1            # of panel fact
2            PFACTs
1            # of recursive stopping criterium
4            NBMINs
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
2            RFACTs
1            # of broadcast
1            BCASTs
1            # of lookahead depth
0            DEPTHs
2            SWAP
64           swapping threshold
0            L1 in
0            U  in
1            Equilibration
8            memory alignment
"""

    with open(output_path, "w") as f:
        f.write(content)

    return output_path