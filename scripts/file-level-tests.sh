# -*- sh -*-
# The purpose of this tool set is working with sarif at the shell / file level,
# across multiple versions of the same sarif result set, and across many
# repositories.
#
# These tests mirror that goal: they work on files using the tools and use
# standard unix utilities to verify contents.
# 

sarif-results-summary  -h

#
# Simple failure checks.  These should produce no output.
# 
test_files="
../data/wxWidgets_wxWidgets__2021-11-21_16_06_30__export.sarif
../data/torvalds_linux__2021-10-21_10_07_00__export.sarif
../data/treeio/results.sarif
"
for file in $test_files ; do
    sarif-results-summary $file > /dev/null 
done
for file in $test_files ; do
    sarif-results-summary -r $file > /dev/null 
done
          
#
# The following are for iterating and evolving result inspection to find test
# cases covering the different output options.  They are intended for manual use
# and review.
#
read -r file srcroot <<< "../data/treeio/results.sarif ../data/treeio/treeio"

# All results, minimal output
sarif-results-summary             $file | less

# All results, related locations output
sarif-results-summary -r           $file | less

# All results, related locations and source output
sarif-results-summary -r -s $srcroot $file | less

# single-line result, no flow steps
start="sanitizer.py:8:1:8:16"
sarif-results-summary             $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

# single-line result, with flow steps
start="treeio.core.middleware.chat.py:395:29:395:33"
sarif-results-summary             $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

# single-line result, with flow steps, with relatedLocations
start="treeio.core.middleware.chat.py:395:29:395:33"
sarif-results-summary -r           $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

# single-line result, with flow steps compacted
start="treeio.core.middleware.chat.py:395:29:395:33"
sarif-results-summary -e          $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

# multi-line result, no flow steps, with relatedLocations and source
start=editor_plugin_src.js:722:72:722:73
sarif-results-summary -r -s $srcroot $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

# multi-line result, with flow steps, with relatedLocations and source
start=modal-form.html:89:35:93:14
sarif-results-summary -r -s $srcroot $file | sed -n "/$start/,/RESULT/p" | sed '$d' | less

