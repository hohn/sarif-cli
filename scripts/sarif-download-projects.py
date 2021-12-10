#!/usr/bin/env python3
""" This is part 1 of 2 hardcoded utility scripts.  This one downloads the first
    1000 project pages from lgtm.com and saves the `projects` information in
    ~/local/sarif/projects.pickle for use by `sarif-download-sarif.py`
"""
import concurrent.futures
import pathlib
import pickle
import requests
import sys

LGTM_URL = "https://lgtm.com/"
SESSION = requests.Session()

OUTPUT_DIRECTORY = pathlib.Path(__file__).parent
OUTPUT_DIRECTORY = pathlib.Path.home() / "local/sarif"
PROJECT_FILE = OUTPUT_DIRECTORY / "projects.pickle"

if PROJECT_FILE.exists():
    sys.stderr.write("error: output file %s exists\n" % PROJECT_FILE)
    sys.exit(1)

OUTPUT_DIRECTORY.mkdir(mode=0o755, parents=True, exist_ok=True)

projects = {}
page = 1
current_projects_url = "%sapi/v1.0/projects/" % LGTM_URL
while page < 1000:
	print("Fetching projects page %d..." % page)
	page += 1
	response = SESSION.get(current_projects_url)
	response.raise_for_status()
	response_data = response.json()
	for item in response_data["data"]:
		projects[item["id"]] = item
	if "nextPageUrl" in response_data:
		current_projects_url = response_data["nextPageUrl"]
	else:
		break

# Save them
with open(PROJECT_FILE, 'wb') as outfile:
    pickle.dump(projects, outfile)

print("All projects fetched, saved to %s" % PROJECT_FILE)
