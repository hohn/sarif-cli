""" SARIF signature functionality

These functions convert a SARIF (or any json structure) to its signature, with various options.  
See sarif-to-dot for options and examples.
"""
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

# See format samples above write_node
def write_edges(fp, typedef, sig):
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
            edge = """ {src_node}:"{src_port}" -> {dest} [label="{label}"];
            """.format(src_node=typedef, src_port=field_name, dest=field_type,
                       label=label)
            fp.write(edge)
    else:
        raise Exception("unknown signature: " + str(sig))
    
