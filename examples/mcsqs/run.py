# -*- coding: utf-8 -*-
from __future__ import absolute_import
import aiida
from aiida import orm
from aiida.engine import run_get_node
from aiida.plugins import CalculationFactory

McsqsCalculation = CalculationFactory('atat.mcsqs')

# def run():
#     inputs = {
#         'code': orm.load_code(35),
#         'code_corrdump': orm.load_code(61),
#         'rndstr': orm.load_node(32),
#         'sqscell': orm.load_node(33),
#     }
#     res, node = run_get_node(McsqsCalculation, **inputs)


def run():
    inputs = {
        'code': orm.load_code(2),
        'code_corrdump': orm.load_code(24),
        'rndstr': orm.load_node(48),
        'sqscell': orm.load_node(47),
    }
    res, node = run_get_node(McsqsCalculation, **inputs)


if __name__ == '__main__':
    aiida.load_profile('ce-00')
    run()
