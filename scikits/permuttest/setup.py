from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


def configuration(parent_package='', top_path=None):
    config = Configuration('permuttest', parent_package, top_path)
    config.add_data_dir('tests')
    #config.add_extension("_permuttest',
    #    sources=['_permuttest.pyx', 'toto.c'],
    #	 include_dirs=['.'],
    #	 )
    return config

if __name__ == '__main__':
    setup(**configuration(top_path='').todict())
