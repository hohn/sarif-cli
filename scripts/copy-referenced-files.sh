# 
# This is an example illustrating the steps to copy only files referenced from the
# sarif results into the data/ subdirectory.
#
# This is for the treeio project, adjust as needed for others.
# 

# Get information from the versionControlProvenance field, then start from
# sarif-cli/

# Clone the repository
pushd ~/tmp/
git clone https://github.com/treeio/treeio.git
git checkout bae3115f4015aad2cbc5ab45572232ceec990495 
popd

# Collect file names from error log and copy them
sarif-results-summary \
    -r -s no-real-dir \
    data/treeio/results.sarif 2>&1 |\
    grep "Missing file" | sort -u | awk '{print($4);}' |\
    sed 's|no-real-dir/||g;' | \
    (cd ~/tmp/treeio ; tar -cf - -T -) | \
    (mkdir -p data/treeio/treeio && cd data/treeio/treeio && tar xf -)

# Check:
sarif-results-summary \
    -r -s data/treeio/treeio data/treeio/results.sarif 2>&1 | \
    grep "Missing file"

# Test result view; look for REFERENCE and PATH
sarif-results-summary \
    -s data/treeio/treeio \
    -r data/treeio/results.sarif | less 2>&1

# Some interesting results
sarif-results-summary \
    -s data/treeio/treeio \
    -r data/treeio/results.sarif | \
    sed -n "/editor_plugin_src.js:722:72:722:73/,/RESULT/p" |less

sarif-results-summary \
    -s data/treeio/treeio \
    -r data/treeio/results.sarif | \
    sed -n "/modal-form.html:89:35:93:14/,/RESULT/p" |less

# Clean up: remove clone, if desired
rm -fR ~/tmp/treeio
