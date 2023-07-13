#!/bin/bash -x
# 
# The automationDetails.id entry is produced by CodeQL when using the
# =--sarif-category= flag.
#
# This is a simple end-to-end test to ensure it appears after CSV conversion.
# Run via
#     ./test-vcp.sh > test-vcp.out 2>&1
#
# An output sample -- not suitable for automatic testing yet -- is in test-vcp.sample

#* Two databases, one with and one without
#        --sarif-category mast-issue 
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection
ls -la sqlidb-0.sarif sqlidb-1.sarif
grep -A2 automationDetails sqlidb-0.sarif sqlidb-1.sarif

source ~/local/sarif-cli/.venv/bin/activate

function get-csv() {
    #* Insert versionControlProvenance
    sarif-insert-vcp $1.sarif > $1.1.sarif

    #* Get CSV.
    cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
    sarif-extract-scans-runner --input-signature CLI - > /dev/null <<EOF
$1.1.sarif
EOF
    #* List CSV messages
    cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
    head -4 $1.1.sarif.csv 

    #* List CSV output
    ls -la $1.1*
    find $1.1.sarif.scantables -print
}

cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
get-csv sqlidb-0
get-csv sqlidb-1

function check-flag() {
    #* Look for the flag value
    ag -C1 mast-issue ${1}
    #* Look for the flag label
    ag -C1 automationDetails ${1}
}

#* Flag should be absent.  csv has undefined value.
check-flag 'sqlidb-0*'
#* Flag should be present 
check-flag 'sqlidb-1.1*'
