from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

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
            arr = numpy.loadtxt(handle)
        self.out('arr_len', Int(len(arr)))
