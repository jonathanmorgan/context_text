import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name="django-context-text",
    version="1.0.1",
    author="Jonathan Morgan",
    author_email="jonathan.morgan.007@gmail.com",
    description="Framework for deriving information from text.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonathanmorgan/context_text",
    packages=setuptools.find_packages(),
    # you can also specify which items in manifest should be included.
    #package_data={
    #    'context_text':
    #    [
    #        '*.py',
    #        '*.txt',
    #        '*.md',
    #        'static/context_text/*',
    #        'templates/context_text/*.html'
    #    ]
    #},
    include_package_data=True, # needed for things in manifest to be included in package.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities"
    ],
    install_requires=[
        "django",
        "django-ajax-selects",
        "django-basic-config",
        "django-context-core",
        "django-json-widget",
        "django-taggit",
        "psycopg2",
        "python-utilities-jsm"
    ],
    python_requires='>=3.6',
)
