""" The signature for a single sarif file

Produced by 

    sarif-to-dot -u -t -f 2021-12-09/results.sarif

with some arrays manually sorted so the the signature with more fields comes first.  The case 
    ('Array6343', ('array', (1, 'Struct9699'), (0, 'Struct4055'))), # MANUALLY SORTED
is marked below
"""

# 
# The starting node the leftmost node in ../notes/typegraph.pdf
# 
start_node_CLI = 'Struct5521'

# generated with CLI 2.9.4
struct_graph_CLI = (
    [   ('String', 'string'),
    ('Int', 'int'),
    ('Bool', 'bool'),
    (   'Struct2685',
        (   'struct',
            ('index', 'Int'),
            ('uri', 'String'),
            ('uriBaseId', 'String'))),
    ('Struct5277', ('struct', ('location', 'Struct2685'))),
    ('Struct3497', ('struct', ('index', 'Int'), ('uri', 'String'))),
    ('Struct9567', ('struct', ('location', 'Struct3497'))),
    ('Array6920', ('array', (0, 'Struct5277'), (1, 'Struct9567'))),
    ('Struct1509', ('struct', ('semmle.formatSpecifier', 'String'))),
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
    (   'Struct7125',
        (   'struct',
            ('artifactLocation', 'Struct3497'),
            ('region', 'Struct6299'))),
    (   'Struct6772',
        (   'struct',
            ('id', 'Int'),
            ('message', 'Struct2774'),
            ('physicalLocation', 'Struct7125'))),
    ('Array8753', ('array', (0, 'Struct6772'))),
    (   'Struct0102',
        (   'struct',
            ('locations', 'Array0350'),
            ('message', 'Struct2774'),
            ('partialFingerprints', 'Struct4199'),
            ('relatedLocations', 'Array8753'),
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
    (   'Array1768',
        #('array', (2, 'Struct9699'), (1, 'Struct4055'),(0, 'Struct0102'))),
        #('array',(0, 'Struct0102'), (1, 'Struct4055'), (2, 'Struct9699'))),
        #omitting (0, 'Struct0102') means we will never find column info
        ('array', (2, 'Struct9699'), (1, 'Struct4055'))),
    ('Struct8581', ('struct', ('enabled', 'Bool'), ('level', 'String'))),
    ('Array7069', ('array', (0, 'String'))),
    (   'Struct6853',
        (   'struct',
            ('description', 'String'),
            ('id', 'String'),
            ('kind', 'String'),
            ('name', 'String'),
            ('precision', 'String'),
            ('problem.severity', 'String'),
            ('security-severity', 'String'),
            ('severity', 'String'),
            ('sub-severity', 'String'),
            ('tags', 'Array7069'))),
    (   'Struct7100',
        (   'struct',
            ('defaultConfiguration', 'Struct8581'),
            ('fullDescription', 'Struct2774'),
            ('id', 'String'),
            ('name', 'String'),
            ('properties', 'Struct6853'),
            ('shortDescription', 'Struct2774'))),
    ('Array0147', ('array', (0, 'Struct7100'))),
    (   'Struct7828',
        (   'struct',
            ('name', 'String'),
            ('organization', 'String'),
            ('rules', 'Array0147'),
            ('semanticVersion', 'String'))),
    (   'Struct9027',
        ('struct', ('description', 'Struct2774'), ('uri', 'String'))),
    ('Array4813', ('array', (0, 'Struct9027'))),
    (   'Struct6152',
        (   'struct',
            ('locations', 'Array4813'),
            ('name', 'String'),
            ('semanticVersion', 'String'))),
    ('Struct7826', ('struct', ('locations', 'Array4813'), ('name', 'String'))),
    ('Array9357', ('array', (0, 'Struct6152'), (1, 'Struct7826'))),
    (   'Struct0032',
        ('struct', ('driver', 'Struct7828'), ('extensions', 'Array9357'))),
    (   'Struct3081',
        ('struct', ('repositoryUri', 'String'), ('revisionId', 'String'))),
    ('Array5511', ('array', (0, 'Struct3081'))),
    (   'Struct9786',
        (   'struct',
            ('artifacts', 'Array6920'),
            ('columnKind', 'String'),
            ('newlineSequences', 'Array7069'),
            ('properties', 'Struct1509'),
            ('results', 'Array1768'),
            ('tool', 'Struct0032'),
            ('versionControlProvenance', 'Array5511'))),
    ('Array1273', ('array', (0, 'Struct9786'))),
    (   'Struct5521',
        (   'struct',
            ('$schema', 'String'),
            ('runs', 'Array1273'),
            ('version', 'String')))] )
