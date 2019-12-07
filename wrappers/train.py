#!/usr/bin/env python
import time
import sys
import json

from ase.atoms import Atoms
from ase.db import connect
from icet import (ClusterSpace, StructureContainer,
                  CrossValidationEstimator, ClusterExpansion)

# def train(sc):
#     return ce

def create_structurelist(cells, positions, atomic_numbers, nframes):
    # return a list of ase structures
    # return ,
    pass

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
    with open(os.path.join(cwd, 'positiosn.raw'), 'rb') as f:
        positions = numpy.loadtxt(f)
    with open(os.path.join(cwd, 'atomic_numbers.raw'), 'rb') as f:
        atomic_numbers = numpy.loadtxt(f)
    with open(os.path.join(cwd, 'nframes.raw'), 'rb') as f:
        nframes = numpy.loadtxt(f)
    with open(os.path.join(cwd, 'energies.raw'), 'rb') as f:
        energies = numpy.loadtxt(f)

    structurelist = create_structurelist(cells
                        positions,
                        atomic_numbers,
                        nframes)

    cv_list = [cs.get_cluster_vector(s) for s in structurelist]

    fit_method = data.get('fit_method', 'lasso')
    # start_time = time.time()
    opt = CrossValidationEstimator(fit_data=(cv_list, energies),
                                   fit_method='lasso')
    opt.validate()
    opt.train()

    ce = ClusterExpansion(cluster_space=cs, parameters=opt.parameters, metadata=opt.summary)
    # ce = train(sc, fit_method)
    ce.write('mixing_energy.ce')
    # run_time = time.time() -  start_time

    print_runing_info(run_time)
