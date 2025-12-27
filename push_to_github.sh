#!/bin/bash
# Helper script to push to GitHub
# Usage: ./push_to_github.sh <github-username> <repo-name>

if [ $# -ne 2 ]; then
    echo "Usage: ./push_to_github.sh <github-username> <repo-name>"
    echo "Example: ./push_to_github.sh yonyossef nvda-stock-agent"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME=$2

echo "Setting up remote repository..."
git remote add origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git 2>/dev/null || git remote set-url origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Your code is now on GitHub:"
echo "https://github.com/${GITHUB_USER}/${REPO_NAME}"

