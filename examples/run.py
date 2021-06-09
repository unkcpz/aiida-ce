# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aiida.plugins import WorkflowFactory
from aiida.engine import run_get_node
from aiida import orm

CCE = WorkflowFactory('ce.construct_ce')

inputs = {
    'primitive_structure': orm.load_node(10),
    'structures': orm.load_node(1),
    'cutoffs': orm.List(list=[13.5, 6.0, 5.5]),
    'chemical_symbols': orm.List(list=['Ag', 'Pd']),
    'fit_data_key': orm.Str('mixing_energy'),
    'fit_method': orm.Str('lasso')
}

_, res = run_get_node(CCE, **inputs)
