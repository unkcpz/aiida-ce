#!/usr/bin/env python
import time
import sys
import json
import os
import numpy

from ase.atoms import Atoms
from ase.db import connect
from icet import (ClusterSpace, StructureContainer,
                  CrossValidationEstimator, ClusterExpansion)

cwd = os.getcwd()
# def train(sc):
#     return ce

def create_structurelist(cells, positions, atomic_numbers, natoms):
    # inputs are numpy.ndarray
    # return a list of ase structures
    structurelist = []
    cnframes = numpy.cumsum(natoms) - natoms
    for i, n in enumerate(natoms):
        cell = cells[3*i:3*(i+1)]

        idx = cnframes[i]
        pos = positions[idx:idx+n]
        numbers = atomic_numbers[idx:idx+n]

        structure = Atoms(cell=cell, positions=pos, numbers=numbers, pbc=True)
        structurelist.append(structure)

    return structurelist


def print_runing_info(t):
    # TODO: Add more infos
    print("==============================================")
    print("Done")
    print("==============================================")
    print("Time elapse: {:} seconds".format(t))

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = json.load(f)

    cell = data['structure']['cell']
    positions = data['structure']['positions']
    chemical_symbols = data['chemical_symbols']
    pbc = data['structure'].get('pbc', [True, True, True])

    prim = Atoms(cell=cell, positions=positions, pbc=pbc)
    cutoffs = data['cutoffs']

    cs = ClusterSpace(prim, cutoffs, chemical_symbols)

    sc = StructureContainer(cluster_space=cs)

    # read cells, positions, atomic_numbers, nframes and energies
    with open(os.path.join(cwd, 'cells.raw'), 'rb') as f:
        cells = numpy.loadtxt(f)
    with open(os.path.join(cwd, 'coordinates.raw'), 'rb') as f:
        positions = numpy.loadtxt(f)
    with open(os.path.join(cwd, 'atomic_numbers.raw'), 'rb') as f:
        atomic_numbers = numpy.loadtxt(f, dtype=int)
    with open(os.path.join(cwd, 'natoms.raw'), 'rb') as f:
        natoms = numpy.loadtxt(f, dtype=int)
    with open(os.path.join(cwd, 'energies.raw'), 'rb') as f:
        energies = numpy.loadtxt(f)

    structurelist = create_structurelist(cells,
                        positions,
                        atomic_numbers,
                        natoms)

    cv_list = numpy.array([cs.get_cluster_vector(s) for s in structurelist])

    fit_method = data.get('fit_method', 'lasso')
    start_time = time.time()
    opt = CrossValidationEstimator(fit_data=(cv_list, energies),
                                   fit_method='lasso')
    opt.validate()
    opt.train()

    ce = ClusterExpansion(cluster_space=cs, parameters=opt.parameters, metadata=opt.summary)
    ce.write('model.ce')
    run_time = time.time() -  start_time

    print_runing_info(run_time)
