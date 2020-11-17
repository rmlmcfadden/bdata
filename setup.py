import setuptools
from distutils.core import Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bdata",
    version="6.1.1",
    author="Derek Fujimoto",
    author_email="fujimoto@phas.ubc.ca",
    description="BNMR/BNQR MUD file reader and asymmetry calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dfujim/bdata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Cython",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Development Status :: 5 - Production/Stable",
    ],
    install_requires=['cython>=0.28','numpy>=1.14','mud-py>=1.0.2','requests>=2.22.0','pandas>=0.25'],
)

