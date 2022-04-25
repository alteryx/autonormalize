from os import path

from setuptools import find_packages, setup

dirname = path.abspath(path.dirname(__file__))
with open(path.join(dirname, 'README.md')) as f:
    long_description = f.read()

setup(
    name='autonormalize',
    version='2.0.1',
    description='a library for automated table normalization',
    url='https://github.com/alteryx/autonormalize',
    license='BSD 3-clause',
    author='Alteryx, Inc.',
    author_email='support@featurelabs.com',
    classifiers=[
         'Development Status :: 3 - Alpha',
         'Intended Audience :: Developers',
         'Programming Language :: Python :: 3',
         'Programming Language :: Python :: 3.7',
         'Programming Language :: Python :: 3.8',
         'Programming Language :: Python :: 3.9',
    ],
    install_requires=open('requirements.txt').readlines(),
    tests_require=open('test-requirements.txt').readlines(),
    python_requires='>=3.7, <4',
    test_suite='autonormalize/tests',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "featuretools_plugin": [
            'autonormalize = autonormalize',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
)
