# -*- coding: utf-8 -*-
"""AtatMcsqs parser"""
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida import orm

AtatMcsqsCalculation = CalculationFactory('atat.mcsqs')


class AtatMcsqsParser(Parser):
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
        super().__init__(node)
        if not issubclass(node.process_class, AtatMcsqsCalculation):
            raise exceptions.ParsingError(
                'Can only parse AtatMcsqsCalculation')

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.
        """

        # Check that folder content is as expected
        output_bestsqs_filename = self.node.get_option(
            'output_bestsqs_filename')
        output_bestcorr_filename = self.node.get_option(
            'output_bestcorr_filename')

        # add output node
        bestsqs_content = self.retrieved.get_object_content(
            output_bestsqs_filename)
        bestsqs = self.parse_bestsqs(bestsqs_content)
        self.out('bestsqs', bestsqs)

        bestcorr_content = self.retrieved.get_object_content(
            output_bestcorr_filename)
        bestcorr = self.parse_bestcorr(bestcorr_content)
        self.out('bestcorr', bestcorr)

    @staticmethod
    def parse_bestsqs(content: str) -> orm.StructureData:
        """parse bestsqs output content"""
        data_lines = content.split('\n')

        cell = []
        for line in data_lines[3:6]:
            cell.append([float(i) for i in line.split()[:3]])

        sqs = orm.StructureData(cell=cell)

        for line in data_lines[6:]:
            if line.strip() != '':
                position = tuple(float(i) for i in line.split()[:3])
                element = line.split()[-1]
            sqs.append_atom(position=position, symbols=element)

        return sqs

    @staticmethod
    def parse_bestcorr(content: str) -> orm.Float:
        """parse bestcorr"""
        for line in content.split('\n'):
            if 'Objective_function' in line:
                obj_fun = line.split('=')[-1]

        if 'Perfect_match' in obj_fun:
            ret = orm.Float(.0)
        else:
            ret = orm.Float(float(obj_fun))

        return ret
