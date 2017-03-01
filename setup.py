from setuptools import setup
import yaml

nimbus = yaml.load(open('.nimbus.yml', 'r'))

setup(
    name='heighliner',
    version=nimbus['version'],
    packages=['heighliner'],
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'testinfra',
        'pytest-xdist'
    ],
    entry_points='''
        [console_scripts]
        heighliner=heighliner.heighliner:cli
    ''',
    test_suite='nose.collector',
    tests_require=['nose'],
)
