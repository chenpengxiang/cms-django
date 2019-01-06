from setuptools import setup, find_packages

setup(
    name='cms-django',
    packages=find_packages(),
    install_requires=['Django',
                      'psycopg2',
                      'pylint',
                      'pylint-django',
                      'pylint_runner'],
)
