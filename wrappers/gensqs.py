#!/usr/bin/env python
import time
import sys
import json
import os

from ase.atoms import Atoms
from icet import ClusterSpace
from icet.tools.structure_generation import generate_sqs

cwd = os.getcwd()

def run_sqs(cs, max_size, include_smaller_cells, target_concentrations, n_steps):
    sqs = generate_sqs(cluster_space=cs,
                       max_size=max_size,
                       include_smaller_cells=include_smaller_cells,
                       target_concentrations=target_concentrations,
                       n_steps=n_steps)
    return sqs

def write_out(sqs):
    sqs_cell = sqs.cell.tolist()
    sqs_positions = sqs.positions.tolist()
    sqs_atomic_numbers = sqs.numbers.tolist()
    sqs_pbc = sqs.pbc.tolist()
    cluster_vector = cs.get_cluster_vector(sqs).tolist()

    data_out = {'structure': {
                    'cell': sqs_cell,
                    'positions': sqs_positions,
                    'atomic_numbers': sqs_atomic_numbers,
                    'pbc': sqs_pbc},
                'cluster_vector': cluster_vector}
    with open(os.path.join(cwd, 'sqs.out'), 'w') as f:
        json.dump(data_out, f, indent=4)

def print_runing_info(t):
    print("==============================================")
    print("Done")
    print("==============================================")
    print("Time elapse: {:} seconds".format(t))


if __name__ == "__main__":
    with open(sys.argv[1]) as json_data:
        data = json.load(json_data)

    cell = data['structure']['cell']
    positions = data['structure']['positions']
    chemical_symbols = data['chemical_symbols']
    pbc = data['structure'].get('pbc', [True, True, True])

    prim = Atoms(cell=cell, positions=positions, pbc=pbc)
    cutoffs = data['cutoffs']

    cs = ClusterSpace(prim, cutoffs, chemical_symbols)

    max_size = data['max_size']
    include_smaller_cells = data['include_smaller_cells']
    n_steps = data.get('n_steps', 3000)
    target_concentrations = data['target_concentrations']

    start_time = time.time()

    # run sqs
    sqs = run_sqs(cs,
            max_size,
            include_smaller_cells,
            target_concentrations,
            n_steps)

    # print runing time
    run_time = time.time() - start_time
    print_runing_info(run_time)

    write_out(sqs)
