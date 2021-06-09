# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from ase import Atom
from ase.build import bulk
from icet import ClusterSpace
from icet.tools.structure_generation import (generate_sqs,
                                             generate_sqs_from_supercells,
                                             generate_sqs_by_enumeration,
                                             generate_target_structure)

from icet.input_output.logging_tools import set_log_config
set_log_config(level='INFO')

primitive_structure = bulk('Au')
cs = ClusterSpace(primitive_structure, [8.0, 4.0], ['Au', 'Pd'])
target_concentrations = {'Au': 0.5, 'Pd': 0.5}

# sqs = generate_sqs(cluster_space=cs,
#                    max_size=8,
#                    target_concentrations=target_concentrations)
# print('Cluster vector of generated structure:', cs.get_cluster_vector(sqs))

supercells = [primitive_structure.repeat((1, 2, 4))]
sqs = generate_sqs_from_supercells(cluster_space=cs,
                                   supercells=supercells,
                                   n_steps=10000,
                                   target_concentrations=target_concentrations)
print(('Cluster vector of generated structure:', cs.get_cluster_vector(sqs)))
