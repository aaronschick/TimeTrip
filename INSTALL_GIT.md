# Installing Git on macOS

You need to install Xcode Command Line Tools to use git. Here are your options:

## Option 1: Install via Terminal (Easiest)

1. Open Terminal
2. Run this command:
   ```bash
   xcode-select --install
   ```
3. A dialog will appear asking to install the tools
4. Click **"Install"**
5. Wait for the installation to complete (may take 10-15 minutes)
6. Once done, verify installation:
   ```bash
   git --version
   ```

## Option 2: Install Full Xcode (If Option 1 Doesn't Work)

1. Open the App Store
2. Search for "Xcode"
3. Install Xcode (this is a large download, ~10GB+)
4. After installation, open Xcode once to accept the license
5. Then git will be available

## Option 3: Use GitHub Desktop (GUI Alternative)

If you prefer a graphical interface:

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Use the GUI to:
   - Add your local repository
   - Commit changes
   - Push to GitHub

**Using GitHub Desktop:**
- File → Add Local Repository
- Select `/Users/aschick/Documents/chronoverse`
- Click "Publish repository" to push to GitHub

## Option 4: Install Git via Homebrew (If You Have Homebrew)

If you have Homebrew installed:

```bash
brew install git
```

## After Installation

Once git is installed, you can proceed with the GitHub setup:

```bash
cd /Users/aschick/Documents/chronoverse
git init
git add .
git commit -m "Initial commit: Chronoverse timeline web application"
git remote add origin https://github.com/aaronschick/chronoverse.git
git branch -M main
git push -u origin main
```

## Verify Installation

After installing, verify git works:

```bash
git --version
```

You should see something like: `git version 2.x.x`

## Troubleshooting

### Installation dialog doesn't appear
- Try running: `sudo xcode-select --install`
- Or download from: https://developer.apple.com/download/all/

### "Command line tools are already installed"
- Git should already work! Try `git --version` to verify
- If it still doesn't work, try: `sudo xcode-select --reset`

### Still having issues?
- Check if git is in a different location: `which git`
- You may need to restart Terminal after installation

