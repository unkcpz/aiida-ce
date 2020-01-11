"""Compute a band structure with Quantum ESPRESSO

Uses the PwBandStructureWorkChain provided by aiida-quantumespresso.
"""
from aiida.engine import submit
from aiida.orm import Code
from aiida.plugins import WorkflowFactory

PwBandStructureWorkChain = WorkflowFactory('ce.band_structure')

def test_workflow():
    results = submit(
        PwBandStructureWorkChain,
        code=Code.get_from_string("pw-6.4@labcmp"),
        structure=load_node(2),  # REPLACE <PK>
    )
