""" Tests for calculations
"""
import numpy

def test_enum_process(ce_enum_code):
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida.engine import run
    from aiida.orm import StructureData, List, Int

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
