#!/bin/bash

# Ensure we are in the root of the project
cd "$(dirname "$0")/.."

echo "Initializing DVC..."
dvc init

echo "Setting up local remote storage for DVC (to avoid pushing large data to GitHub)..."
mkdir -p .dvc_storage
dvc remote add -d local_storage .dvc_storage

echo "Adding raw and processed data directories to DVC..."
# Note: Ensure these directories exist before adding
if [ -d "data/raw" ]; then
    dvc add data/raw
fi

if [ -d "data/processed" ]; then
    dvc add data/processed
fi

echo "Data versioning setup complete!"
echo "Don't forget to commit the .dvc files to git:"
echo "git add data/raw.dvc data/processed.dvc .gitignore"
