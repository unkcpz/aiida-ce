""" Tests for calculations
"""
import numpy
import os

from aiida_ce import tests

from aiida.plugins import CalculationFactory, DataFactory
from aiida.engine import run
from aiida.orm import StructureData, List, Int, \
                        Dict, Bool, Str

from ase.build import bulk
from ase.db import connect

def test_train_process(ce_train_code):
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

    result = run(CalculationFactory('ce.train'), **inputs)
    assert 'model' in result

def test_enum_process(ce_enum_code):
    StructureSet = DataFactory('ce.structures')

    from ase.build import bulk
    prim = bulk('Ag')
    structure = StructureData(ase=prim)
    chemical_symbols = List(list=[['Au', 'Pd']])

    # set up calculation
    inputs = {
        'code': ce_enum_code,
        'structure': structure,
        'chemical_symbols': chemical_symbols,
        'min_volume': Int(1),
        'max_volume': Int(4),
        'metadata': {
            'options': {
                'max_wallclock_seconds': 30
            },
        },
    }

    result = run(CalculationFactory('ce.genenum'), **inputs)
    structures = result['enumerate_structures']
    structure0 = structures.get_structure(0).get_ase()

    assert numpy.allclose(structure0.cell, prim.cell)
    assert numpy.allclose(structure0.positions, prim.positions)
    assert isinstance(structures, StructureSet)

    assert result['number_of_structures'] == 10

def test_sqs_process(ce_sqs_code):
    prim = bulk('Au')
    structure = StructureData(ase=prim)
    chemical_symbols = List(list=[['Au', 'Pd']])

    # set up calculation
    inputs = {
        'code': ce_sqs_code,
        'structure': structure,
        'chemical_symbols': chemical_symbols,
        'pbc': List(list=[True, True, True]),
        'cutoffs': List(list=[5.0]),
        'max_size': Int(8),
        'include_smaller_cells': Bool(True),
        'n_steps': Int(2000),
        'target_concentrations': Dict(dict={'Au': 0.5, 'Pd': 0.5}),
        'metadata': {
            'options': {
                'max_wallclock_seconds': 30,
            },
        }
    }

    result = run(CalculationFactory('ce.gensqs'), **inputs)
    assert 'sqs' in result
    assert 'cluster_space' in result

    sqs = result['sqs'].get_ase()
    assert sqs.get_number_of_atoms() == 8
