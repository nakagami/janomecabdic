
try:
    from .dic import MeCabDictionary
except ImportError:
    from .dic_fallback import MeCabDictionary
