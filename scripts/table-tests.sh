# -*- sh -*-
#
# Sanity tests for the table-producing scripts.  Should succeed and produce
# nothing on stdout/stderr
# 
( cd ../data/treeio/2021-12-09 && sarif-extract-tables results.sarif test-tables )
( cd ../data/treeio/2022-02-25 && sarif-extract-tables results.sarif test-tables )

( cd ../data/treeio && sarif-extract-multi multi-sarif-01.json test-multi-table )
( cd ../data/treeio && sarif-extract-scans scan-spec-0.json test-scan )

# Simple run
( cd ../data/treeio/ &&
      sarif-extract-scans-runner - > /dev/null <<EOF
2021-12-09/results.sarif
2022-02-25/results.sarif
EOF
)

# Repeated run with state
( cd ../data/treeio/ &&
      sarif-extract-scans-runner -i1 -s successful-runs - <<EOF
2021-12-09/results.sarif
2022-02-25/results.sarif
EOF
  sarif-extract-scans-runner -i1 -s successful-runs - <<EOF
2021-12-09/results.sarif
2022-02-25/results.sarif
EOF
)

# Aggregate multiple results
( cd ../data/treeio/
  cat > test-sas-files <<EOF
2021-12-09/results.sarif
2022-02-25/results.sarif
EOF
      
  sarif-extract-scans-runner test-sas-files
  sarif-aggregate-scans -i1 test-sas-files aggregated.scantables 
  sarif-pad-aggregate aggregated.scantables aggregated.scantables.padded
)
