import sys
import os
import re
import codecs
import csv

MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

def get_csv_writer():
    """ Set up and return the default csv writer on stdout.
    """
    return csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

def write_csv(writer, *columns):
    """ Print via `writer`, with some additional processing """
    writer.writerow(columns)

def get_relatedlocation_message_info(related_location):
    """ Given a relatedLocation, extract message information.

    The relatedLocation typically starts from 
    get(sarif_struct, 'runs', [int], 'results', [int], 'relatedLocations', [int])

    For a threadFlow, extract message information for a location contained in it.

    The location typically starts from 
    get(sarif_struct, 'runs', _i, 'results', _i, 'codeFlows', _i, 'threadFlows', _i, 'locations', _i) 
    """
    message = get(related_location, 'message', 'text')
    artifact = get(related_location, 'physicalLocation', 'artifactLocation')
    region = get(related_location, 'physicalLocation', 'region')
    return message, artifact, region

class WholeFile:
    pass

def get_location_message_info(result):
    """ Given one of the results, extract message information.

    The `result` typically starts from get(sarif_struct, 'runs', run_index, 'results', res_index)

    Returns: (message, artifact, region)
        For an empty 'region' key, returns (message, artifact, sarif_cli.WholeFile)

    """
    message = get(result, 'message', 'text')
    artifact = get(result, 'locations', 0, 'physicalLocation', 'artifactLocation')
    # If there is no 'region' key, use the whole file
    region = get(result,  'locations', 0, 'physicalLocation').get('region', WholeFile)
    return (message, artifact, region)

def display_underlined(l1, c1, l2, c2, line, line_num):
    """ Display the given line followed by a second line with underscores at the locations.
    
    l1, c1, l2, c2: the line/column range
    line: the line of text
    line_num: the line number for the text, used with the line/column range
    """
    # Display the line
    msg("%s" % (line))
    msg("\n")
    # Print the underline
    underline = underline_for_result(l1, c1, l2, c2, line, line_num)
    msg(underline)
    # Next result
    msg("\n")

def underline_for_result(first_line, first_column, last_line, last_column, line, line_num):
    """Provide the underline for a result line.

    first_line, first_column, last_line, last_column : 
        the region from lineinfo(region)
    line: 
        the line of source
    line_num:  
        the index of line, must satisfy first_line <= line_num <= last_line
    """
    # Underline the affected region
    # col_* use the [start, end) indexing
    #   From the first non-whitespace char
    match = re.search("([^\s])+", line)
    if match:
        col_from = match.span()[0]
    else:
        col_from = 0
    #   To the last non-whitespace char
    match = re.search("(\s)+$", line)
    if match:
        col_to = match.span()[0]
    else:
        col_to = len(line)
    #   Use 1-indexing
    col_from += 1 ; col_to += 1
    #   Adjust first line
    if line_num == first_line:
        col_from = max(col_from, first_column)
    #   Adjust last line
    if line_num == last_line:
        col_to = min(col_to, last_column)
    #   Use 0-indexing
    col_from -= 1 ; col_to -= 1
    # Return the underline
    return " " * col_from + "^" * (col_to - col_from)
    

def load_lines(root, path, line_from, line_to):
    """Load the line range [line_from, line_to], including both, 
    from the file at root/path.  
    Lines are counted from 1.  
    Use 1 space for each tab.  This seems to be the codeql handling for beginning of line.
    Newlines are dropped.
    """
    fname = os.path.join(root, path)
    if not os.path.exists(fname):
        dbg("Missing file: %s" % fname)
        return []
    with codecs.open(fname, 'r', encoding="latin-1") as file:
        lines = file.readlines()
        return [line.rstrip("\n\r").replace("\t", " ")
                for line in lines[line_from-1 : line_to-1+1]]

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
    sys.stderr.write("warning: %s" % message)
    sys.stderr.flush()
