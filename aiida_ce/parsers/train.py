from  aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import SinglefileData

TrainCalculation = CalculationFactory('ce.train')

class TrainParser(Parser):
    """
    Parser outputs of train calculation
    parse file model.ce
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a EnumCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        from aiida.common import exceptions
        super(TrainParser, self).__init__(node)
        if not issubclass(node.process_class, TrainCalculation):
            raise exceptions.ParsingError("Can only parse TrainCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.
        """
        # Check that folder content is as expected
        output_filename = self.node.get_option('output_filename')

        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename, 'model.ce']
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to fine '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output file
        self.logger.info("Parsing '{}'".format('model.ce'))
        with self.retrieved.open('model.ce', 'rb') as handle:
            model_node = SinglefileData(file=handle)
        self.out('model', model_node)

        return ExitCode(0)
