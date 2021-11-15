import sys
import os

MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

def load_lines(root, path, line_from, line_to):
    """Load the line range [line_from, line_to], including both, 
    from the file at root/path.  Lines are counted from 1.  Newlines are dropped."""
    fname = os.path.join(root, path)
    with open(fname, 'r') as file:
        lines = file.readlines()
        return [line.rstrip("\n\r") for line in lines[line_from-1 : line_to-1+1]]

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

def dbg(message):
    """ Print message to stderr """
    sys.stdout.flush()
    sys.stderr.write(message)
    sys.stderr.flush()
