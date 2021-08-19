Install
*******

AutoNormalize is available for Python 3.7 and 3.8. The recommended way to install Featuretools is using ``pip`` ::

    python -m pip install featuretools[autonormalize]


.. _graphviz:

Installing Graphviz
-------------------

In order to use plotting you will need to install the graphviz library.

pip users::

    pip install graphviz
    
conda users::

    conda install -c conda-forge python-graphviz

Ubuntu::

    sudo apt install graphviz
    pip install graphviz

Mac OS::

    brew install graphviz
    pip install graphviz

Windows:

- Install according to your package manager::

    # conda
    conda install -c conda-forge python-graphviz
    # pip
    pip install graphviz

- If you installed graphviz with ``pip``, install graphviz.exe from the `official source <https://graphviz.org/download/#windows>`_


Install from Source
-------------------

To install autonormalize from source, clone the repository from `github
<https://github.com/alteryx/autonormalize>`_::

    git clone https://github.com/alteryx/autonormalize.git
    cd autonormalize
    python setup.py install

or use ``pip`` locally if you want to install all dependencies as well::

    pip install .

You can view the list of all dependencies within the ``extras_require`` field
of ``setup.py``.



Development
-----------
Before making contributing to the codebase, please follow the guidelines `here <https://github.com/alteryx/autonormalize/blob/main/contributing.md>`_

Virtualenv
~~~~~~~~~~
We recommend developing in a `virtualenv <https://virtualenvwrapper.readthedocs.io/en/latest/>`_::

    mkvirtualenv autonormalize

Install development requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run::

    make installdeps

Test
~~~~
.. note::

    In order to the run the autonormalize tests you will need to have graphviz installed as described above.

Run autonormalize tests::

    make test

Before committing make sure to run linting in order to pass CI::

    make lint

Some linting errors can be automatically fixed by running the command below::

    make lint-fix


Build Documentation
~~~~~~~~~~~~~~~~~~~
Build the docs with the commands below::

    cd docs/

    # small changes
    make html

    # rebuild from scatch
    make clean html

.. note ::

    The autonormalize library must be import-able to build the docs.
