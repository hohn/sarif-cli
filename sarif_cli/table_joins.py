""" Collection of joins for the base tables provided by typegraph.attach_tables()

    The `problem` and `path-problem` entries provide that information; the
    `relatedLocations` table provides the details when multiple results are
    present for either.  `project` is the high-level overview; `artifacts` 
    provides those for the other tables.
"""
import pandas as pd
import re
from .typegraph import tagged_array_columns, tagged_struct_columns

class BaseTablesTypes:
    codeflows = {
        "codeflow_id" : pd.UInt64Dtype(),
        "codeflow_index" : pd.Int64Dtype(),
        "threadflow_index" : pd.Int64Dtype(),
        "location_index" : pd.Int64Dtype(),
        "endColumn" : pd.Int64Dtype(),
        "endLine" : pd.Int64Dtype(),
        "startColumn" : pd.Int64Dtype(),
        "startLine" : pd.Int64Dtype(),
        "artifact_index" : pd.Int64Dtype(),
        "uri" : pd.StringDtype(),
        "uriBaseId" : pd.StringDtype(),
        "message" : pd.StringDtype(),
    }

def joins_for_af_0350_location(tgraph):
    """ 
    Join all the tables used by 0350's right side into one.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    sft = lambda id: sf(id).rename(columns = tagged_struct_columns(tgraph, id))
    aft = lambda id: af(id).rename(columns = tagged_array_columns(tgraph, id))
    
    af_0350_location =  (
        aft('0350')
        # 
        .merge(sft(2683), how="left", left_on='t0350_id_or_value_at_index', right_on='t2683_struct_id',
               validate="1:m")
        .drop(columns=['t0350_id_or_value_at_index', 't2683_struct_id', 't0350_type_at_index'])
        # 
        .merge(sft(4963), how="left", left_on='t2683_physicalLocation', right_on='t4963_struct_id',
               validate="1:m")
        .drop(columns=['t2683_physicalLocation', 't4963_struct_id'])
        # 
        .merge(sft(6299), how="left", left_on='t4963_region', right_on='t6299_struct_id', 
               validate="1:m")
        .drop(columns=['t4963_region', 't6299_struct_id'])
        # 
        .merge(sft(2685), how="left", left_on='t4963_artifactLocation', right_on='t2685_struct_id', 
               validate="1:m")
        .drop(columns=['t4963_artifactLocation', 't2685_struct_id'])
        # 
        .merge(sft(2774), how="left", left_on='t2683_message', right_on='t2774_struct_id', 
               validate="1:m")
        .drop(columns=['t2683_message', 't2774_struct_id'])
        #
        .rename(columns={'t0350_array_id'    : 'm0350_location_array_id',
                         't0350_value_index' : 'm0350_location_array_index',
                         't2683_id'          : 'm0350_location_id',
                         't6299_endColumn'   : 'm0350_location_endColumn', 
                         't6299_endLine'     : 'm0350_location_endLine', 
                         't6299_startColumn' : 'm0350_location_startColumn', 
                         't6299_startLine'   : 'm0350_location_startLine', 
                         't2685_index'       : 'm0350_location_index',
                         't2685_uri'         : 'm0350_location_uri',
                         't2685_uriBaseId'   : 'm0350_location_uriBaseId',
                         't2774_text'        : 'm0350_location_message',
                         })
    )
    return af_0350_location

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

def joins_for_problem(tgraph, af_0350_location):
    """ 
    Return table providing the `problem` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    sft = lambda id: sf(id).rename(columns = tagged_struct_columns(tgraph, id))
    aft = lambda id: af(id).rename(columns = tagged_array_columns(tgraph, id))
    # 
    # Form the message dataframe (@kind problem) via joins
    # 

    kind_problem_1 = (
        aft(6343)
        .merge(sft(4055), how="inner",
               left_on='t6343_id_or_value_at_index', right_on='t4055_struct_id', 
               validate="1:m")
        .drop(columns=['t6343_type_at_index', 't6343_id_or_value_at_index',
                       't4055_struct_id']) 
        #
        .merge(af_0350_location, how="left", left_on='t4055_locations',
               right_on='m0350_location_array_id', validate="1:m")
        .drop(columns=['t4055_locations', 'm0350_location_array_id'])
        #
        .merge(af_0350_location.rename(columns=lambda x: re.sub('m0350_location',
                                                                'm0350_relatedLocation',
                                                                x)),
               how="left", left_on='t4055_relatedLocations',
               right_on='m0350_relatedLocation_array_id', validate="1:m")
        .drop(columns=['t4055_relatedLocations', 'm0350_relatedLocation_array_id'])
        #
        .merge(sft(2774), how="left", left_on='t4055_message', right_on='t2774_struct_id')
        .drop(columns=['t4055_message', 't2774_struct_id'])
        .rename(columns={"t2774_text": "t4055_message_text"})
        # 
        .merge(sft(4199), how="left", left_on='t4055_partialFingerprints',
               right_on='t4199_struct_id')
        .drop(columns=['t4055_partialFingerprints', 't4199_struct_id'])
        #
        .merge(sft(3942), how="left", left_on='t4055_rule',
               right_on='t3942_struct_id')
        .drop(columns=['t4055_rule', 't3942_struct_id'])
    )

    kind_problem_2 = (
        kind_problem_1
        .rename({
            't6343_array_id'     : 'results_array_id',
            't6343_value_index'  : 'results_array_index',
            't4055_ruleId'       : 'ruleId',
            't4055_ruleIndex'    : 'ruleIndex',
            't4055_message_text' : 'message_text',
            't3942_id'           : 'rule_id',
            't3942_index'        : 'rule_index',
        }, axis='columns')
        # Strip type prefix for the rest
        .rename(columns = lambda x: re.sub('m0350_|t4199_', '', x))
    )
    # # TODO potential cleanup
    # # Remove dummy locations previously injected by signature.fillsig
    # kind_problem_2 = kind_problem_1[kind_problem_1.uri != 'scli-dyys dummy value']
    # #
    return kind_problem_2


def joins_for_codeflows(tgraph, sf_2683):
    """ 
    Return the table providing the `codeFlows` for a `path-problem table.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    #
    codeflows = (
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
    codeflows_1 = (
        codeflows
        .drop(columns=['id_2683'])
        .rename({
            't9799_array_id': 'codeflow_id',
            't9799_idx': 'codeflow_index',
            't1597_idx': 'threadflow_index',
            't1075_locations_idx': 'location_index',
            'location_index_2685': 'artifact_index',
            'message_text_2683': 'message',
        }, axis='columns')
    )
    codeflows_2 = codeflows_1.astype(BaseTablesTypes.codeflows).reset_index(drop=True)
    return codeflows_2

def joins_for_path_problem(tgraph, af_0350_location):
    """ 
    Return table providing the `path-problem` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    sft = lambda id: sf(id).rename(columns = tagged_struct_columns(tgraph, id))
    aft = lambda id: af(id).rename(columns = tagged_array_columns(tgraph, id))

    kind_pathproblem_1 = (
        aft(6343)
        .merge(sft(9699), how="inner", left_on='t6343_id_or_value_at_index', right_on='t9699_struct_id',
               validate="1:m")
        .drop(columns=['t6343_id_or_value_at_index', 't9699_struct_id', 't6343_type_at_index'])
        #
        .merge(af_0350_location, how="left", left_on='t9699_locations',
               right_on='m0350_location_array_id', validate="1:m")
        .drop(columns=['t9699_locations', 'm0350_location_array_id'])
        #
        .merge(af_0350_location.rename(columns=lambda x: re.sub('m0350_location',
                                                                'm0350_relatedLocation',
                                                                x)),
               how="left", left_on='t9699_relatedLocations',
               right_on='m0350_relatedLocation_array_id', validate="1:m")
        .drop(columns=['t9699_relatedLocations', 'm0350_relatedLocation_array_id'])
        #
        .merge(sft(2774), how="left", left_on='t9699_message', right_on='t2774_struct_id')
        .drop(columns=['t9699_message', 't2774_struct_id'])
        .rename(columns={"t2774_text": "t9699_message_text"})
        # 
        .merge(sft(4199), how="left", left_on='t9699_partialFingerprints',
               right_on='t4199_struct_id')
        .drop(columns=['t9699_partialFingerprints', 't4199_struct_id'])
        #
        .merge(sft(3942), how="left", left_on='t9699_rule',
               right_on='t3942_struct_id')
        .drop(columns=['t9699_rule', 't3942_struct_id'])
    )
    strip_colums = lambda x: re.sub('t9699_|m0350_|t4199_', '', x)
    kind_pathproblem_2 = (kind_pathproblem_1
                          .rename({
                              't6343_array_id'     : 'results_array_id',
                              't6343_value_index'  : 'results_array_index',
                              't9699_codeFlows'    : 'codeFlows_id',
                              't9699_ruleId'       : 'ruleId',
                              't9699_ruleIndex'    : 'ruleIndex',
                              't9699_message_text' : 'message_text',
                              't3942_id'           : 'rule_id',
                              't3942_index'        : 'rule_index',
                          }, axis='columns')
                          # Strip type prefix for the rest
                          .rename(columns = strip_colums))

    # # TODO potential cleanup
    # # Remove dummy locations previously injected by signature.fillsig
    # kind_pathproblem_2 = kind_pathproblem_1[kind_pathproblem_1.uri != 'scli-dyys dummy value']
    # #
    return kind_pathproblem_2

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
    Return table providing the `project` information for sarif-extract-multi.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    project_df = (
        af(7481)
        #
        .merge(sf(3452), how="left", left_on='id_or_value_at_index', right_on='struct_id', validate="1:m")
        .drop(columns=['id_or_value_at_index', 'struct_id', 'array_id', 'type_at_index'])
        #
        .merge(sf(6787), how="left", left_on='sarif_content', right_on='struct_id', validate="1:m")
        .drop(columns=['sarif_content', 'struct_id'])
        .rename(columns={"version": "version_6787"})
        #
        .merge(af('0177'), how="left", left_on='runs', right_on='array_id',
               suffixes=("_7481", "_0177"), validate="1:m")
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
    # Keep columns of interest
    project_df_1 = (
        project_df
        .drop(columns=['value_index_7481', 'versionControl_value_index_5511'])
        .rename({
            'version_6787': 'sarif_version',
            'value_index_0177': 'run_index',
            'driver_name_7820': 'driver_name',
            'driver_version_7820': 'driver_version',
        }, axis='columns')
    )
    return project_df_1

def joins_for_project_single(tgraph):
    """ 
    Return table providing the `project` information for sarif-extract-scans
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    # 
    project_df = (
        sf(6787)
        .rename(columns={"version": "version_6787", "struct_id": "struct_id_6787"})
        #
        .merge(af('0177'), how="left", left_on='runs', right_on='array_id',
               validate="1:m")
        .drop(columns=['runs', 'array_id', 'type_at_index'])
        .rename(columns={"value_index": "value_index_0177"})
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
        .merge(af(5511), how="left", left_on='versionControlProvenance', right_on='array_id')
        .drop(columns=['versionControlProvenance', 'array_id', 'type_at_index'])
        .rename(columns={"value_index": "versionControl_value_index_5511"})
        # 
        .merge(sf(3081), how="left", left_on='id_or_value_at_index', right_on='struct_id')
        .drop(columns=['id_or_value_at_index', 'struct_id'])
        #
    )
    # Keep columns of interest
    project_df_1 = (
        project_df
        .drop(columns=['struct_id_6787', 'versionControl_value_index_5511'])
        .rename({
            'version_6787': 'sarif_version',
            'value_index_0177': 'run_index',
            'driver_name_7820': 'driver_name',
            'driver_version_7820': 'driver_version',
        }, axis='columns')
    )
    return project_df_1

def joins_for_rules(tgraph):
    """ 
    Return table providing the `rules` information.
    """
    # Access convenience functions
    sf = lambda num: tgraph.dataframes['Struct' + str(num)]
    sft = lambda id: sf(id).rename(columns = tagged_struct_columns(tgraph, id))
    af = lambda num: tgraph.dataframes['Array' + str(num)]
    aft = lambda id: af(id).rename(columns = tagged_array_columns(tgraph, id))
    # 
    rules_df = (
        aft(8754)
        # 
        .drop(columns=['t8754_type_at_index'])
        # 
        .merge(sft(6818), how="left", left_on='t8754_id_or_value_at_index',
               right_on='t6818_struct_id',
               validate="1:m")
        .drop(columns=['t8754_id_or_value_at_index', 't6818_struct_id'])
        # 
        .merge(sft(8581), how="left", left_on='t6818_defaultConfiguration',
               right_on='t8581_struct_id', validate="1:m") 
        .drop(columns=['t6818_defaultConfiguration', 't8581_struct_id'])
        # 
        .merge(sft(2774), how="left", left_on='t6818_fullDescription',
               right_on='t2774_struct_id', validate="1:m") 
        .drop(columns=['t6818_fullDescription', 't2774_struct_id'])
        .rename(columns={'t2774_text': "t6818_t2774_fullDescription"})
        # 
        .merge(sft(2774), how="left", left_on='t6818_shortDescription',
               right_on='t2774_struct_id', validate="1:m") 
        .drop(columns=['t6818_shortDescription', 't2774_struct_id'])
        .rename(columns={"t2774_text": 't6818_t2774_shortDescription'})
        # 
        .merge(sft(7849), how="left", left_on='t6818_properties',
               right_on='t7849_struct_id', validate="1:m") 
        .drop(columns=['t6818_properties', 't7849_struct_id'])
        # 
        .merge(aft(7069), how="left", left_on='t7849_tags',
               right_on='t7069_array_id', validate="1:m")  
        .drop(columns=['t7849_tags', 't7069_array_id', 't7069_type_at_index'])
    )
    rules_2 = (
        rules_df
        .rename({
            't8754_array_id'             : 'rules_array_id',
            't8754_value_index'          : 'rules_array_index',
            't7069_value_index'          : 'tag_index',
            't7069_id_or_value_at_index' : 'tag_text',
        }, axis='columns')
        # Strip type prefix for the rest
        .rename(columns = lambda x: re.sub('t6818_t2774_|t6818_|t8581_|t7849_', '', x))
    )
    return rules_2

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
    )
    # Keep columns of interest and rename
    df_1 = (
        artifacts_df
        .rename({
            'array_id': 'artifacts_id',
            'artifact_index_4640': 'artifacts_array_index',
        }, axis='columns')
    )

    if (df_1['artifacts_array_index'] == df_1['index']).all():
        df_1 = df_1.drop(columns=['artifacts_array_index'])

    return df_1
