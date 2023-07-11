#
#* Following are the steps needed to build a codeql db and various SARIF analyses.
# 
echo '$0: Interactive use only'
exit 1

#* Where are we?
codeql --version 

#* Get repo 
git clone git@github.com:hohn/codeql-dataflow-sql-injection.git
cd codeql-dataflow-sql-injection/

#* Build vanilla DB
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection
rm -fR sqlidb
codeql database create --language=cpp -s . -j 8 -v sqlidb --command='./build.sh'
ls sqlidb


#* Pack compatibility with CLI
#  Note workaround to avoid using --additional-packs
function codeql-complib() {
    if [ -z "$1" ]; then
        echo "Usage: codeql-complib <language>"
        return 1
    fi
    curl --silent https://raw.githubusercontent.com/github/codeql/codeql-cli/v$(codeql version --format=json | jq -r .version)/$1/ql/lib/qlpack.yml | grep version | cut -d':' -f2 | sed 's/^[ ]*//' 
}

: '
0:$ codeql-complib cpp
0.4.6

Put the version into the qlpack:
...
dependencies:
    codeql/cpp-all: ^0.4.6
...

Then
    codeql pack install
followed by
    codeql database analyze 
without 
       --additional-packs $HOME/local/codeql-v2.11.6/   \


Or create the qlpack file using commands:
    codeql pack init foo
    codeql pack add --dir=foo codeql/cpp-all@"$(codeql-complib cpp)"

'

#* Install packs
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection
rm -f *lock*
codeql pack install

#* Run the analyze command's plain version
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection

# Note workaround for using --additional-packs
if false
then
   source ../scripts/grab.sh
   grab v2.11.6 osx64 $HOME/local

   codeql database analyze                                 \
          -v                                               \
          --ram=14000                                      \
          -j12                                             \
          --rerun                                          \
          --format=sarif-latest                            \
          --additional-packs $HOME/local/codeql-v2.11.6/   \
          --output sqlidb-0.sarif                          \
          --                                               \
          sqlidb                                           \
          SqlInjection.ql
fi

codeql database analyze                                 \
       -v                                               \
       --ram=14000                                      \
       -j12                                             \
       --rerun                                          \
       --format=sarif-latest                            \
       --output sqlidb-0.sarif                          \
       --                                               \
       sqlidb                                           \
       SqlInjection.ql

# This field should not be there:
grep automationDetails sqlidb-0.sarif

#* Run the analyze command with options
#  but don't rerun the analysis.  We just want another SARIF file.
#  
cd ~/local/sarif-cli/data/codeql-dataflow-sql-injection

codeql database analyze                         \
       -v                                       \
       --sarif-category mast-issue \
       --ram=14000                              \
       -j12                                     \
       --format=sarif-latest                    \
       --output sqlidb-1.sarif                  \
       --                                       \
       sqlidb                                   \
       SqlInjection.ql

# Now it's present:
grep -A2 automationDetails sqlidb-1.sarif

: '
    "automationDetails" : {
      "id" : "mast-issue/"
    },
'

