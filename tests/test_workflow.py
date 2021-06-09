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
IcetSqsWorkChain = WorkflowFactory('icet.sqs')

# ConstructClusterExpansion


@pytest.mark.usefixtures('clear_database_before_test')
def test_construct_ce_default(structure_db, primitive_structure):
    """test default"""
    inputs = {
        'primitive_structure': primitive_structure,
        'structure_db': structure_db,
        'cutoffs': orm.List(list=[13.5, 6.0, 5.5]),
        'chemical_symbols': orm.List(list=['Ag', 'Pd']),
        'fit_data_key': orm.Str('mixing_energy'),
        'fit_method': orm.Str('lasso')
    }

    res, node = run_get_node(ConstructClusterExpansion, **inputs)

    assert node.is_finished_ok
    assert 'cluster_expansion' in res
    assert isinstance(res['cluster_expansion'], ClusterExpansionData)


@pytest.mark.usefixtrue('clear_database_before_test')
def test_icet_sqs_default(cluster_space_aupd, supercell):
    """test default"""
    cluster_space_data = ClusterSpaceData()
    cluster_space_data.set_from_cluster_space(cluster_space_aupd)

    inputs = {
        'cluster_space': cluster_space_data,
        'supercell': supercell,
        'n_steps': orm.Int(1000),
        'random_seed': orm.Int(1234),
        'target_concentrations': orm.Dict(dict={
            'Au': 0.5,
            'Pd': 0.5
        })
    }

    res, node = run_get_node(IcetSqsWorkChain, **inputs)

    assert node.is_finished_ok
    assert 'output_cluster_vector' in res
    assert 'output_structure' in res
