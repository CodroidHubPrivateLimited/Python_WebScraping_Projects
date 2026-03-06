#!/usr/bin/env bash
set -e

# Render native Python runtime does not allow apt installs during build.
# Keep this script as a safe no-op.
echo "Skipping OS package install on Render native runtime."
