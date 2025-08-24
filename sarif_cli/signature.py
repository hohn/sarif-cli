""" SARIF signature functionality

These functions convert a SARIF (or any json structure) to its signature, with various options.  
See sarif-to-dot for options and examples.
"""
from dataclasses import dataclass
from . import traverse
import zlib
from sarif_cli import snowflake_id

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

flakegen = snowflake_id.Snowflake(0)

#
# Context for signature functions
#
@dataclass
class Context:
    sig_to_typedef: dict                     # signature -> typedef name map

def shorthash(signature):
    return zlib.adler32(str(signature).encode('utf-8')) % 10000

#
# Signature formation
#
def _signature_dict(args, elem, context: Context):
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
            context.sig_to_typedef[signature] = "Struct%04d" % shorthash(signature)
        typedef = context.sig_to_typedef[signature]
        return typedef
    else:
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
            #cannot have leading 0 hashes later in table joins so replace now
            #context.sig_to_typedef[signature] = str("Array%04d" % shorthash(signature)).replace("0", "1")
            context.sig_to_typedef[signature] = "Array%04d" % shorthash(signature)
        typedef = context.sig_to_typedef[signature]
        return typedef
    else:
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
    graph [rankdir = "LR", ranksep=2];
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
                       [ ('description', 'String'),
                         ('kind', 'String'),
                         ('precision', 'String'),
                         ('security-severity', 'String'),
                         ('severity', 'String'),
                         ('sub-severity', 'String'),
                         ('tags', 'Array003'),
                        ]])
# 
# scli-dyys is a random id string for later identification of dummy values
# 
dummy_properties = { 'description' : 'scli-dyys dummy value',
                     'kind' : 'scli-dyys dummy value',
                     'precision' : 'scli-dyys dummy value',
                     'security-severity' : 'scli-dyys dummy value',
                     'problem.severity' : 'scli-dyys dummy value',
                     'sub-severity' : 'scli-dyys dummy value',
                     'tags' : ['scli-dyys dummy value'],
                    }

relatedLocations_keys = set([first for first, _ in
                             [('message', 'Struct009'),
                              ('physicalLocation', 'Struct006'),
                              ('id', 'Int'),
                              ]])

dummy_newlineSequences = ['\r\n', '\n', '\u2028', '\u2029']

dummy_relatedLocations_entry = [
    {'id': -1,
     'physicalLocation': {'artifactLocation': {'uri': 'scli-dyys dummy value',
                                               'uriBaseId': 'scli-dyys uriBaseId',
                                               'index': -1},
                          'region': {'startLine': -1, 
                                     'startColumn': -1,
                                     'endLine': -1, 
                                     'endColumn': -1}},
     'message': {'text': 'scli-dyys dummy value'}}]

dummy_message_entry = {'text': 'scli-dyys dummy value'}

dummy_sourceLanguage = 'unknown'

def fillsig_dict(args, elem, context):
    """ Fill in the missing fields in dictionary signatures.
    """
    full_elem = {}
        
    # Several rules overlap and need to be applied together, so this is (now) a
    # simple sequence tests.

    if 'results' in elem.keys() and not 'automationDetails' in elem.keys():
        # Want this to be flagged if not present- ie no submodule info added/no
        # sarif-category used  
        full_elem['automationDetails'] = {'id' : "no-value-for-ad"}

    if {'locations', 'message', 'partialFingerprints', 'ruleId',
        'ruleIndex'}.issubset(elem.keys()):
        # Ensure 'rule' is present 
        rule = elem.get('rule', None)
        if rule is not None:
            full_elem['rule'] = rule
        else:
            full_elem['rule'] = {
                "id" : elem.get('ruleId'),
                "index" : elem.get('ruleIndex'),
            }

    if {'columnKind', 'properties', 'tool',
        'versionControlProvenance'}.issubset(elem.keys()):
        full_elem['artifacts'] = elem.get('artifacts', [])

    if region_keys.intersection(elem.keys()):
        startLine, startColumn, endLine, endColumn = traverse.lineinfo(elem)
        full_elem['endColumn'] = endColumn
        full_elem['endLine'] = endLine
        full_elem['startColumn'] = startColumn
        full_elem['startLine'] = startLine

    if physicalLocation_keys.intersection(elem.keys()):
        full_elem['region'] = elem.get('region', dummy_region())

    if properties_keys.intersection(elem.keys()):
        for k, dummy_val in dummy_properties.items():
            full_elem[k] = elem.get(k, dummy_val)

    if {'message', 'physicalLocation'}.issubset(elem.keys()):
         # Ensure an id is present when message/physicalLocation are
        full_elem['id'] = elem.get('id', -1)

    if elem.get('defaultConfiguration') == {}:
        full_elem['defaultConfiguration'] = {
            "enabled" : False,
            "level" : 'scli-dyys dummy value'
        }

    if 'level' in elem.keys():
        full_elem['enabled'] = elem.get('enabled', True)

    if 'semmle.formatSpecifier' in elem.keys():
        # Ensure semmle.sourceLanguage is present at least in dummy form
        full_elem['semmle.sourceLanguage'] = elem.get('semmle.sourceLanguage', dummy_sourceLanguage)

    if 'versionControlProvenance' in elem.keys():
        # Ensure newlineSequences is present when versionControlProvenance is
        full_elem['newlineSequences'] = elem.get('newlineSequences', dummy_newlineSequences)

    if 'primaryLocationLineHash' in elem.keys():
        # Ensure primaryLocationStartColumnFingerprint is present
        full_elem['primaryLocationStartColumnFingerprint'] = elem.get('primaryLocationStartColumnFingerprint', "fingerprint_placeholder")
        

    #this fix depends on optional property defaultConfiguration being presents
    if 'defaultConfiguration' in elem.keys():
        # Ensure fullDescription is present
        # value must be unique because it is used in id gen used in table join later (joins_for_rules)
        flake = flakegen.next()
        full_elem['fullDescription'] = elem.get('fullDescription', "description_placeholder"+str(flake))   

    if 'partialFingerprints' in elem.keys():
        # Ensure relatedLocations is present
        full_elem['relatedLocations'] = elem.get('relatedLocations',
                                                 dummy_relatedLocations_entry)
        
    if 'physicalLocation' in elem.keys():
        # Ensure id and message are present
        full_elem['id'] = elem.get('id', -1)
        full_elem['message'] = elem.get('message', dummy_message_entry)

    # Supplement final keys with keys from input.  This is to ensure that keys
    # not explicit here (like additions to the sarif standard) are propagated. 
    remaining_keys = set(elem.keys()) - set(full_elem.keys())
    for key in remaining_keys:
        full_elem[key] = elem[key]

    # Sort signature for consistency across inputs.
    final = {}
    keys = sorted(full_elem.keys())
    for key in keys:
        val = full_elem[key]
        # And recurse to get nested elements
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
    elif t in [str, int, bool, float]:
        return elem
    else:
        raise Exception("Unknown element type", t, elem)

