# to build

- make a folder named `build-context_text`.
- get source code.  Either:

    - clone this repository into that folder: `git clone https://github.com/jonathanmorgan/context_text"
    - or (DO THIS) grab the release source tar ball for the release you want to build.

- move the following files into `build-context_text`:

    - context_text/build_files/LICENSE
    - context_text/build_files/MANIFEST.in
    - context_text/build_files/setup.py
    - context_text/README.md

- make sure you have `setuptools`, `wheel`, and `twine` packages installed in the Python environment you are using to build.
- in the `build-context_text` folder:

    - build: `python setup.py sdist bdist_wheel`
    - test upload to test.pypi.org: `python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
    - to install from test: `pip install --index-url https://test.pypi.org/simple/ django-context-text`
    - if all works OK, upload to pypi.org: `python3 -m twine upload dist/*`
    - install using pip and test: `pip install django-context-text`

# More details

- [https://packaging.python.org/tutorials/packaging-projects/](https://packaging.python.org/tutorials/packaging-projects/)
- semantic versioning: [https://semver.org/](https://semver.org/)
- creating releases on github.com: [https://help.github.com/en/github/administering-a-repository/creating-releases](https://help.github.com/en/github/administering-a-repository/creating-releases)
- making your code citable: [https://guides.github.com/activities/citable-code/](https://guides.github.com/activities/citable-code/)
- packaging django apps: [https://docs.djangoproject.com/en/dev/intro/reusable-apps/](https://docs.djangoproject.com/en/dev/intro/reusable-apps/)

## setup.py

- More details on all the options for setup.py: https://packaging.python.org/guides/distributing-packages-using-setuptools/
- Requirements: https://packaging.python.org/discussions/install-requires-vs-requirements/#install-requires-vs-requirements-files

    - Must include hard requirements on the "install_requires" variable in call to setup(), not enough to have a requirements.txt file.

- MANIFEST.in:

    - Notes on manifest files from Visual Studio Code plugin: https://marketplace.visualstudio.com/items?itemName=benspaulding.python-manifest-template
    - Actual manifest file template: https://github.com/benspaulding/vscode-python-manifest-template/blob/master/example/MANIFEST.in

- Including the data files in MANIFEST.in in your package:

    - https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
    - Variables "package_data" and "include_package_data".
