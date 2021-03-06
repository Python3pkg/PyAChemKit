"""
This is a command-line tool for generating `.chem` files using 
the :py:func:`~achemkit.randomnet.Linear` random reaction network algorithm.

usage: chem_linear.py [options]

Options:

  -h, --help                      show this help message and exit
  -o OUTFILE, --outfile OUTFILE   write to OUTFILE in .chem format (if ommited, use stdout)
  -a NATOMS, --natoms NATOMS      number of atoms
  -l LENGTH, --length LENGTH      maximum number of atoms per molecule
  -f PFORM, --pform PFORM         probability of bonding
  -b PBREAK, --pbreak PBREAK      probability of breaking
  -u, --undirected                undirected molecules
  -d, --directed                  directed molecules
  -t RATES, --rates RATES         possible reaction rates
  -s SEED, --seed SEED            pseudo-random seed
"""

import random
import argparse
import sys

from achemkit import Linear 

def main():
    parser = argparse.ArgumentParser(description="Generates `.chem` using Linear algorithm.")
    parser.add_argument("-o", "--outfile", action="store", type=argparse.FileType('w'), help="write to OUTFILE in .chem format (if ommited, use stdout)", metavar="OUTFILE")
    parser.add_argument("-a", "--natoms", action="store", type=int, help="number of atoms", default=2)
    parser.add_argument("-l", "--length", action="store", type=int, help="maximum number of atoms per molecule", default=5)
    parser.add_argument("-f", "--pform", action="store", type=float,  help="probability of bonding", default=0.25)
    parser.add_argument("-b", "--pbreak", action="store", type=float,  help="probability of breaking", default=0.1)
    parser.add_argument("-u", "--undirected", action="store_false", dest="directed",  help="undirected molecules")
    parser.add_argument("-d", "--directed", action="store_true",  help="directed molecules", default=True)
    parser.add_argument("-t", "--rates", action="store", type=int,  help="possible reaction rates", default=[1.0])
    parser.add_argument("-s", "--seed", action="store", type=int, help="pseudo-random seed", default=None)
    args = parser.parse_args()
    
    rates = [float(x) for x in args.rates]
    
    #strip defaults
    if len(rates) > 1:
        rates = rates[1:]    
    
    rng = random.Random(args.seed)
    #import cProfile
    #cProfile.run("""
    net = Linear(args.natoms, args.length, args.pform, args.pbreak, args.directed, rates, rng=rng)
    #""".strip())
    
    chemstr = """#Linear reaction network
# natoms = {0}
# length = {1}
# pform = {2}
# pbreak = {3}
# direct = {4}
# rates = {5}
# seed = {6}
    
""".format(args.natoms, args.length, args.pform, args.pbreak, args.directed, rates, args.seed)
    chemstr += str(net)
    chemstr += "\n"

    if args.outfile is None:
        #print to standard out
        sys.stdout.write(chemstr)
    else:
        #write to provided filename
        args.outfile.write(chemstr)
        
        
        
if __name__=="__main__":
    main()
