#Copyright ReportLab Europe Ltd. 2000-2021
#see license.txt for license details
__doc__="""The Reportlab PDF generation library."""
Version = "3.5.67"
__version__=Version
__date__='20210412'

import sys, os

__min_python_version__ = (3,6)
if sys.version_info[0:2]!=(2, 7) and sys.version_info< __min_python_version__:
    raise ImportError("""reportlab requires Python 2.7+ or %s.%s+; other versions are unsupported.
If you want to try with other python versions edit line 10 of reportlab/__init__
to remove this error.""" % (__min_python_version__))

#define these early in reportlab's life
isPy3 = sys.version_info[0]==3
if isPy3:
    def cmp(a,b):
        return -1 if a<b else (1 if a>b else 0)
    xrange = range
    ascii = ascii

    def _fake_import(fn,name):
        from importlib import machinery
        m = machinery.SourceFileLoader(name,fn)
        try:
            sys.modules[name] = m.load_module(name)
        except FileNotFoundError:
            raise ImportError('file %s not found' % ascii(fn))
else:
    from future_builtins import ascii
    xrange = xrange
    cmp = cmp
    def _fake_import(fn,name):
        if os.path.isfile(fn):
            import imp
            with open(fn,'rb') as f:
                sys.modules[name] = imp.load_source(name,fn,f)

#try to use dynamic modifications from
#reportlab.local_rl_mods.py
#reportlab_mods.py or ~/.reportlab_mods
try:
    import reportlab.local_rl_mods
except ImportError:
    pass

if not isPy3:
    PermissionError = ImportError

try:
    import reportlab_mods   #application specific modifications can be anywhere on python path
except ImportError:
    try:
        _fake_import(os.path.expanduser(os.path.join('~','.reportlab_mods')),'reportlab_mods')
    except (ImportError,KeyError,PermissionError):
        pass
