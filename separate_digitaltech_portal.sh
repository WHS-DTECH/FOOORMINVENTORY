#!/bin/bash
# Script to move digitaltech_portal out of FOOORMINVENTORY and make it a standalone project

set -e

# Absolute paths
SRC_DIR="$(dirname "$0")/digitaltech_portal"
DEST_PARENT="$(dirname "$0")/../digitaltech_portal"

if [ ! -d "$SRC_DIR" ]; then
  echo "digitaltech_portal directory not found in FOOORMINVENTORY. Aborting."
  exit 1
fi

if [ -d "$DEST_PARENT" ]; then
  echo "Target digitaltech_portal already exists at $DEST_PARENT. Aborting to avoid overwrite."
  exit 1
fi

# Move the folder
mv "$SRC_DIR" "$DEST_PARENT"

# Optional: print next steps
cat <<EOM

digitaltech_portal has been moved to:
  $DEST_PARENT

You can now open digitaltech_portal as its own workspace in VS Code.
If you want to remove the old FOOORMINVENTORY folder, do so manually after verifying everything works.
EOM
