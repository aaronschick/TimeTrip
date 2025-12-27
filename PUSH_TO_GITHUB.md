# Push Chronoverse to GitHub

Since you already have the repository at https://github.com/aaronschick/chronoverse, follow these steps:

## Step 1: Initialize Git (if not already done)

```bash
cd /Users/aschick/Documents/chronoverse
git init
```

## Step 2: Add All Files

```bash
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Chronoverse timeline web application"
```

## Step 4: Connect to Your GitHub Repository

```bash
# Add the remote repository
git remote add origin https://github.com/aaronschick/chronoverse.git

# If you get "remote origin already exists", use this instead:
# git remote set-url origin https://github.com/aaronschick/chronoverse.git
```

## Step 5: Push to GitHub

```bash
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

If the repository already has content and you want to merge:

```bash
# Pull existing content first
git pull origin main --allow-unrelated-histories

# Resolve any conflicts if they occur, then:
git push -u origin main
```

## Alternative: Force Push (if repository is empty or you want to overwrite)

**⚠️ Only use this if the repository is empty or you want to completely replace its contents:**

```bash
git push -u origin main --force
```

## What Gets Pushed

All these files will be added:
- ✅ All source code (`app/`, `templates/`, `static/`)
- ✅ Configuration files
- ✅ Data file (`timeline_data_4.csv`)
- ✅ Documentation files
- ✅ Requirements (`requirements.txt`)
- ✅ `.gitignore`

These will **NOT** be pushed (excluded by `.gitignore`):
- ❌ `venv/` - Virtual environment
- ❌ `__pycache__/` - Python cache
- ❌ `.DS_Store` - macOS files

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/aaronschick/chronoverse.git
```

### Authentication Required
- GitHub may ask for username and password
- For password, use a **Personal Access Token** (not your GitHub password)
- Create token: GitHub → Settings → Developer settings → Personal access tokens → Generate new token

### "Permission denied"
- Make sure you have write access to the repository
- Check that you're logged into GitHub with the correct account

