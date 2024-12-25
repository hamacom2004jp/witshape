.. -*- coding: utf-8 -*-

********************************
Developer Information
********************************

This section describes the steps to build a development environment for witshape.

How to install the project
==============================

To install the project, follow these steps:

1. Clone project:

    .. code-block:: bash

        git clone https://github.com/hamacom2004jp/witshape.git

2. Go to the project directory:

    .. code-block:: bash

        cd witshape

3. Create a virtual environment for your project:

    .. code-block:: bash

        python -m venv .venv
        . .venv/bin/activate

4. Install project dependencies:

    .. code-block:: bash

        python.exe -m pip install --upgrade pip
        pip install -r requirements.txt

5. Build the project:

    .. code-block:: bash

        sphinx-apidoc -F -o docs_src/resources witshape
        sphinx-build -b html docs_src docs
        python -m collectlicense --out witshape/licenses --clear
        python setup.py sdist
        python setup.py bdist_wheel

.. sphinx-build -b gettext docs_src docs_build
.. sphinx-intl update -p docs_build -l en
        
How to commit a module
=========================

If you are willing to cooperate in the development, please follow these guidelines:

1. Create a new branch:

    .. code-block:: bat

        git checkout -b feature/your-feature

2. Make your changes and commit!:

    .. code-block:: bat

        git commit -m "Add your changes"

3. Push to the branch you created:

    .. code-block:: bat

        git push origin feature/your-feature

4. Create a pull request.
