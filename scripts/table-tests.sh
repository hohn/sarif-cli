# -*- sh -*-
#
# Sanity tests for the table-producing scripts.  Should succeed and produce
# nothing on stdout/stderr
# 
( cd ../data/treeio/2021-12-09 && sarif-extract-tables results.sarif test-tables )
( cd ../data/treeio/2022-02-25 && sarif-extract-tables results.sarif test-tables )
( cd ../data/treeio && sarif-extract-multi multi-sarif-01.json test-multi-table )
( cd ../data/treeio && sarif-extract-scans scan-spec-0.json test-scan )
