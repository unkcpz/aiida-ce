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
code = helpers.get_code(entry_point='ce', computer=computer)

# Prepare input parameters
DiffParameters = DataFactory('ce')
parameters = DiffParameters({'ignore-case': True})

SinglefileData = DataFactory('singlefile')
file1 = SinglefileData(
    file=os.path.join(tests.TEST_DIR, "input_files", 'file1.txt'))
file2 = SinglefileData(
    file=os.path.join(tests.TEST_DIR, "input_files", 'file2.txt'))

# set up calculation
inputs = {
    'code': code,
    'parameters': parameters,
    'file1': file1,
    'file2': file2,
    'metadata': {
        'description': "Test job submission with the aiida_ce plugin",
    },
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('ce'), **inputs)
result = run(CalculationFactory('ce'), **inputs)

computed_diff = result['ce'].get_content()
print("Computed diff between files: \n{}".format(computed_diff))
