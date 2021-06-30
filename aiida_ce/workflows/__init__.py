# -*- coding: utf-8 -*-
"""init"""
from aiida import orm
from aiida.plugins import DataFactory
from aiida.engine import WorkChain, calcfunction

ClusterSpaceData = DataFactory('cluster_space')


@calcfunction
def _create_cluster_space(primitive_structure: orm.StructureData,
                          cutoffs: orm.List,
                          chemical_symbols: orm.List) -> ClusterSpaceData:
    """calculation function to create cluster space"""
    cutoffs = cutoffs.get_list()
    chemical_symbols = chemical_symbols.get_list()

    primitive_structure = primitive_structure.get_ase()  # primitive structure

    cs_data = ClusterSpaceData()
    cs_data.set(ase=primitive_structure,
                cutoffs=cutoffs,
                chemical_symbols=chemical_symbols)

    return cs_data
