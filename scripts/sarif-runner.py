#!/usr/bin/env python3
import subprocess
import json
import os
import pickle
from datetime import datetime
#
# Collect sarif file information
# 
paths = open('sarif-files.txt', 'r').readlines()
max_files = 80000

# Use saved status, only re-run failed attempts
if  os.path.exists("successful_runs"):
    with open("successful_runs", "rb") as infile:
        successful_runs = pickle.load(infile)
else:
    successful_runs = set()

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
    # Scan specification
    # 
    scan_spec = {
        "project_id": abs(hash(project + component)),
        "scan_id": int(os.path.getmtime(path)),
        "sarif_file_name": path,
    }
    scan_spec_file = os.path.join(project, component + ".scanspec")
    with open(scan_spec_file, 'w') as fp:
        json.dump(scan_spec, fp)
    # 
    # Table output directory
    # 
    output_dir = os.path.join(project, component + ".scantables")
    try: os.mkdir(output_dir, mode=0o755)
    except FileExistsError: pass
    #
    # Run sarif-extract-scans
    # 
    if path in successful_runs:
        # Don't rerun
        continue

    # Some timing information
    if count % 10 == 0:
        print("{:6} {}".format("DATE", datetime.now().isoformat()))
    
    # Save occasionally
    if count % 10 == 0:
        with open("successful_runs", 'wb') as outfile:
            pickle.dump(successful_runs, outfile)

    scan_log_file = os.path.join(project, component + ".scanlog")
    runstats = subprocess.run(['sarif-extract-scans', scan_spec_file, output_dir],
                              capture_output=True, text=True)
    if runstats.returncode == 0:
        print("{:6} {}".format("OK", path))
        successful_runs.add(path)
    else:
        print("{:6} {} {}".format("FAIL", path, scan_log_file))
        # log error
        with open(scan_log_file, 'w') as fp:
            fp.write(runstats.stderr)
        # report only tail
        print("{:6} {}".format("", "Error tail: "))
        for t1 in runstats.stderr.split('\n')[-6:-1]:
            print("{:6} {}".format("", t1))    
