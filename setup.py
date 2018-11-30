import setuptools
from distutils.core import Extension
from Cython.Build import cythonize
import numpy

with open("README.md", "r") as fh:
    long_description = fh.read()

# module extension
ext = Extension("bdata.mudpy",
                sources=["./bdata/mudpy.pyx"])

setuptools.setup(
    name="bdata",
    version="1.3.6",
    author="Derek Fujimoto",
    author_email="fujimoto@phas.ubc.ca",
    description="BNMR/BNQR MUD file reader and asymmetry calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dfujim/bdata",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['cython>=0.28','numpy>=1.14'],
    ext_modules = cythonize([ext],include_path = [numpy.get_include()]),
)

