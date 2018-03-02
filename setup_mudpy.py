# Setup Cython mudpy functions
# Derek Fujimoto
# July 2017 

# python3 setup_mudpy.py build_ext --inplace

from distutils.core import setup, Extension
from Cython.Distutils import build_ext
    
# Compile mudpy
setup(
    cmdclass={"build_ext": build_ext},
    ext_modules=[Extension("mudpy",
                           sources=["mudpy.pyx",
                                    "./mud_src/mud.c",
                                    "./mud_src/mud_gen.c",
                                    "./mud_src/mud_encode.c",
                                    "./mud_src/mud_new.c",
                                    "./mud_src/mud_tri_ti.c",
                                    "./mud_src/mud_all.c"])]
                                    
)
