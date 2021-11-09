import sys

MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

def indices(sarif_struct, *path):
    """ Return a range for the indices of PATH """
    return range(0, len(get(sarif_struct, *path)))

def get(sarif_struct, *path):
    """ Get the sarif entry at PATH """
    res = sarif_struct
    for p in path:
        res = res[p]
    return res

def msg(message):
    """ Print message to stdout """
    sys.stdout.write(message)
    sys.stdout.write('\n')
    
