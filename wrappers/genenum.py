#!/usr/bin/env python
import json
import sys
import os
import numpy
import time

from icet.tools import enumerate_structures
from ase.atoms import Atoms

start_time = time.time()

cwd = os.getcwd()

with open(sys.argv[1]) as json_data:
    data = json.load(json_data)

# cell, positions, and chemical_symbols must be set
cell = data['structure']['cell']
positions = data['structure']['positions']
chemical_symbols = data['chemical_symbols']

# if not read, set to default value
pbc = data['structure'].get('pbc', [True, True, True])
sizes = data.get('sizes', [1])
concentration_restrictions = data.get('concentration_restrictions', None)

# TODO: random export of certain numbers of structures
structurelist = []
prim = Atoms(cell=cell, positions=positions, pbc=pbc)

# Make sure the output files is removed
try:
    os.remove(os.path.join(cwd, 'coordinates.raw'))
    os.remove(os.path.join(cwd, 'cells.raw'))
    os.remove(os.path.join(cwd, 'atomic_numbers.raw'))
    os.remove(os.path.join(cwd, 'nframes.raw'))
except:
    pass

# open files on 'append' mode to write
coor_raw = open(os.path.join(cwd, 'coordinates.raw'), 'a')
cell_raw = open(os.path.join(cwd, 'cells.raw'), 'a')
atomic_number_raw = open(os.path.join(cwd, 'atomic_numbers.raw'), 'a')
nframes = []
for structure in enumerate_structures(structure=prim, sizes=sizes,
                                    chemical_symbols=chemical_symbols,
                                    concentration_restrictions=concentration_restrictions):
    #
    numpy.savetxt(coor_raw, structure.positions)
    numpy.savetxt(cell_raw, structure.cell)
    numpy.savetxt(atomic_number_raw, structure.numbers, fmt='%d')
    nframes.append(structure.get_number_of_atoms())

coor_raw.close()
cell_raw.close()
atomic_number_raw.close()

with open(os.path.join(cwd, 'nframes.raw'), 'w') as f:
    numpy.savetxt(f, numpy.array(nframes), fmt='%d')

print("==============================================")
print("Done")
print("==============================================")
print("Time elapse: {:} seconds", time.time()-start_time)
# TODO: writing the input info and record the running step info
