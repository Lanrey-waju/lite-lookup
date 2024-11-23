#!/bin/bash

CHANGELOG_FILE="CHANGELOG.md"
START_VERSION="0.1.0"

# Increment version function
increment_version() {
  local current_version=$1
  local version_type=$2
  local major minor patch
  IFS='.' read -r major minor patch <<<"$current_version"

  case $version_type in
    "minor")
      minor=$((minor + 1))
      patch=0
      ;;
    "patch")
      patch=$((patch + 1))
      ;;
  esac

  echo "$major.$minor.$patch"
}

# Get the current version from the changelog or start fresh
if [ -f "$CHANGELOG_FILE" ]; then
  LAST_VERSION=$(grep -E '^### Release' "$CHANGELOG_FILE" | head -1 | awk '{print $3}')
else
  LAST_VERSION=$START_VERSION
fi

CURRENT_VERSION=$LAST_VERSION
VERSION_LOG=""

CHANGE_KEYS=() # Array for keys (version,category)
CHANGE_VALUES=() # Array for corresponding values

# Helper function to append changes
append_change() {
  local key=$1
  local value=$2

  for i in "${!CHANGE_KEYS[@]}"; do
    if [[ "${CHANGE_KEYS[i]}" == "$key" ]]; then
      CHANGE_VALUES[i]+="$value\n"
      return
    fi
  done

  # If key doesn't exist, create a new entry
  CHANGE_KEYS+=("$key")
  CHANGE_VALUES+=("$value\n")
}

# Loop through git commits in reverse chronological order
while IFS= read -r line; do
  if [[ $line =~ ^(Add|Added) ]]; then
    CURRENT_VERSION=$(increment_version "$CURRENT_VERSION" "minor")
    append_change "$CURRENT_VERSION,Features" "- ${line}"
  elif [[ $line =~ ^(fix|fixed|Fix|Fixed) ]]; then
    CURRENT_VERSION=$(increment_version "$CURRENT_VERSION" "patch")
    append_change "$CURRENT_VERSION,Fixes" "- ${line}"
  else
    append_change "$CURRENT_VERSION,Other" "- ${line}"
  fi
done < <(git log --pretty=format:"%s (%ad)" --date=short --reverse)

# Build the changelog content
{
  echo "## Generated Changelog - $(date +%Y-%m-%d)"
  for i in "${!CHANGE_KEYS[@]}"; do
    key="${CHANGE_KEYS[i]}"
    version="${key%,*}"       # Extract version
    category="${key#*,}"      # Extract category

    if [ "$VERSION_LOG" != "$version" ]; then
      echo -e "\n### Release $version"
      VERSION_LOG="$version"
    fi

    echo -e "**$category:**\n${CHANGE_VALUES[i]}"
  done
  echo "" # Ensure there's a newline at the end.
} >> "$CHANGELOG_FILE"

# Set the version in the VERSION file and update __init__.py and setup.py
export version="$CURRENT_VERSION"
echo "$version" > "VERSION"
echo "VERSION = \"$version\"" > "litelookup/__init__.py"
awk -v ver="$version" 'NR==3 {$0="version = \"" ver "\""} 1' setup.py > temp.py && mv temp.py setup.py

echo "CHANGELOG.md and version files updated."