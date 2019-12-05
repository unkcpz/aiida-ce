from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory, DataFactory

EnumCalculation = CalculationFactory('ce.genenum')

class EnumParser(Parser):
    """
    Parser outputs of genenum.
    coordinates.raw, cells.raw, atomic_numbers.raw, nframes.raw
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a EnumCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        from aiida.common import exceptions
        super(EnumParser, self).__init__(node)
        if not issubclass(node.process_class, EnumCalculation):
            raise exceptions.ParsingError("Can only parse EnumCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.
        """
        import numpy
        from aiida.orm import Int

        StructureSet = DataFactory('ce.structures')

        # Check that folder content is as expected
        output_filename = self.node.get_option('output_filename')

        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename, 'cells.raw']
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to fine '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output node
        self.logger.info("Parsing coordinates.raw, cells.raw, atomic_numbers.raw, nframes.raw")
        with self.retrieved.open('cells.raw', 'rb') as handle:
            cells = numpy.loadtxt(handle)
        with self.retrieved.open('coordinates.raw', 'rb') as handle:
            positions = numpy.loadtxt(handle)
        with self.retrieved.open('atomic_numbers.raw', 'rb') as handle:
            atomic_numbers = numpy.loadtxt(handle, dtype=int)
        with self.retrieved.open('nframes.raw', 'rb') as handle:
            nframes = numpy.loadtxt(handle, dtype=int)

        out = StructureSet()
        out.from_raws(cells,
                    positions,
                    atomic_numbers,
                    nframes)
        self.out('enumerate_structures', out)
        self.out('number_of_structures', Int(len(nframes)))

        return ExitCode(0)
