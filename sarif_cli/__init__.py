import sys

MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

def lineinfo(region):
    """ Return sensible values for start/end line/columns for the possibly empty
    entries in the sarif 'region' structure.
    """
    startLine, startColumn, endLine, endColumn = map(
        lambda e: region.get(e, -1), ['startLine', 'startColumn', 'endLine', 'endColumn'])
    # Full information is startLine / startColumn / endLine / endcolumn
    # - only have startLine / startColumn / _ / endcolumn
    if endLine == -1: endLine = startLine 

    # - only have startLine / _ / _ / endcolumn
    if startColumn == -1: startColumn = 1 

    return startLine, startColumn, endLine, endColumn

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
    
