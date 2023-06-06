from . import specgram_examiner, figures
from warnings import warn_explicit, catch_warnings

try:
    from . import filter
except ImportError as e:    
    warn_explicit(str(e), Warning, __file__, e.__traceback__.tb_lineno)