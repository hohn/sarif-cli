""" Collection of joins for the derived tables

"""
from . import snowflake_id

import logging
import numpy
import pandas as pd
import re
from sarif_cli import hash
from sarif_cli import status_writer

class ZeroResults(Exception):
    pass

#
# Column types for scan-related pandas tables
# 
class ScanTablesTypes:
    scans = {
        "id"                   : pd.UInt64Dtype(),
        "commit_id"            : pd.StringDtype(),
        "project_id"           : pd.UInt64Dtype(),
        "db_create_start"      : numpy.dtype('M'),
        "db_create_stop"       : numpy.dtype('M'),
        "scan_start_date"      : numpy.dtype('M'),
        "scan_stop_date"       : numpy.dtype('M'),
        "tool_name"            : pd.StringDtype(),
        "tool_version"         : pd.StringDtype(),
        "tool_query_commit_id" : pd.StringDtype(),
        "sarif_file_name"      : pd.StringDtype(),
        "results_count"        : pd.Int64Dtype(),
        "rules_count"          : pd.Int64Dtype(),
    }
    results = {
        'id'               : pd.UInt64Dtype(),
        'scan_id'          : pd.UInt64Dtype(),
        'query_id'         : pd.StringDtype(),
        'query_kind'       : pd.StringDtype(),
        'query_precision'  : pd.StringDtype(),
        'query_severity'   : pd.StringDtype(),
        'query_tags'       : pd.StringDtype(),

        'codeFlow_id'      : pd.UInt64Dtype(),
        
        'message'          : pd.StringDtype(),
        'message_object'   : numpy.dtype('O'),
        'location'         : pd.StringDtype(),
        
        'source_startLine' : pd.Int64Dtype(),
        'source_startCol'  : pd.Int64Dtype(),
        'source_endLine'   : pd.Int64Dtype(),
        'source_endCol'    : pd.Int64Dtype(),
        
        'sink_startLine'   : pd.Int64Dtype(),
        'sink_startCol'    : pd.Int64Dtype(),
        'sink_endLine'     : pd.Int64Dtype(),
        'sink_endCol'      : pd.Int64Dtype(),
        
        # TODO Find high-level info from query name or tags?
        'source_object'    : numpy.dtype('O'),
        'sink_object'      : numpy.dtype('O'),
    }
    projects = {
        "id"                 : pd.UInt64Dtype(),
        "project_name"       : pd.StringDtype(),
        "creation_date"      : numpy.dtype('M'),
        "repo_url"           : pd.StringDtype(),
        "primary_language"   : pd.StringDtype(),
        "languages_analyzed" : pd.StringDtype(),
    }

#
# Projects table
# 
def joins_for_projects(basetables, external_info):
    """ 
    Form the 'projects' table for the ScanTables dataclass
    """
    b = basetables; e = external_info
   
    # if the sarif does not have versionControlProvenance, semmle.sourceLanguage ect
    # there is no reliable way to know the project name 
    # and will still need to use a guess about the project id
    if "repositoryUri" in b.project:
        repo_url = b.project.repositoryUri[0]
         # For a repository url of the form
        #   (git|https)://*/org/project.*
        # use the org/project part as the project_name.
        # 
        url_parts = re.match(r'(git|https)://[^/]+/([^/]+)/(.*).git', repo_url)
        if url_parts:
            project_name = f"{url_parts.group(2)}-{url_parts.group(3)}"
            project, component = e.sarif_file_name.rstrip().split('/')
            # if the runners guess from the filename was bad, replace with real info
            # and continue to use that scanspec to pass that around
            if project_name != project+"-"+component:
                e.project_id = hash.hash_unique(project_name.encode())
        else:
            project_name = pd.NA
    else:
        repo_url = "unknown"
        project_name = pd.NA
    
    res = pd.DataFrame(data={
        "id"                 : e.project_id,
        "project_name"       : project_name,
        "creation_date"      : pd.Timestamp(0.0, unit='s'), # TODO: external info 
        "repo_url"           : repo_url, 
        "primary_language"   : b.project['semmle.sourceLanguage'][0],
        "languages_analyzed" : ",".join(list(b.project['semmle.sourceLanguage']))
    }, index=[0])

    # Force all column types to ensure appropriate formatting
    res1 = res.astype(ScanTablesTypes.projects).reset_index(drop=True)
    return res1

#
# Scans table
# 
def joins_for_scans(basetables, external_info, scantables, sarif_type):
    """ 
    Form the `scans` table for the ScanTables dataclass
    """
    b = basetables; e = external_info
    driver_name = b.project.driver_name.unique()
    assert len(driver_name) == 1, "More than one driver name found for single sarif file."
    driver_version = b.project.driver_version.unique()
    assert len(driver_version) == 1, \
        "More than one driver version found for single sarif file."
    # TODO if commit id exists in external info for CLI gen'd sarif, add?
    if sarif_type == "LGTM":
        commit_id = b.project.revisionId[0]
    else:
        commit_id = "unknown"
    res = pd.DataFrame(data={
        "id"                   : e.scan_id,
        "commit_id"            : commit_id,
        "project_id"           : e.project_id,
        # TODO extract real date information from somewhere external
        "db_create_start"      : pd.Timestamp(0.0, unit='s'),
        "db_create_stop"       : pd.Timestamp(0.0, unit='s'),
        "scan_start_date"      : pd.Timestamp(0.0, unit='s'),
        "scan_stop_date"       : pd.Timestamp(0.0, unit='s'),
        # 
        "tool_name"            : driver_name[0],
        "tool_version"         : driver_version[0],
        "tool_query_commit_id" : pd.NA,
        "sarif_file_name"      : e.sarif_file_name,
        "results_count"        : scantables.results.shape[0],
        "rules_count"          : len(b.rules['id'].unique()),
    },index=[0])
    # Force all column types to ensure correct writing and type checks on reading.
    res1 = res.astype(ScanTablesTypes.scans).reset_index(drop=True)
    return res1

# 
# Results table
# 
def joins_for_results(basetables, external_info):
    """ 
    Form and return the `results` table
    """
    # Get one table per query_kind, then stack them, 
    #   problem
    #   path-problem
    #
    # Concatenation with an empty table triggers type conversion to float, so don't
    # include empty tables.
    tables = [_results_from_kind_problem(basetables, external_info),
              _results_from_kind_pathproblem(basetables, external_info)]
    stack = [table for table in tables if len(table) > 0]
    
    # Concatenation fails without at least one table, so avoid that.
    if len(stack) > 0:
        res = pd.concat(stack)
    else:
        if stack == []:
            logging.warning("Zero problem/path_problem results found in sarif "
                            "file but processing anyway.")
            status_writer.csv_write(status_writer.zero_results)
        res = tables[0]
        
    # Force all column types to ensure appropriate formatting
    res1 = res.astype(ScanTablesTypes.results).reset_index(drop=True)
    return res1

#id as primary key
def _populate_from_rule_table_code_flow_tag_text(basetable, flowtable):
    val = flowtable.rule_id.values[0]
    return basetable.rules.query("id == @val")["tag_text"].str.cat(sep='_')

#id as primary key
def _populate_from_rule_table_tag_text(basetable, i):
    val = basetable.kind_problem.rule_id[i]
    return basetable.rules.query("id == @val")["tag_text"].str.cat(sep='_')

#id as primary key
def _populate_from_rule_table(column_name, basetable, i):
    val = basetable.kind_problem.rule_id[i]
    return basetable.rules.query("id == @val")[column_name].head(1).item()

#id as primary key
def _populate_from_rule_table_code_flow(column_name, basetable, flowtable):
    val = flowtable.rule_id.values[0]
    return basetable.rules.query("id == @val")[column_name].head(1).item()

def _results_from_kind_problem(basetables, external_info):
    b = basetables; e = external_info
    flakegen = snowflake_id.Snowflake(2)
    res = pd.DataFrame(
        data={
            'id': [flakegen.next() for _ in range(len(b.kind_problem))],
            
            'scan_id' : e.scan_id,
            'query_id' : b.kind_problem.rule_id,
            'query_kind'       :  "problem",
            'query_precision'  :  [_populate_from_rule_table("precision", b, i) for i in range(len(b.kind_problem))],
            'query_severity'   :  [_populate_from_rule_table("problem.severity", b, i) for i in range(len(b.kind_problem))],
            'query_tags'   : [_populate_from_rule_table_tag_text(b, i) for i in range(len(b.kind_problem))],
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
                    'query_id' : cfid0ppt0.rule_id.values[0],
                    'query_kind'       : "path-problem",
                    'query_precision'  : _populate_from_rule_table_code_flow("precision", b, cfid0ppt0),
                    'query_severity'   : _populate_from_rule_table_code_flow("problem.severity", b, cfid0ppt0),
                    'query_tags'   : _populate_from_rule_table_code_flow_tag_text(b, cfid0ppt0),
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
