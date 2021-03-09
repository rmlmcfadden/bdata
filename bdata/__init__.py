from bdata.bdata import bdata, life
from bdata.bjoined import bjoined
from bdata.bmerged import bmerged
from bdata.exceptions import InputError, MinimizationError

import os

__all__ = ['bdata', 'bjoined', 'bmerged', 'life']
__version__ = '6.3.0'
__author__ = 'Derek Fujimoto'
_mud_data = os.path.join(os.environ['HOME'], '.bdata')
