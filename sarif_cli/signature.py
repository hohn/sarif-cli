""" SARIF signature functionality

These functions convert a SARIF (or any json structure) to its signature, with various options.  
See sarif-to-dot for options and examples.
"""
from dataclasses import dataclass
import sarif_cli.traverse as traverse

# 
# These are internal node format samples produced by the _signature* functions, as
# (typedef, sig) tuples:
# 
# [ ('String', 'string'),
#   ('Int', 'int'),
#   ('Bool', 'bool'),
#   ('Struct000', ('struct', ('text', 'String'))),
#   ('Struct001', ('struct', ('enabled', 'Bool'), ('level', 'String'))),
#   ('Array002', ('array', (0, 'String'))),
#   ( 'Struct003',
#     ( 'struct',
#       ('kind', 'String'),
#       ('precision', 'String'),
#       ('severity', 'String'),
#       ('tags', 'Array002'))),
# ...

#
# Context for signature functions
#
@dataclass
class Context:
    sig_to_typedef: dict        # signature to typedef name map
    sig_count: int              # simple struct counter for Struct%03d names

#
# Signature formation
#
def _signature_dict(args, elem, context):
    """ Assemble and return the signature for a dictionary.
    """
    # Collect signatures
    sig = {}
    for key, val in elem.items():
        sig[key] = _signature(args, val, context)
    # Sort signature
    keys = list(elem.keys())
    keys.sort()
    # Form and return (struct (key sig) ...)
    signature = ("struct", ) + tuple([(key, sig[key]) for key in keys])
    if args.typedef_signatures:
        # Give every unique struct a name and use a reference to it as value.
        if signature not in context.sig_to_typedef:
            context.sig_to_typedef[signature] = "Struct%03d" % context.sig_count
            context.sig_count += 1
        signature = context.sig_to_typedef[signature]
    return signature

def _signature_list(args, elem, context):
    """ Assemble and return the signature for a Python list.
    """
    if args.unique_array_signatures:
        # Collect all unique signatures
        sig = set()
        for el in elem:
            sig.add(_signature(args, el, context))
        sig = list(sig)
        sig.sort()
        signature = ("array", ) + tuple([(i, s) for (i, s) in enumerate(sig)])
    else:
        # Collect all signatures
        sig = []
        for el in elem:
            sig.append(_signature(args, el, context))
        signature = ("array", ) + tuple([(i, s) for (i, s) in enumerate(sig)])
    if args.typedef_signatures:
        # Give every unique array a name and use a reference to it as value.
        if signature not in context.sig_to_typedef:
            context.sig_to_typedef[signature] = "Array%03d" % context.sig_count
            context.sig_count += 1
        signature = context.sig_to_typedef[signature]
    return signature

def _signature(args, elem, context):
    """ Assemble and return the signature for a list/dict/value structure.
    """
    t = type(elem)
    if t == dict:
        return _signature_dict(args, elem, context)
    elif t == list:
        return _signature_list(args, elem, context)
    elif t == str:
        if args.typedef_signatures:
            return context.sig_to_typedef["string"]
        return ("string")
    elif t == int:
        if args.typedef_signatures:
            return context.sig_to_typedef["int"]
        return ("int")
    elif t == bool:
        if args.typedef_signatures:
            return context.sig_to_typedef["bool"]
        return ("bool")
    else:
        return ("unknown", elem)

#
# Dot output routines
#
def write_header(fp):
    fp.write("""digraph sarif_types {
    node [shape=box,fontname="Charter"];
    graph [rankdir = "LR"];
    edge [];
    """)
    # Alternative font choices:
    #     node [shape=box,fontname="Avenir"];
    #     node [shape=box,fontname="Enriqueta Regular"];

def write_footer(fp):
    fp.write("}")
    
def write_node(fp, typedef, sig):
    """ Write nodes in dot format.
    """
    if sig in ["string", "int", "bool"]:
        label = sig
    elif sig[0] == "array":
        label = "\l|".join([ "<%s>%s" % (field[0],field[0]) for field in sig[1:]])
    elif sig[0] == "struct":
        label = "\l|".join([ "<%s>%s" % (field[0],field[0]) for field in sig[1:]])
    else:
        raise Exception("unknown signature: " + str(sig))
    node = """ "{name}" [
    label = "{head}\l|{body}\l"
    shape = "record"
    ];
    """.format(name=typedef, head=typedef, body=label)
    fp.write(node)

def write_edges(args, fp, typedef, sig):
    """ Write edges in dot format.
    """
    if sig in ["string", "int", "bool"]:
        pass
    elif sig[0] in ("struct", "array"):
        # Sample struct:
        # ( struct
        #      (semmle.formatSpecifier string)
        #      (semmle.sourceLanguage string))
        # 
        # Sample array:
        # ( array
        #   ( 0
        #     ( struct
        #       (repositoryUri string)
        #       (revisionId string))))
        for field in sig[1:]:
            field_name, field_type = field
            label = ""
            dest = str(field_type)
            if dest in ["String", "Int", "Bool"] and args.no_edges_to_scalars:
                pass
            else:
                edge = """ {src_node}:"{src_port}" -> {dest} [label="{label}"];
                """.format(src_node=typedef, src_port=field_name, dest=field_type,
                           label=label)
                fp.write(edge)
    else:
        raise Exception("unknown signature: " + str(sig))
    
#
# Fill missing elements
#
region_keys = set([first for first, _ in  [ ('endColumn', 'Int'),
                                            ('endLine', 'Int'),
                                            ('startColumn', 'Int'),
                                            ('startLine', 'Int')]])

def dummy_region():
    """ Return a region with needed keys and "empty" entries -1
    """
    return {
        'endColumn' : -1,
        'endLine' : -1,
        'startColumn' : -1,
        'startLine' : -1
    }

physicalLocation_keys = set([first for first, _ in
                             [ ('artifactLocation', 'Struct000'), 
                               ('region', 'Struct005')]])

properties_keys = set([first for first, _ in
                       [ ('kind', 'String'),
                         ('precision', 'String'),
                         ('security-severity', 'String'),
                         ('severity', 'String'),
                         ('sub-severity', 'String'),
                         ('tags', 'Array003'),
                        ]])
dummy_properties = { 'kind' : 'unspecified',
                     'precision' : 'unspecified',
                     'security-severity' : 'unspecified',
                     'severity' : 'unspecified',
                     'sub-severity' : 'unspecified',
                     'tags' : ['unspecified'],
                    }

def fillsig_dict(args, elem, context):
    """ Fill in the missing fields in dictionary signatures.
    """
    full_elem = {}
    def _remaining_keys():
        # Supplement final keys with keys from input.  This is to ensure that keys
        # not explicit here (like additions to the sarif standard) are propagated. 
        rest = set(elem.keys()) - set(full_elem.keys())
        for key in rest:
            full_elem[key] = elem[key]
        
    if region_keys.intersection(elem.keys()):
        startLine, startColumn, endLine, endColumn = traverse.lineinfo(elem)
        full_elem['endColumn'] = endColumn
        full_elem['endLine'] = endLine
        full_elem['startColumn'] = startColumn
        full_elem['startLine'] = startLine
        _remaining_keys()
    elif physicalLocation_keys.intersection(elem.keys()):
        full_elem['region'] = elem.get('region', dummy_region())
        _remaining_keys()
    elif properties_keys.intersection(elem.keys()):
        full_elem = {}
        for k, dummy_val in dummy_properties.items():
            full_elem[k] = elem.get(k, dummy_val)
        _remaining_keys()
    else:
        full_elem = elem

    # Sort signature for consistency across inputs.
    final = {}
    keys = sorted(full_elem.keys())
    for key in keys:
        val = full_elem[key]
        final[key] = fillsig(args, val, context)
    return final

def fillsig_list(args, elem, context):
    """ 
    """
    # Collect all entries
    final = []
    for el in elem:
        final.append(fillsig(args, el, context))
    return final

def fillsig(args, elem, context):
    """ Assemble and return the signature for a list/dict/value structure.
    """
    t = type(elem)
    if t == dict:
        return fillsig_dict(args, elem, context)
    elif t == list:
        return fillsig_list(args, elem, context)
    elif t in [str, int, bool]:
        return elem
    else:
        raise Exception("Unknown element type")

