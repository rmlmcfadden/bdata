# Setup Cython double exponential integrator
# Derek Fujimoto
# October 2017 

# python3 setup_integrator.py build_ext --inplace

from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy
        
# Compile integrator
setup(
    ext_modules=cythonize(Extension("integrator",
                sources=["integrator.pyx",
                        "FastNumericalIntegration_src/integration_fns.cpp"],
                language="c++",             # generate C++ code                        
                include_dirs=["FastNumericalIntegration_src",numpy.get_include()],
                libraries=["m"],
                extra_compile_args=['-std=c++11',"-ffast-math"]
)))
