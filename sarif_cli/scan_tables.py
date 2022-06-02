""" Collection of joins for the derived tables

"""
import pandas as pd
from . import snowflake_id

#
# Scans table
# 
def joins_for_scans(basetables, external_info, scantables):
    """ 
    Form the `scans` table for the ScanTables dataclass
    """
    b = basetables; e = external_info
    driver_name = b.project.driver_name.unique()
    assert len(driver_name) == 1, "More than one driver name found for single sarif file."
    driver_version = b.project.driver_version.unique()
    assert len(driver_version) == 1, \
        "More than one driver version found for single sarif file."
    res = pd.DataFrame(data={
        "id"                   : e.scan_id,
        "commit_id"            : pd.NA,
        "project_id"           : e.project_id,
        # 
        "db_create_start"      : pd.NA,
        "db_create_stop"       : pd.NA,
        "scan_start_date"      : pd.NA,
        "scan_stop_date"       : pd.NA,
        # 
        "tool_name"            : driver_name[0],
        "tool_version"         : driver_version[0],
        "tool_query_commit_id" : pd.NA,
        "sarif_file_name"      : e.sarif_file_name,
        "results_count"        : scantables.results.shape[0],
        "rules_count"          : len(b.rules['id'].unique()),
    },index=[0])
    return res

# 
# Results table
# 
def joins_for_results(basetables, external_info):
    """ 
    Form and return the `results` table
    """
    # Get one table per result_type, then stack them, 
    #   kind_problem
    #   kind_pathproblem
    #
    # Concatenation with an empty table triggers type conversion to float, so don't
    # include empty tables
    res = pd.concat(
        [table for table in [_results_from_kind_problem(basetables, external_info),
                             _results_from_kind_pathproblem(basetables, external_info)]
         if len(table) > 0])
    return res

def _results_from_kind_problem(basetables, external_info):
    b = basetables; e = external_info
    flakegen = snowflake_id.Snowflake(2)
    res = pd.DataFrame(
        data={
            'id': [flakegen.next() for _ in range(len(b.kind_problem))],
            
            'scan_id' : e.scan_id,
            'query_id' : e.ql_query_id,
            
            'result_type' : "kind_problem",
            'codeFlow_id' : 0,      # link to codeflows (kind_pathproblem only, NULL here)
            
            'message': b.kind_problem.message_text,
            'message_object' : pd.NA,
            'location': b.kind_problem.location_uri,
            
            # for kind_problem, use the same location for source and sink
            'source_startLine' : b.kind_problem.location_startLine,
            'source_startCol' : b.kind_problem.location_startColumn,
            'source_endLine' : b.kind_problem.location_endLine,
            'source_endCol' : b.kind_problem.location_endColumn,
            
            'sink_startLine' : b.kind_problem.location_startLine,
            'sink_startCol' : b.kind_problem.location_startColumn,
            'sink_endLine' : b.kind_problem.location_endLine,
            'sink_endCol' : b.kind_problem.location_endColumn,
            
            'source_object' : pd.NA, # TODO: find high-level info from query name or tags?
            'sink_object' : pd.NA,
        })
    # Force column type(s) to avoid floats in output.
    res1 = res.astype({ 'id' : 'uint64', 'scan_id': 'uint64'}).reset_index(drop=True)

    return res1


def _results_from_kind_pathproblem(basetables, external_info):
    # 
    # Only get source and sink, no paths.  This implies one codeflow_index and one
    # threadflow_index, no repetitions.  
    # 
    b = basetables; e = external_info
    flakegen = snowflake_id.Snowflake(3)

    # The sarif tables have relatedLocation information, which result in multiple
    # results for a single codeFlows_id -- the expression
    #     b.kind_pathproblem[b.kind_pathproblem['codeFlows_id'] == cfid0]
    # produces multiple rows.
    # 
    # The `result` table has no entry to distinguish these, so we use a simplified
    # version of `kind_pathproblem`.

    reduced_kind_pathp = b.kind_pathproblem.drop(
        columns=[
            'relatedLocation_array_index',
            'relatedLocation_endColumn',
            'relatedLocation_endLine',
            'relatedLocation_id',
            'relatedLocation_index',
            'relatedLocation_message',
            'relatedLocation_startColumn',
            'relatedLocation_startLine',
            'relatedLocation_uri',
            'relatedLocation_uriBaseId',
        ])

    # Per codeflow_id taken from b.kind_pathproblem table, it should suffice to
    # take one codeflow_index, one threadflow_index, first and last location_index
    # from the b.codeflows table.
    # 
    # To ensure nothing is missed, collect all the entries and then check for
    # unique rows.
    cfids = reduced_kind_pathp['codeFlows_id'].unique()

    source_sink_coll = []
    for cfid0 in cfids:
        cfid0t0 = b.codeflows[b.codeflows['codeflow_id'] == cfid0]
        cfid0ppt0 = reduced_kind_pathp[reduced_kind_pathp['codeFlows_id'] ==
                                       cfid0].drop_duplicates()
        assert cfid0ppt0.shape[0] == 1, \
            "Reduced kind_pathproblem table still has multiple entries"
        for cfi0 in range(0, cfid0t0['codeflow_index'].max()+1):
            cf0 = cfid0t0[cfid0t0['codeflow_index'] == cfi0]
            for tfi0 in range(0, cf0['threadflow_index'].max()+1):
                tf0 = cf0[ cf0['threadflow_index'] == tfi0 ]
                loc_first = tf0['location_index'].min()
                loc_last = tf0['location_index'].max()
                source = tf0[tf0['location_index'] == loc_first]
                sink = tf0[tf0['location_index'] == loc_last]
                # Note that we're adding the unique row ids after the full table
                # is done, below.
                res = {
                    'scan_id' : e.scan_id,
                    'query_id' : e.ql_query_id,
                    # 
                    'result_type' : "kind_pathproblem",
                    'codeFlow_id' : cfid0,
                    # 
                    'message': cfid0ppt0.message_text.values[0],
                    'message_object' : pd.NA,
                    'location': cfid0ppt0.location_uri.values[0],
                    # 
                    'source_location' : source.uri.values[0],
                    'source_startLine' : source.startLine.values[0],
                    'source_startCol' : source.startColumn.values[0],
                    'source_endLine' : source.endLine.values[0],
                    'source_endCol' : source.endColumn.values[0],
                    # 
                    'sink_location' : sink.uri.values[0],
                    'sink_startLine' : sink.startLine.values[0],
                    'sink_startCol' : sink.startColumn.values[0],
                    'sink_endLine' : sink.endLine.values[0],
                    'sink_endCol' : sink.endColumn.values[0],
                    #
                    'source_object' : pd.NA, # TODO: find high-level info from
                                             # query name or tags?
                    'sink_object' : pd.NA,
                }
                source_sink_coll.append(res)
    results0 = pd.DataFrame(data=source_sink_coll).drop_duplicates().reset_index(drop=True)

    # Add the snowflake ids
    results0['id'] = [flakegen.next() for _ in range(len(results0))]

    # The 'scan_id' column is needed for astype
    if len(results0) == 0:
        results0['scan_id'] = []

    # Force column type(s) to avoid floats in output.
    results1 = results0.astype({ 'id' : 'uint64', 'scan_id': 'uint64'}).reset_index(drop=True)

    return results1
