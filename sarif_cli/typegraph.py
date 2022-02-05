"""Operations on the type graph produced by sarif-to-dot -u -t -f

To get a map of this type graph, use
    cd sarif-cli/data/treeio
    ../../bin/sarif-to-dot -u -t -f -n -d  results.sarif | dot -Tpdf > typegraph.pdf

This file also contains some type graph reference values; these may be moved out into
separate files at some point.
"""
from dataclasses import dataclass
from typing import *
import pandas as pd

# 
# Structure graph from ../../bin/sarif-to-dot -u -t -f results.sarif
# 
struct_graph_2022_02_01 = (
[   ('String', 'string'),
    ('Int', 'int'),
    ('Bool', 'bool'),
    (   'Struct2685',
        (   'struct',
            ('index', 'Int'),
            ('uri', 'String'),
            ('uriBaseId', 'String'))),
    ('Struct5277', ('struct', ('location', 'Struct2685'))),
    ('Array4640', ('array', (0, 'Struct5277'))),
    ('Array7069', ('array', (0, 'String'))),
    (   'Struct9543',
        (   'struct',
            ('semmle.formatSpecifier', 'String'),
            ('semmle.sourceLanguage', 'String'))),
    ('Struct2774', ('struct', ('text', 'String'))),
    (   'Struct6299',
        (   'struct',
            ('endColumn', 'Int'),
            ('endLine', 'Int'),
            ('startColumn', 'Int'),
            ('startLine', 'Int'))),
    (   'Struct4963',
        (   'struct',
            ('artifactLocation', 'Struct2685'),
            ('region', 'Struct6299'))),
    (   'Struct2683',
        (   'struct',
            ('id', 'Int'),
            ('message', 'Struct2774'),
            ('physicalLocation', 'Struct4963'))),
    ('Array0350', ('array', (0, 'Struct2683'))),
    (   'Struct4199',
        (   'struct',
            ('primaryLocationLineHash', 'String'),
            ('primaryLocationStartColumnFingerprint', 'String'))),
    ('Struct3942', ('struct', ('id', 'String'), ('index', 'Int'))),
    (   'Struct4055',
        (   'struct',
            ('locations', 'Array0350'),
            ('message', 'Struct2774'),
            ('partialFingerprints', 'Struct4199'),
            ('relatedLocations', 'Array0350'),
            ('rule', 'Struct3942'),
            ('ruleId', 'String'),
            ('ruleIndex', 'Int'))),
    ('Struct0987', ('struct', ('location', 'Struct2683'))),
    ('Array1075', ('array', (0, 'Struct0987'))),
    ('Struct4194', ('struct', ('locations', 'Array1075'))),
    ('Array1597', ('array', (0, 'Struct4194'))),
    ('Struct7122', ('struct', ('threadFlows', 'Array1597'))),
    ('Array9799', ('array', (0, 'Struct7122'))),
    (   'Struct9699',
        (   'struct',
            ('codeFlows', 'Array9799'),
            ('locations', 'Array0350'),
            ('message', 'Struct2774'),
            ('partialFingerprints', 'Struct4199'),
            ('relatedLocations', 'Array0350'),
            ('rule', 'Struct3942'),
            ('ruleId', 'String'),
            ('ruleIndex', 'Int'))),
    ('Array6343', ('array', (1, 'Struct9699'), (0, 'Struct4055'))), # MANUALLY SORTED
    ('Struct8581', ('struct', ('enabled', 'Bool'), ('level', 'String'))),
    (   'Struct7849',
        (   'struct',
            ('kind', 'String'),
            ('precision', 'String'),
            ('security-severity', 'String'),
            ('severity', 'String'),
            ('sub-severity', 'String'),
            ('tags', 'Array7069'))),
    (   'Struct6818',
        (   'struct',
            ('defaultConfiguration', 'Struct8581'),
            ('fullDescription', 'Struct2774'),
            ('id', 'String'),
            ('name', 'String'),
            ('properties', 'Struct7849'),
            ('shortDescription', 'Struct2774'))),
    ('Array8754', ('array', (0, 'Struct6818'))),
    (   'Struct7820',
        (   'struct',
            ('name', 'String'),
            ('organization', 'String'),
            ('rules', 'Array8754'),
            ('version', 'String'))),
    ('Struct8972', ('struct', ('driver', 'Struct7820'))),
    (   'Struct3081',
        ('struct', ('repositoryUri', 'String'), ('revisionId', 'String'))),
    ('Array5511', ('array', (0, 'Struct3081'))),
    (   'Struct3388',
        (   'struct',
            ('artifacts', 'Array4640'),
            ('columnKind', 'String'),
            ('newlineSequences', 'Array7069'),
            ('properties', 'Struct9543'),
            ('results', 'Array6343'),
            ('tool', 'Struct8972'),
            ('versionControlProvenance', 'Array5511'))),
    ('Array0177', ('array', (0, 'Struct3388'))),
    (   'Struct6787',
        (   'struct',
            ('$schema', 'String'),
            ('runs', 'Array0177'),
            ('version', 'String')))]
)

# 
# The starting node is the typedef with '$schema' in the struct, also the leftmost
# node in ../notes/sarif-structure-from-sarif-to-dot.pdf
# 
start_node_2022_02_01 = 'Struct6787' 

#
# Utility classes
# 
class MissingFieldException(Exception):
    pass

class SignatureMismatch(Exception):
    pass


Tree = Union[Dict, List, int, str, bool]
NodeId = str

#
# Data aggregate
#
@dataclass
class Typegraph:
    signature_graph : Dict[NodeId, Any]   # (typedef -> signature) dict
    instances : Dict[NodeId, List[Tuple]] # (node -> (row list)) dict
    fields: Dict[NodeId, List]            # (node -> (field list)) dict
    dataframes: Dict[NodeId, Any]         # (node -> dataframe) dict

    """
    # Given this typedef
    (   'Struct6787',
        (   'struct',
            ('$schema', 'String'),
            ('runs', 'Array0177'),
            ('version', 'String')))
    # and an instance SI of Struct6787, we have the following fields:
    instances['Struct6787'] = []

    fields['Struct6787'] = ('$schema',        # Sorted from here
                            'runs',
                            'version')

    table_header['Struct6787'] = ('id',
                                  '$schema',        # Sorted from here
                                  'runs',
                                  'version')
    
    # The values are filled via
    instances['Struct6787'].append( (id(SI), # "uplink" id
                                     SI['$schema'],  # value for int|string|bool
                                     id(SI['runs']), # "downlink" id
                                     SI['version']) )
    # which may evaluate to, e.g., 
    instances['Struct6787'].append( (4543584064,
                                     'schema-sarif...',
                                     4543582656,
                                     '2.1') )

    # Array entries use a fixed header with labeled entries:
    # (array_id, value_index, value_type, id_or_value_at_index)
    
    array_header['Array7069'] = ('id',
                                 'value_index',
                                 'value_type',
                                 'value_or_id')
    """


    def __init__(self, signature_graph : List):
        """
        Arguments:
        signature_graph -- The graph of typedefs (signatures), see
                           struct_graph_2022_02_01 as example
        """
        self.signature_graph = dict(signature_graph)
        self.instances = {}
        self.fields = {}
        self.dataframes = {}
        for typedef, signature in signature_graph:
            self.instances[typedef] = []
            self.fields[typedef] = fields(signature)
            
def fields(signature):
    if type(signature) != tuple: 
        # 'bool', 'int', 'string'
        return None
    else:
        typ, *fields = signature
        return sorted([fname for fname, ftype in fields])

def dict_fields(tree: Dict):
    return sorted(tree.keys())

#
# Destructuring functions use the typegraph to destructure all subtrees into tables
#
def destructure(typegraph: Typegraph, node: NodeId, tree: Tree):
    t = type(tree)
    if t == dict:
        _destructure_dict(typegraph, node, tree)
    elif t == list:
        _destructure_list(typegraph, node, tree)
    elif t in [str, int, bool]:
        pass
    else:
        raise Exception("Unhandled type: %s" % t)

def _destructure_dict_1(typegraph, node, tree):
    """
    # typegraph.signature_graph destructuring
    d1 = dict(struct_graph_2022_02_01)
    In [765]: typ, *sig = d1['Struct6787']
    
    In [766]: sig
    Out[766]: [('$schema', 'String'), ('runs', 'Array0177'), ('version', 'String')]
    
    In [767]: typ
    Out[774]: 'struct'
    """
    def id_or_value(tree, fieldname, fieldtype):
        """ Id for recursive types, value for leaves
        """
        if fieldtype in ['Bool', 'Int', 'String']:
            return tree[fieldname]
        else:
            return id(tree[fieldname])

    # Sanity check
    sig = typegraph.signature_graph[node]
    if type(sig) != tuple:
        raise SignatureMismatch()

    # Destructure this dictionary
    subtype, *signature = sig
    typegraph.instances[node].append(
        (id(tree),
         *[id_or_value(tree, fieldname, fieldtype)
           for fieldname, fieldtype in signature]))

    # Destructure recursive entries
    for fieldname, fieldtype in signature:
        if fieldtype not in ['Bool', 'Int', 'String']:
            destructure(typegraph, fieldtype, tree[fieldname])


def _destructure_dict(typegraph: Typegraph, node, tree):
    tree_fields = dict_fields(tree)
    type_fields = typegraph.fields[node]
    if tree_fields == type_fields:
        _destructure_dict_1(typegraph, node, tree)
        
    elif set(tree_fields).issuperset(set(type_fields)):
        # Log a warning
        # log.warning("XX: Tree has unrecognized fields")
        _destructure_dict_1(typegraph, node, tree)

    elif set(tree_fields).issubset(set(type_fields)):
        raise MissingFieldException("XX: (Sub)tree is missing fields required by typedef")

    else:
        raise Exception("typegraph: unhandled case reached.  Internal error")
        

def _destructure_list(typegraph, node: str, tree: List):
    """
    """
    # List entries with multiple distinct signatures must be in order from most specific
    # to least specific.
    # 
    # HERE, WE ASSUME THAT THE `signature` list (see below) IS SORTED IN THE CORRECT ORDER
    # 
    # For the cases in struct_graph_2022_02_01, Struct4055 and
    # Struct9699, the signature with more fields takes precedence -- that is,
    # ('Array6343', ('array', (1, 'Struct9699'), (0, 'Struct4055'))), # MANUALLY SORTED
    # 
    """
    The three considered array signatures:

    Multiple signatures (this is minimized by signature.fillsig()):
        In [753]: d1 = typegraph.signature_graph

        In [949]: subtype, *signature = d1['Array6343']
        In [950]: subtype, signature
        Out[952]: ('array', [(0, 'Struct4055'), (1, 'Struct9699')])

        In [953]: subtype
        Out[953]: 'array'
    
    Single signature, with recursive subtype:

        In [954]: subtype, *signature = d1['Array1597']
        In [955]: signature
        Out[955]: [(0, 'Struct4194')]

    Single signature, leaf value:

        In [956]: subtype, *signature = d1['Array7069']
        In [957]: signature
        Out[957]: [(0, 'String')]
    """
    # Array entries use a fixed header with labeled entries:
    # (array_id, value_index, type_at_index, id_or_value_at_index)

    subtype, *signature = typegraph.signature_graph[node]
    for value, valueindex in zip(tree, range(0,len(tree))):
        for sigindex, sigtype in signature:
            if sigtype in ['Bool', 'Int', 'String']:
                # Destructure array leaf entries
                typegraph.instances[node].append(
                    (id(tree),
                     valueindex, 
                     sigtype,
                     value))
            else:
                # Destructure recursive entries
                try:
                    destructure(typegraph, sigtype, value)
                    typegraph.instances[node].append(
                        (id(tree),
                         valueindex, 
                         sigtype,
                         id(value)))
                    # Next `value` on success
                    break           
                except MissingFieldException as e:
                    # Re-raise if last available signature failed, otherwise try
                    # next `signature`
                    if (sigindex, sigtype) == signature[-1]:
                        raise

#
# Form tables from destructured json/sarif
#
def attach_tables(typegraph):
    for typedef, valarray in typegraph.instances.items():
        if typedef.startswith('Array'):
            # Arrays
            colheader = ('array_id', 'value_index', 'type_at_index', 'id_or_value_at_index')
        elif typedef.startswith('Struct'):
            # Structs
            colheader = ('struct_id', *typegraph.fields[typedef])
        else:
            continue            # skip String etc.
        typegraph.dataframes[typedef] = pd.DataFrame(valarray, columns = colheader)
        
