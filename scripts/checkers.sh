#!/bin/bash
#
# A collection of commands to run static python checkers.  For ad-hoc use, may be
# added to ci/cd at some point.
#
cd ../ && . .venv/bin/activate && pyflakes bin/ sarif_cli/
