#!/usr/bin/env python3
""" This is part 2 of 2 hardcoded utility scripts.  This one downloads the sarif
    files for the `projects` collected by `sarif-download-projects.py` to
    subdirectories of ~/local/sarif/projects.pickle.
    
    Already downloaded files will not be tried again, so if this script fails it
    can just be rerun.
"""

import concurrent.futures
import pathlib
import pickle
import requests
import sys

LGTM_URL = "https://lgtm.com/"
SESSION = requests.Session()

# OUTPUT_DIRECTORY = pathlib.Path(__file__).parent
OUTPUT_DIRECTORY = pathlib.Path.home() / "local/sarif"
PROJECT_FILE = OUTPUT_DIRECTORY / "projects.pickle"

if not PROJECT_FILE.exists():
    sys.stderr.write("error: missing input file %s\n" % PROJECT_FILE)
    sys.exit(1)

OUTPUT_DIRECTORY.mkdir(mode=0o755, parents=True, exist_ok=True)

with open(PROJECT_FILE, "rb") as infile:
    projects = pickle.load(infile)

thread_pool = concurrent.futures.ThreadPoolExecutor(25)
futures = {}
any_failed = []
def process(index, pair):
    try:
        project_key, project = pair
        output_path = OUTPUT_DIRECTORY / project["url-identifier"] / "results.sarif"
        if output_path.exists():
            print("Already fetched %d/%d (%s)" % 
                  (index + 1, len(projects), project["url-identifier"]))
            return
        else:
            print("Processing project %d/%d (%s)..." %                   
                  (index + 1, len(projects), project["url-identifier"]))

        # Get latest analysis information.
        analysis_summary_url = "%sapi/v1.0/analyses/%d/commits/latest" % (LGTM_URL, project_key)
        response = SESSION.get(analysis_summary_url)
        response.raise_for_status()
        analysis_summary = response.json()
        analysis_id = analysis_summary["id"]

        # Get SARIF export.
        sarif_url = "%sapi/v1.0/analyses/%s/alerts" % (LGTM_URL, analysis_id)
        response = SESSION.get(sarif_url)
        response.raise_for_status()
        # And save it 
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(response.text)
    except:
        any_failed.append( (index, pair) )

for index, pair in enumerate(projects.items()):
    try:
        futures[pair[0]] = thread_pool.submit(process, index, pair)
    except RuntimeError:
        pass
thread_pool.shutdown()

for index, pair in any_failed:
    print("Processing failed for %d, %s:" % (index, pair))
    print("Re-run to try those again")
