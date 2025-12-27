# Adding Chronoverse to GitHub

Follow these steps to add your project to GitHub:

## Step 1: Initialize Git Repository

Open Terminal and run:

```bash
cd /Users/aschick/Documents/chronoverse

# Initialize git repository
git init

# Add all files (respecting .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Chronoverse timeline web application"
```

## Step 2: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name**: `chronoverse` (or your preferred name)
   - **Description**: "Universal timeline web application for Earth history, world events, and space history"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 3: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Run these in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/chronoverse.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

If you're using SSH instead of HTTPS:

```bash
git remote add origin git@github.com:YOUR_USERNAME/chronoverse.git
git branch -M main
git push -u origin main
```

## Step 4: Verify

Visit your repository on GitHub - you should see all your files!

## What Gets Committed

The `.gitignore` file ensures these are **NOT** committed:
- `venv/` - Virtual environment (users should create their own)
- `__pycache__/` - Python cache files
- `.DS_Store` - macOS system files
- `*.pyc` - Compiled Python files
- Other temporary/system files

These **WILL** be committed:
- All source code (`app/`, `templates/`, `static/`)
- Configuration files (`config.py`, `run.py`)
- Data file (`timeline_data_4.csv`)
- Documentation (`README.md`, etc.)
- Requirements (`requirements.txt`)
- `.gitignore`

## Future Updates

When you make changes:

```bash
# See what changed
git status

# Add specific files
git add path/to/file

# Or add all changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Troubleshooting

### "Repository not found" error
- Check that the repository name and your username are correct
- Make sure you've created the repository on GitHub first

### Authentication issues
- For HTTPS: GitHub may prompt for username/password or personal access token
- For SSH: Make sure your SSH key is set up in GitHub settings

### "Permission denied" error
- Make sure you have write access to the repository
- Check that you're using the correct remote URL

