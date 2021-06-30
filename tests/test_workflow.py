# -*- coding: utf-8 -*-
"""tests of ce workflows"""
# pylint: disable=redefined-outer-name
import pytest
from aiida.engine.launch import run_get_node
from aiida import orm
from aiida.plugins import WorkflowFactory, DataFactory

ClusterSpaceData = DataFactory('cluster_space')
ClusterExpansionData = DataFactory('cluster_expansion')
ConstructClusterExpansion = WorkflowFactory('construct_ce')
IcetMcsqsWorkChain = WorkflowFactory('icet.mcsqs')

# ConstructClusterExpansion


@pytest.mark.usefixtures('clear_database_before_test')
def test_construct_ce_default(structure_db, primitive_structure):
    """test default"""
    inputs = {
        'cluster_space': {
            'primitive_structure': primitive_structure,
            'cutoffs': orm.List(list=[13.5, 6.0, 5.5]),
            'chemical_symbols': orm.List(list=['Ag', 'Pd']),
        },
        'structure_db': structure_db,
        'fit_data_key': orm.Str('mixing_energy'),
        'fit_method': orm.Str('lasso')
    }

    res, node = run_get_node(ConstructClusterExpansion, **inputs)

    assert node.is_finished_ok
    assert 'cluster_expansion' in res
    assert isinstance(res['cluster_expansion'], ClusterExpansionData)


@pytest.mark.usefixtrue('clear_database_before_test')
def test_icet_sqs_default():
    """test default"""
    from ase.build import bulk

    primitive_structure = orm.StructureData(ase=bulk('Au'))

    inputs = {
        'cluster_space': {
            'primitive_structure': primitive_structure,
            'cutoffs': orm.List(list=[8.0, 4.0]),
            'chemical_symbols': orm.List(list=[['Au', 'Pd']]),
        },
        'supercell': orm.StructureData(ase=bulk('Au').repeat((1, 2, 4))),
        'n_steps': orm.Int(1000),
        'random_seed': orm.Int(1234),
        'target_concentrations': orm.Dict(dict={
            'Au': 0.5,
            'Pd': 0.5
        })
    }

    res, node = run_get_node(IcetMcsqsWorkChain, **inputs)

    assert node.is_finished_ok
    assert 'output_cluster_vector' in res
    assert 'output_structure' in res
