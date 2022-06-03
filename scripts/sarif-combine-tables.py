#!/usr/bin/env python3
#
# Traverse the org/project.scantables/ directories produced by ./sarif-runner.py
# and concatenate the collection of (codeflows.csv results.csv scans.csv
# projects.csv) tables into 4 tables.
#
import os
import sys
from datetime import datetime
import pandas as pd

#
# TODO: Factor out functionality / structures in common with ./sarif-runner.py
# 

# 
# Parameters
# 
max_files = 80000
sarif_file_list = 'sarif-files.txt'
combined_tables_dir = 'sarif-scantables-combined'

#
# Utilities
# 
_extract_scans_tables = { 
    "scans" : [],
    "results" : [],
    "projects" : [], 
    "codeflows" : [],
}

def _all_csv_files_exist(output_dir):
    for file_prefix in _extract_scans_tables.keys():
        csv_fname = os.path.join(output_dir, file_prefix + ".csv")
        if not os.path.exists(csv_fname):
            return False
    return True

#
# Prepare output directory first; can't really run without it
# 
try: os.mkdir(combined_tables_dir, mode=0o755)
except FileExistsError: pass

#
# Collect sarif file information
# 
paths = open(sarif_file_list, 'r').readlines()

#
# Traverse all possible output directories
# 
count = 0
for path in paths:
    count += 1
    if count > max_files: break
    # 
    # Paths and components
    # 
    path = path.rstrip()
    project, sarif_file = path.split('/')
    component = sarif_file.removesuffix('.json')
    #
    # Validate data directory
    #
    output_dir = os.path.join(project, component + ".scantables")
    if not os.path.exists(output_dir):
        continue
    if not _all_csv_files_exist(output_dir):
        continue
    #
    # Append data for every table
    #
    for file_prefix in _extract_scans_tables.keys():
        csv_fname = os.path.join(output_dir, file_prefix + ".csv")
        data = pd.read_csv(csv_fname)
        _extract_scans_tables[file_prefix].append(data)

    # Some timing information
    if count % 100 == 0:
        print("{:6} {:6}/{:6}".format("COUNT", count, len(paths)))
        print("{:6} {}".format("DATE", datetime.now().isoformat()))
        sys.stdout.flush()
              
# 
# Create and write the combined dataframes
# 
for file_prefix in _extract_scans_tables.keys():
    all = pd.concat(_extract_scans_tables[file_prefix], ignore_index=True, axis='index')

    with open(os.path.join(combined_tables_dir, file_prefix + ".csv"), 'w') as fh:
        all.to_csv(fh, index=False)

