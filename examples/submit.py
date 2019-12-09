# -*- coding: utf-8 -*-
"""Submit a test calculation on localhost.

Usage: verdi run submit.py
"""
from __future__ import absolute_import
from __future__ import print_function
import os
from aiida_ce import tests, helpers
from aiida.plugins import DataFactory, CalculationFactory
from aiida.engine import run

# get code
computer = helpers.get_computer()
code = helpers.get_code(entry_point='ce.train', computer=computer)

# Prepare input parameters
ClusterSpaceData = DataFactory('ce.cluster')
StructureSet = DataFactory('ce.structures')
prim = bulk('Ag')
cs_dict = {
    'cell': prim.cell.tolist(),
    'positions': prim.positions.tolist(),
    'pbc':prim.pbc.tolist(),
    'cutoffs': [13.5, 6.0],
    'chemical_symbols': [['Ag', 'Pd']]
}

cs = ClusterSpaceData(cs_dict)

db_file = os.path.join(tests.TEST_DIR, "input_files", 'ref.db')
db = connect(db_file)
structurelist = [row.toatoms() for row in db.select('natoms<=8')]
energies = [row.mixing_energy for row in db.select('natoms<=8')]
structures = StructureSet(structurelist=structurelist)
structures.set_energies(numpy.array(energies))

inputs = {
    'code': ce_train_code,
    'structures': structures,
    'cluster_space': cs,
    'fit_method': Str('lasso'),
    'metadata': {
        'options': {
            'max_wallclock_seconds': 300,
        },
    },
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('ce'), **inputs)
result = run(CalculationFactory('ce'), **inputs)
