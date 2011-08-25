#!/usr/bin/env python
version = '0.1'


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path,
        namespace_packages=['scikits'])
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True,
    )
    config.add_subpackage('scikits.permuttest')
    config.add_data_files('scikits/__init__.py')
    return config


def setup_package():
    from numpy.distutils.core import setup
    setup(
        name='scikits.permuttest',
        version=version,
        maintainer='Alessandro Daducci and Alexis Roche',
        maintainer_email='name.surname@epfl.ch',
        description='Statistical permutation tests',
        url='http://www.scipy.org',
        license='BSD',
        configuration=configuration,
        #install_requires=['numpy >= 1.0.2',],
    )
    return

if __name__ == '__main__':
    setup_package()
