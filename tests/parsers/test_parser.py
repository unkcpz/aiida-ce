# -*- coding: utf-8 -*-
"""Tests for the parser."""
# pylint: disable=redefined-outer-name
import os

import pytest
from aiida import orm
from aiida.plugins import ParserFactory

from .. import TEST_DIR


@pytest.fixture
def generate_calc_job_node():
    """generate calc_job node """
    def _generate_calc_job_node(entry_point_name, computer, test_name):
        from aiida.plugins.entry_point import format_entry_point_string
        from aiida.common import LinkType

        entry_point = format_entry_point_string('aiida.calculations',
                                                entry_point_name)
        node = orm.CalcJobNode(computer=computer, process_type=entry_point)

        node.set_option('output_bestsqs_filename', 'bestsqs.out')
        node.set_option('output_bestcorr_filename', 'bestcorr.out')
        node.store()

        filepath_folder = os.path.join(TEST_DIR, 'parsers', 'fixtures',
                                       test_name)

        retrieved = orm.FolderData()
        retrieved.put_object_from_tree(filepath_folder)

        retrieved.add_incoming(node,
                               link_type=LinkType.CREATE,
                               link_label='retrieved')
        retrieved.store()

        return node

    return _generate_calc_job_node


def test_mcsqs_default(fixture_localhost, generate_calc_job_node):
    """Test mcsqs output parser"""
    entry_point_calc_job = 'atat.mcsqs'
    entry_point_parser = 'atat.mcsqs'

    node = generate_calc_job_node(entry_point_calc_job, fixture_localhost,
                                  'mcsqs_default')
    parser = ParserFactory(entry_point_parser)

    results, calcfunction = parser.parse_from_node(node,
                                                   store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message

    assert 'bestsqs' in results
    assert 'bestcorr' in results

    assert isinstance(results['bestsqs'], orm.StructureData)
    assert results['bestcorr'] == 0
