#!/bin/bash

# Exit on error
set -e

# Determine bump type (major/minor/patch)
BUMP_TYPE=${1:-patch}

# Bump version using poetry
poetry version $BUMP_TYPE
NEW_VERSION=$(poetry version -s)
echo "Version bumped to: $NEW_VERSION"

# Commit version change
git add pyproject.toml
git commit -m "Bump version to ${NEW_VERSION}"

# Push the version bump
git push

# For minor or major bumps, ask about release
if [[ "$BUMP_TYPE" == "major" ]]; then
    read -p "Create release for v${NEW_VERSION}? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./scripts/release.sh
    fi
fi