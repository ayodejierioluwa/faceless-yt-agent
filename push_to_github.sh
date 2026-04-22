#!/bin/bash
# 🚀 YouTube Bot GitHub Pusher

echo "--- 🤖 YouTube Bot: Automating your Push ---"

# 1. Initialize Git if needed
if [ ! -d ".git" ]; then
    echo "Initializing local repository..."
    git init
fi

# 2. Prepare files
echo "Staging files..."
git add .

# 3. Create commit
echo "Committing changes..."
git commit -m "Automated Migration to Google AI & GitHub Actions"

# 4. Set branch
git branch -M main

# 5. Handle Remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
    echo "-------------------------------------------------------"
    read -p "Paste your GitHub Repo URL (e.g. https://github.com/user/repo.git): " REPO_URL
    git remote add origin "$REPO_URL"
    echo "Remote 'origin' added."
else
    echo "Remote already exists: $REMOTE_URL"
fi

# 6. Push
echo "Pushing to GitHub..."
git push -u origin main

echo "--- ✅ Done! Check your GitHub Actions tab! ---"
