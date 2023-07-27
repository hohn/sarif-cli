# Reference urls:
# https://github.com/github/codeql-cli-binaries/releases/download/v2.8.0/codeql-linux64.zip
# https://github.com/github/codeql/archive/refs/tags/codeql-cli/v2.8.0.zip
#
# grab -- retrieve and extract codeql cli and library
# Usage: grab version url prefix
grab() {
    version=$1; shift
    platform=$1; shift
    prefix=$1; shift
    mkdir -p $prefix/codeql-$version &&
        cd $prefix/codeql-$version || return

    # Get cli
    wget "https://github.com/github/codeql-cli-binaries/releases/download/$version/codeql-$platform.zip"
    # Get lib
    wget "https://github.com/github/codeql/archive/refs/tags/codeql-cli/$version.zip"
    # Fix attributes
    if [ `uname` = Darwin ] ; then
        xattr -c *.zip
    fi
    # Extract
    unzip -q codeql-$platform.zip
    unzip -q $version.zip
    # Rename library directory for VS Code
    mv codeql-codeql-cli-$version/ ql
    # remove archives?
    # rm codeql-$platform.zip
    # rm $version.zip
}

# grab v2.7.6 osx64 $HOME/local
# grab v2.8.3 osx64 $HOME/local
# grab v2.8.4 osx64 $HOME/local

# grab v2.6.3 linux64 /opt

# grab v2.6.3 osx64 $HOME/local
# grab v2.4.6 osx64 $HOME/local
 
