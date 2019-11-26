[![Build Status](https://travis-ci.org/unkcpz/aiida-ce.svg?branch=master)](https://travis-ci.org/unkcpz/aiida-ce)
[![Coverage Status](https://coveralls.io/repos/github/unkcpz/aiida-ce/badge.svg?branch=master)](https://coveralls.io/github/unkcpz/aiida-ce?branch=master)
[![Docs status](https://readthedocs.org/projects/aiida-ce/badge)](http://aiida-ce.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/aiida-ce.svg)](https://badge.fury.io/py/aiida-ce)

# aiida-ce

Cluster Expansion

This plugin is the default output of the
[AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter),
intended to help developers get started with their AiiDA plugins.

Plugins templated using the plugin cutter

* include a calculation, parser and data type as well as an example of
  how to submit a calculation
* include basic regression tests using the [pytest](https://docs.pytest.org/en/latest/) framework ( (submitting a calculation, ...)
* can be directly pip-installed (and are prepared for submisson to [PyPI](https://pypi.org/)
* include a documentation template ready for [Read the Docs](http://aiida-diff.readthedocs.io/en/latest/)
* come with [Travis CI](https://travis-ci.org) configuration - enable it to run tests and check test coverage at every commit
* come with pre-commit hooks that sanitize coding style and check for syntax errors - enable via `pre-commit install`

For more information on how to take advantage of these features,
see the [developer guide](https://aiida-diff.readthedocs.io/en/latest/developer_guide) of your plugin.


## Features

 * Add input files using `SinglefileData`:
   ```python
   SinglefileData = DataFactory('singlefile')
   inputs['file1'] = SinglefileData(file='/path/to/file1')
   inputs['file2'] = SinglefileData(file='/path/to/file2')
   ```

 * Specify command line options via a python dictionary and `DiffParameters`:
   ```python
   d = { 'ignore-case': True }
   DiffParameters = DataFactory('ce')
   inputs['parameters'] = DiffParameters(dict=d)
   ```

 * `DiffParameters` dictionaries are validated using [voluptuous](https://github.com/alecthomas/voluptuous).
   Find out about supported options:
   ```python
   DiffParameters = DataFactory('ce')
   print(DiffParameters.schema.schema)
   ```

## Installation

```shell
pip install aiida-ce
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```


## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:
```shell
verdi daemon start         # make sure the daemon is running
cd examples
verdi run submit.py        # submit test calculation
verdi process list -a  # check status of calculation
```

The plugin also includes verdi commands to inspect its data types:
```shell
verdi data ce list
verdi data ce export <PK>
```

## Development

```shell
git clone https://github.com/unkcpz/aiida-ce .
cd aiida-ce
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-ce.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT


## Contact

morty.yu@yahoo.com

