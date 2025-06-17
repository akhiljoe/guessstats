#!/bin/bash

echo "=== 🚀 Script started ==="

# Configurable variables
REPO="akhiljoe/guessstats"
# SOURCE_BRANCH="office_guessstats"
SOURCE_BRANCH=$(git rev-parse --abbrev-ref HEAD)
TARGET_BRANCH="main"

echo "📌 Detected current branch as '$SOURCE_BRANCH'"

# Step 1: Create the pull request
echo "➡️  Creating pull request from '$SOURCE_BRANCH' to '$TARGET_BRANCH'..."

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d "{\"title\":\"Merge $SOURCE_BRANCH to $TARGET_BRANCH\",\"head\":\"$SOURCE_BRANCH\",\"base\":\"$TARGET_BRANCH\",\"body\":\"Automated PR from $SOURCE_BRANCH branch\"}" \
  https://api.github.com/repos/$REPO/pulls)

HTTP_BODY=$(echo "$RESPONSE" | sed '$d')
HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_STATUS" -ne 201 ]; then
  echo "❌ Failed to create pull request (HTTP $HTTP_STATUS):"
  echo "$HTTP_BODY"
  exit 1
fi

PR_NUMBER=$(echo "$HTTP_BODY" | grep -m 1 '"number":' | sed 's/[^0-9]*//g')

if [ -z "$PR_NUMBER" ]; then
  echo "❌ Could not extract pull request number:"
  echo "$HTTP_BODY"
  exit 1
fi

echo "✅ Pull request #$PR_NUMBER created successfully."

# Step 2: Merge the pull request
echo "➡️  Merging pull request #$PR_NUMBER..."

MERGE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d '{"merge_method":"merge"}' \
  https://api.github.com/repos/$REPO/pulls/$PR_NUMBER/merge)

MERGE_BODY=$(echo "$MERGE_RESPONSE" | sed '$d')
MERGE_STATUS=$(echo "$MERGE_RESPONSE" | tail -n1)

if [ "$MERGE_STATUS" -ne 200 ] && [ "$MERGE_STATUS" -ne 201 ]; then
  echo "❌ Failed to merge pull request (HTTP $MERGE_STATUS):"
  echo "$MERGE_BODY"
  exit 1
fi

echo "✅ Pull request #$PR_NUMBER merged successfully."
echo "=== ✅ Script finished ==="
