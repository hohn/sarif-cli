#!/bin/bash
#* Setup 
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection
ls -la sqlidb-0.sarif sqlidb-1.sarif

#
source ~/local/sarif-cli/.venv/bin/activate

#* Utility functions
function get-csv() {
    #* Insert versionControlProvenance
    sarif-insert-vcp $1.sarif > $1.1.sarif

    #* Populate CSV with provided timestamps
    cat > $1.timestamp << EOF
{
    "db_create_start": "2023-07-03T00:56:15.576222",
    "db_create_stop": "2023-07-03T00:56:42.781839",
    "scan_start": "2023-07-03T00:56:47.546696",
    "scan_stop": "2023-07-03T00:57:55.988059"
}
EOF

    sarif-extract-scans-runner --input-signature CLI --with-timestamps - <<EOF
$1.1.sarif,$1.timestamp
EOF

    #* List CSV messages
    cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
    head -4 $1.1.sarif.csv 

    #* List CSV output
    ls -la $1.1*
    find $1.1.sarif.scantables -print
    csvcut -c "db_create_start,db_create_stop,scan_start_date,scan_stop_date" \
           $1.1.sarif.scantables/scans.csv

    # #* show log
    # echo "run log:"
    # cat $1.1.sarif.scanlog
}

function get-csv-no-ts() {
    #* Insert versionControlProvenance
    sarif-insert-vcp $1.sarif > $1.1.sarif

    #* Get CSV with dummy timestamps
    sarif-extract-scans-runner --input-signature CLI - <<EOF
$1.1.sarif
EOF

    #* List CSV messages
    cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
    head -4 $1.1.sarif.csv 

    #* List CSV output
    ls -la $1.1*
    find $1.1.sarif.scantables -print
    csvcut -c "db_create_start,db_create_stop,scan_start_date,scan_stop_date" \
           $1.1.sarif.scantables/scans.csv
}

clean-csv () {
    cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
    rm -f $1.1.sarif.csv 
    rm -f $1.1*scan{log,spec}
    rm -fR $1.1.sarif.scantables 
}    

#* Clean up and run tool
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection 
clean-csv sqlidb-0
get-csv sqlidb-0

clean-csv sqlidb-1
get-csv-no-ts sqlidb-1

#* Look for the timestamp value
function check-timestamp() {
    ag -C1 "00:56:15.57622|1970-01-01" ${1}
}
# With custom stamp:
check-timestamp 'sqlidb-0.1*/scans.csv'
# With default stamp:
check-timestamp 'sqlidb-1.1*/scans.csv'
# 
