""" Collection of joins for the base tables provided by typegraph.attach_tables()

    The `problem` and `path-problem` entries provide that information; the
    `relatedLocations` table provides the details when multiple results are
    present for either.  `project` is the high-level overview; `artifacts` 
    provides those for the other tables.
"""
import pandas as pd

def joins_for_sf_2683(tgraph):
    """ 
    Join all the tables used by 2683's right side into one.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    sf_2683 = ( 
        # 
        sf(2683)
        .rename(columns={"struct_id": "struct_id_2683", "id": "id_2683"})
        # 
        .merge(sf(4963), how="left", left_on='physicalLocation', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'physicalLocation'])
        # 
        .merge(sf(6299), how="left", left_on='region', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'region'])
        # 
        .merge(sf(2685), how="left", left_on='artifactLocation', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'artifactLocation'])
        .rename(columns={"index": "location_index_2685"})
        # 
        .merge(sf(2774), how="left", left_on='message', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'message'])
        .rename(columns={"text": "message_text_2683"})
        # 
    )

    return sf_2683

def joins_for_problem(tgraph, sf_2683):
    """ 
    Return table providing the `problem` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    # Form the message dataframe (@kind problem) via joins
    # 
    kind_problem_1 = (
        af(6343)
        .rename(columns={"value_index": "results_idx_6343", "array_id": "result_id_6343"})
        .merge(sf(4055), how="inner", left_on='id_or_value_at_index', right_on='struct_id',
               validate="1:m")
        .drop(columns=['type_at_index', 'id_or_value_at_index', 'struct_id'])
        .rename(columns={"message": "result_message_4055",
                         "relatedLocations": "relatedLocations_id"})
        # locations
        .merge(af('0350'), how="left", left_on='locations', right_on='array_id', validate="1:m")
        .drop(columns=['locations', 'array_id', 'type_at_index'])
        # 
        .merge(sf_2683, how="left", left_on='id_or_value_at_index', right_on='struct_id_2683', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id_2683'])
        # 
        .merge(sf(2774), how="left", left_on='result_message_4055', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'result_message_4055'])
        .rename(columns={"text": "message_text_4055"})
        # 
        .merge(sf(4199), how="left", left_on='partialFingerprints', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'partialFingerprints'])
        #
        .merge(
            sf(3942).rename(columns={"id": "rule_id", "index": "rule_index"}), 
            how="left", left_on='rule', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'rule'])
        #
    )
    return kind_problem_1

def joins_for_codeflows(tgraph, sf_2683):
    """ 
    Return the table providing the `codeFlows` for a `path-problem table.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    #
    af_9799 = (
        af(9799).rename(columns={"array_id": "t9799_array_id", "value_index": "t9799_idx"})
        # 
        .merge(sf(7122), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id', 'type_at_index'])
        # 
        .merge(af(1597).rename(columns={"array_id": "t1597_array_id", "value_index": "t1597_idx"}),
               how="left", left_on='threadFlows', right_on='t1597_array_id', validate="1:m")
        .drop(columns=['threadFlows', 't1597_array_id', 'type_at_index'])
        #
        .merge(sf(4194), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        #
        .merge(af(1075).rename(columns={"array_id": "t1075_array_id", "value_index": "t1075_idx"}),
               how="left", left_on='locations', right_on='t1075_array_id', validate="1:m")
        .drop(columns=['locations', 't1075_array_id', 'type_at_index'])
        .rename(columns={"t1075_idx": "t1075_locations_idx"})
        #
        .merge(sf('0987'), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        #
        .merge(sf_2683, how="left", left_on='location', right_on='struct_id_2683', validate="1:m")
        .drop(columns=['location', 'struct_id_2683'])
    )
    return af_9799

def joins_for_path_problem(tgraph, sf_2683):
    """ 
    Return table providing the `path-problem` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    #
    kind_pathproblem_1 = (
        af(6343)
        .rename(columns={"value_index": "t6343_result_idx", "array_id": "t6343_result_id"})
        .merge(sf(9699), how="inner", left_on='id_or_value_at_index', right_on='struct_id',
               validate="1:m")
        .rename(columns={"codeFlows"           : "t9699_codeFlows",
                         "locations"           : "t9699_locations",
                         "message"             : "t9699_message",
                         "partialFingerprints" : "t9699_partialFingerprints",
                         "relatedLocations"    : "t9699_relatedLocations",
                         "rule"                : "t9699_rule",
                         "ruleId"              : "t9699_ruleId",
                         "ruleIndex"           : "t9699_ruleIndex",
                         })
        .drop(columns=['id_or_value_at_index', 'struct_id', 'type_at_index'])
        # 9699.locations
        .merge(af('0350').rename(columns={"value_index": "t0350_location_idx"}),
               how="left", left_on='t9699_locations', right_on='array_id', validate="1:m")
        .drop(columns=['t9699_locations', 'array_id', 'type_at_index'])
        # 
        .merge(sf_2683, how="left", left_on='id_or_value_at_index', right_on='struct_id_2683', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id_2683'])
        #
        # # TODO: merge or keep separate?
        # # 9699.codeFlows
        # .merge(af_9799, how="left", left_on='t9699_codeFlows', right_on='t9799_array_id', validate="1:m")
        #
        # 9699.message
        .merge(sf(2774), how="left", left_on='t9699_message', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 't9699_message'])
        .rename(columns={"text": "t9699_message_text"})
        # 
        # 9699.partialFingerprints
        .merge(sf(4199), how="left", left_on='t9699_partialFingerprints', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 't9699_partialFingerprints'])
        #
        # 9699.relatedLocations -- keep ids
        # 
        # 9699.rule
        .merge(
            sf(3942).rename(columns={"id": "t3942_rule_id", "index": "t3942_rule_idx"}), 
            how="left", left_on='t9699_rule', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 't9699_rule'])
    )

    # # TODO potential cleanup
    # # Remove dummy locations previously injected by signature.fillsig
    # kind_pathproblem_2 = kind_pathproblem_1[kind_pathproblem_1.uri != 'scli-dyys dummy value']
    # #
    return kind_pathproblem_1

def joins_for_relatedLocations(tgraph, sf_2683):
    """ 
    Return table providing the  `relatedLocations` and `locations` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    # Form the relatedLocation dataframe via joins, starting from the union of
    # relatedLocations from `kind problem` (sf(4055)) and `kind path-problem`
    # (sf(9699)).
    # 
    related_locations_1 = (
        pd.concat([sf(4055)[['relatedLocations', 'struct_id']], sf(9699)[['relatedLocations', 'struct_id']]])
        .merge(af('0350'), how="left", left_on='relatedLocations', right_on='array_id', validate="1:m")
        .drop(columns=['relatedLocations', 'array_id', 'value_index', 'type_at_index'])
        # 
        .merge(sf(2683), how="left", left_on='id_or_value_at_index', right_on='struct_id',
               suffixes=("_4055_9699", "_2683"), validate="1:m")
        .drop(columns=['struct_id_2683', 'id_or_value_at_index'])
        # 
        .merge(sf(4963), how="left", left_on='physicalLocation', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'physicalLocation'])
        # 
        .merge(sf(6299), how="left", left_on='region', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'region'])
        # 
        .merge(sf(2685), how="left", left_on='artifactLocation', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'artifactLocation'])
        # 
        .merge(sf(2774), how="left", left_on='message', right_on='struct_id', validate="1:m")
        .drop(columns=['struct_id', 'message'])
    )

    # Keep columns of interest
    related_locations_2 = (related_locations_1[['struct_id_4055_9699', 'uri', 'startLine', 'startColumn', 'endLine', 'endColumn', 'text']]
          .rename({'text': 'message', 'struct_id_4055_9699': 'struct_id'}, axis='columns'))

    # Remove dummy locations previously injected by signature.fillsig
    related_locations_3 = related_locations_2[related_locations_2.uri != 'scli-dyys dummy value']

    return related_locations_3

def joins_for_project(tgraph):
    """ 
    Return table providing the `project` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    project_df = (
        af(6785)
        #
        .merge(sf(3739), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id', 'array_id', 'type_at_index'])
        #
        .merge(sf(6787), how="left", left_on='sarif_content', right_on='struct_id', validate="1:m")
        .drop(columns=['sarif_content', 'struct_id'])
        .rename(columns={"version": "version_6787"})
        #
        .merge(af('0177'), how="left", left_on='runs', right_on='array_id',
               suffixes=("_6785", "_0177"), validate="1:m")
        .drop(columns=['runs', 'array_id', 'type_at_index'])
        #
        .merge(sf(3388), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        # 
        # .merge(af(7069), how="left", left_on='newlineSequences', right_on='array_id',
        #        validate="1:m")
        # .drop(columns=['newlineSequences', 'array_id', 'type_at_index'])
        .drop(columns=['newlineSequences'])
        #
        .merge(sf(9543), how="left", left_on='properties', right_on='struct_id', validate="1:m")
        .drop(columns=['properties', 'struct_id'])
        #
        # tool - driver - rules - defaultConfiguration - ( properties - tags )
        # 
        .merge(sf(8972), how="left", left_on='tool', right_on='struct_id', validate="1:m")
        .drop(columns=['tool', 'struct_id'])
        # 
        .merge(sf(7820), how="left", left_on='driver', right_on='struct_id', validate="1:m")
        .drop(columns=['driver', 'struct_id'])
        .rename(columns={"version": "driver_version_7820", "name": "driver_name_7820"})
        # 
        .merge(af(8754), how="left", left_on='rules', right_on='array_id', validate="1:m")
        .drop(columns=['rules', 'array_id', 'type_at_index'])
        .rename(columns={"value_index": "rule_value_index_8754"}) # rule index
        #
        .merge(sf(6818), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        .rename(columns={"id": "rule_id_6818", "name": "rule_name_6818"})
        # 
        .merge(sf(8581), how="left", left_on='defaultConfiguration', right_on='struct_id', validate="1:m")
        .drop(columns=['defaultConfiguration', 'struct_id'])
        # 
        .merge(sf(2774), how="left", left_on='fullDescription', right_on='struct_id', validate="1:m")
        .drop(columns=['fullDescription', 'struct_id'])
        .rename(columns={"text": "rule_fullDescription_6818"})
        # 
        .merge(sf(2774), how="left", left_on='shortDescription', right_on='struct_id', validate="1:m")
        .drop(columns=['shortDescription', 'struct_id'])
        .rename(columns={"text": "rule_shortDescription_6818"})
        # 
        .merge(sf(7849), how="left", left_on='properties', right_on='struct_id', validate="1:m")
        .drop(columns=['properties', 'struct_id'])
        # 
        .merge(af(7069), how="left", left_on='tags', right_on='array_id', validate="1:m")
        .drop(columns=['tags', 'array_id', 'type_at_index'])
        .rename(columns={"value_index": "tag_index_7069", "id_or_value_at_index": "tag_text_7069"})
        # versionControlProvenance - repositoryUri
        # The merge with af(8754) replicates versionControlProvenance, no 1:m validation
        .merge(af(5511), how="left", left_on='versionControlProvenance', right_on='array_id')
        .drop(columns=['versionControlProvenance', 'array_id', 'type_at_index'])
        .rename(columns={"value_index": "versionControl_value_index_5511"})
        # 
        .merge(sf(3081), how="left", left_on='id_or_value_at_index', right_on='struct_id')
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        #
    )
    return project_df

def joins_for_artifacts(tgraph):
    """ 
    Return table providing the `artifacts` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    artifacts_df = (
        af(4640)
        #
        .merge(sf(5277), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id', 'type_at_index'])
        .rename(columns={"value_index": "artifact_index_4640"})
        #
        .merge(sf(2685), how="left", left_on='location', right_on='struct_id', validate="1:m")
        .drop(columns=['location', 'struct_id'])
        .rename(columns={"index": "location_index_2685", "uri": "location_uri_2685",
                         "uriBaseId": "location_uriBaseId_2685"})
    )
    return artifacts_df
