""" The signature for a multi-sarif result file

Produced by 

    cd sarif-cli/data/treeio
    sarif-extract-multi -c multi-sarif-01.json none | sarif-to-dot -utf - 

with some arrays manually sorted so the the signature with more fields comes first.  The case 
    ('Array6343', ('array', (1, 'Struct9699'), (0, 'Struct4055'))), # MANUALLY SORTED
is marked below.

Also, this struct should be (and is) identical to struct_graph_2022_02_01 in the
leading entries, but there are two extras.

To get a map of this type graph, use

    cd sarif-cli/data/treeio
    sarif-extract-multi -c multi-sarif-01.json none | \
        sarif-to-dot -u -t -f -n -d  - | dot -Tpdf > typegraph-multi.pdf

"""

# 
# The starting node is the leftmost node in ../notes/typegraph-multi.pdf
# 
start_node_2022_03_08 = 'Array7481'

struct_graph_2022_03_08 = (
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
            ('version', 'String'))),    # Up to here identical to struct_graph_2022_02_01
    (   'Struct3452',
        (   'struct',
            ('creation_date', 'String'),
            ('primary_language', 'String'),
            ('project_name', 'String'),
            ('query_commit_id', 'String'),
            ('sarif_content', 'Struct6787'),
            ('sarif_file_name', 'String'),
            ('scan_id', 'Int'),
            ('scan_start_date', 'String'),
            ('scan_stop_date', 'String'),
            ('tool_name', 'String'),
            ('tool_version', 'String'))),
    ('Array7481', ('array', (0, 'Struct3452')))]
)
