#
#* Following are the steps needed to build a codeql db using different versions of
# the codeql cli
# 
echo '$0: Interactive use only'
exit 1

#* Use virtual environment.  See README for setup.
source ~/local/sarif-cli/.venv/bin/activate

#* What can we use?
gh codeql list-versions

#* History
open https://github.com/github/codeql-cli-binaries/blob/HEAD/CHANGELOG.md

#* Get repo 
cd ~/local/sarif-cli
git clone git@github.com:hohn/codeql-dataflow-sql-injection.git
cd codeql-dataflow-sql-injection/

#* Choose
v2.14.0
v2.13.5
v2.13.4
v2.13.3
v2.13.1
v2.13.0
v2.12.7
v2.12.6
v2.11.6
v2.10.5
v2.9.4

CLI_VERSION=v2.9.4
CLI_VERSION=v2.12.7
gh codeql set-version $CLI_VERSION

#* Build vanilla DB
cd ~/local/sarif-cli/codeql-dataflow-sql-injection
rm -fR sqlidb
codeql database create --language=cpp -s . -j 8 -v sqlidb --command='./build.sh'
cp -r sqlidb sqlidb-$CLI_VERSION

#* Pack compatibility with CLI
function codeql-complib() {
    if [ -z "$1" ]; then
        echo "Usage: codeql-complib <language>"
        return 1
    fi
    curl --silent https://raw.githubusercontent.com/github/codeql/codeql-cli/v$(codeql version --format=json | jq -r .version)/$1/ql/lib/qlpack.yml | grep version | cut -d':' -f2 | sed 's/^[ ]*//' 
}

# Create the qlpack file using commands:
cd ~/local/sarif-cli
#: Bug: drops the codeql- prefix
rm -fR dataflow-sql-injection
codeql pack init codeql-dataflow-sql-injection
cp -f dataflow-sql-injection/qlpack.yml codeql-dataflow-sql-injection/
# Add correct library dependency
codeql pack add --dir=codeql-dataflow-sql-injection codeql/cpp-all@"$(codeql-complib cpp)"

#* Install packs
cd ~/local/sarif-cli/codeql-dataflow-sql-injection
rm -f *lock*
codeql pack install

#* Run the analyze command with options
#  
cd ~/local/sarif-cli/codeql-dataflow-sql-injection
codeql database analyze                         \
       -v                                       \
       --sarif-category santa-chap              \
       --ram=16000                              \
       -j8                                      \
       --format=sarif-latest                    \
       --output sqlidb-$CLI_VERSION.sarif       \
       --                                       \
       sqlidb-$CLI_VERSION                      \
       SqlInjection.ql

# Verify cli version in SARIF output
SAVER=`jq -r '.runs |.[] |.tool.driver.semanticVersion ' sqlidb-$CLI_VERSION.sarif`
if [ v$SAVER != $CLI_VERSION ] ;
then
    echo "---: codeql version inconsistency"
fi

# Check sarif-category flag
grep -A2 automationDetails sqlidb-$CLI_VERSION.sarif

#* Insert versionControlProvenance
cd ~/local/sarif-cli/codeql-dataflow-sql-injection 
sarif-insert-vcp sqlidb-$CLI_VERSION.sarif > sqlidb-$CLI_VERSION-1.sarif

#* Get CSV.
cd ~/local/sarif-cli/codeql-dataflow-sql-injection 
sarif-extract-scans-runner --input-signature CLI - > /dev/null <<EOF
sqlidb-$CLI_VERSION-1.sarif
EOF

#* Check CSV messages for success
cd ~/local/sarif-cli/codeql-dataflow-sql-injection 
# head -4 sqlidb-$CLI_VERSION-1.sarif.csv 
grep -qi success sqlidb-$CLI_VERSION-1.sarif.csv || {
    echo "---: sarif-cli failure: sqlidb-$CLI_VERSION-1.sarif*"
}

#* CSV output
# ls -la sqlidb-$CLI_VERSION-1*
# find sqlidb-$CLI_VERSION-1*.scantables -print
