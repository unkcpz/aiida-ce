import numpy
import json

from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory, DataFactory
from aiida.orm import Int, List, StructureData

from ase.atoms import Atoms

SqsCalculation = CalculationFactory('ce.gensqs')
ClusterSpaceData = DataFactory('ce.cluster')

class SqsParser(Parser):
    """
    Parser outputs of gensqs.
    parse the file sqs.out
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a EnumCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        from aiida.common import exceptions
        super(SqsParser, self).__init__(node)
        if not issubclass(node.process_class, SqsCalculation):
            raise exceptions.ParsingError("Can only parse SqsCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.
        """

        # Check that folder content is as expected
        output_filename = self.node.get_option('output_filename')

        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename, 'sqs.out']
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to fine '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output node
        self.logger.info("Parsing sqs.out")
        with self.retrieved.open('sqs.out', 'rb') as handle:
            data = json.load(handle)

        cell = data['structure']['cell']
        positions = data['structure']['positions']
        pbc = data['structure']['pbc']
        atomic_numbers = data['structure']['atomic_numbers']
        structure = Atoms(cell=cell, positions=positions, numbers=atomic_numbers, pbc=pbc)
        sqs = StructureData(ase=structure)
        cluster_vector = data['cluster_vector']


        self.out('sqs', sqs)
        self.out('cluster_vector', List(list=cluster_vector))

        calc = self.node
        prim = calc.inputs.structure.get_ase()
        cs = {
            'cell': prim.cell.tolist(),
            'positions': prim.positions.tolist(),
            'pbc': prim.pbc.tolist(),
            'cutoffs': calc.inputs.cutoffs.get_list(),
            'chemical_symbols': calc.inputs.chemical_symbols.get_list(),
        }
        self.out('cluster_space', ClusterSpaceData(cs))

        return ExitCode(0)
