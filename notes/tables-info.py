#
# Simple utilities to retrieve and view Github API information
#
import urllib3
import os
import sys
import json
from pprint import pprint
from contextlib import redirect_stdout

#* Init
header_auth = {'Authorization': 'token %s' % os.environ['GITHUB_TOKEN']}

http = urllib3.PoolManager()

owner = 'hohn'
repo = 'tabu-soda'
header_accept = {'Accept' : 'application/vnd.github.v3+json'}
GET = 'GET'

#* Local utility functions using lexical variables
def gith(verb, path, headers={}):
    res = http.request(
        verb,
        'https://api.github.com' + path,
        headers={**header_auth, **header_accept, **headers}
        )
    return res

def topy(result):
    return json.loads(result.data.decode('utf-8'))

def pathval(result, *path):
    v = topy(result)
    for p in path:
        v = v[p]
    print(f'path: {path}  value: {v}')
    return (path, v)


#* GET /repos/{owner}/{repo}/events
r01 = gith(GET, f'/repos/{owner}/{repo}/events')
pathval(r01, 0, 'repo', 'name')
pathval(r01, 0, 'repo', 'url')

#* GET /repos/{owner}/{repo}/code-scanning/analyses
r02 = gith(GET, f'/repos/{owner}/{repo}/code-scanning/analyses')
topy(r02)
# ?   'sarif_id': '9df9fbb4-bf4b-11ec-9ca6-b32c61360f89',

#** GET /repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}, overview only:
_, analysis_id = pathval(r02, 0, 'id')
r02s01 = gith(GET, f'/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}')
topy(r02s01)
pathval(r02s01, 'commit_sha')
pathval(r02s01, 'created_at')
pathval(r02s01, 'results_count')
pathval(r02s01, 'rules_count')
pathval(r02s01, 'sarif_id')
pathval(r02s01, 'tool', 'name')
pathval(r02s01, 'tool', 'version')

#** GET /repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}, full sarif:
r02s02 = gith(GET, f'/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}',
              headers = {'Accept': 'application/sarif+json'})

pprint(topy(r02s02), open("r02s02", "w", encoding='utf-8'))
json.dump(topy(r02s02), open("r02s02.json", "w", encoding='utf-8'), indent=4)

#* GET /repos/{owner}/{repo}
r03 = gith(GET, f'/repos/{owner}/{repo}')
topy(r03)
pathval(r03, 'created_at')
pathval(r03, 'full_name')
pathval(r03, 'git_url')
pathval(r03, 'clone_url')
pathval(r03, 'language')

#* POST /repos/{owner}/{repo}/code-scanning/sarifs
# TODO: to be tested...
r04 = gith(POST, f'/repos/{owner}/{repo}/code-scanning/sarifs',
           fields={'commit_sha': 'aa22233',
                   'ref': 'refs/heads/<branch name>',
                   'sarif': 'gzip < sarif | base64 -w0',
                   'tool_name' : 'codeql',
                   'started_at': 'when the analysis started',
                   },
           headers = {'Accept': 'application/sarif+json'})

