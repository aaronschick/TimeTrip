# Deploying TimeTrip to Render (Free Hosting)

This guide will help you deploy your TimeTrip Flask application to Render for free.

## Why Render?

- **Free tier available**: 750 hours/month free (enough for 24/7 hosting)
- **Easy deployment**: Connects directly to GitHub
- **Automatic deployments**: Updates when you push to GitHub
- **HTTPS included**: Free SSL certificate
- **No credit card required** for free tier

## Prerequisites

1. A GitHub account (you already have this!)
2. A Render account (sign up at https://render.com - it's free)

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

Make sure all your files are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2. Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended for easy integration)

### 3. Create a New Web Service

1. In your Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub account if you haven't already
4. Select the `TimeTrip` repository
5. Configure the service:
   - **Name**: `timetrip` (or any name you prefer)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT`
   - **Environment**: `Python 3`
   - **Python Version**: `3.11` (important: must be 3.11, not 3.13, due to pandas compatibility)
   
   **Note**: The `runtime.txt` file in the repository specifies Python 3.11.9. Render should automatically detect this, but you can also manually set it to Python 3.11 in the dashboard.

### 4. Create PostgreSQL Database

1. In your Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name**: `timetrip-db` (or any name)
   - **Database**: `timetrip`
   - **Region**: Same as your web service (recommended)
4. Click "Create Database"
5. **Copy the connection string** (Internal Database URL)

### 5. Link Database to Web Service

1. Go to your web service settings
2. Under "Environment", add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the connection string from Step 4
   - **Note**: If the URL starts with `postgres://`, Render will automatically convert it
3. Save changes

### 6. Environment Variables

Set these in your web service settings:
- `DATABASE_URL`: PostgreSQL connection string (from Step 4)
- `FLASK_ENV`: Set to `production` for production mode
- `SECRET_KEY`: Generate a random secret key (optional but recommended)

### 7. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Wait for the build to complete (usually 2-5 minutes)
4. Your app will be live at: `https://timetrip.onrender.com` (or your custom name)

### 8. Initialize Database

After the first deployment:

1. The database tables will be created automatically
2. To import your CSV data:
   - Option A: Use the web interface "Add Event" button
   - Option B: If you have shell access, run:
     ```bash
     python init_db.py --csv timeline_data_4.csv
     ```
   - Option C: Add events manually through the web interface

**Note**: On Render's free tier, you may not have shell access. In that case, use the web interface to add events.

## Custom Domain (Optional)

If you want a custom domain:
1. Go to your service settings in Render
2. Click "Custom Domains"
3. Add your domain
4. Follow the DNS configuration instructions

## Automatic Deployments

Render automatically deploys when you push to your main branch. You can also:
- Manually trigger deployments from the dashboard
- Set up preview deployments for pull requests

## Free Tier Limitations

- **Sleep after inactivity**: Free services sleep after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up.
- **750 hours/month**: Enough for 24/7 hosting
- **512 MB RAM**: Should be sufficient for this app
- **No persistent storage**: Your CSV file is included in the repo, so this is fine

## Troubleshooting

### Build Fails

- Check the build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- **Python Version Issue**: If you see pandas compilation errors, ensure Python 3.11 is selected (not 3.13). The `runtime.txt` file should handle this automatically, but you can manually set it in Render dashboard under "Settings" → "Python Version"
- Verify Python version compatibility

### App Crashes

- Check the logs in Render dashboard
- Verify the data file path is correct
- Ensure `gunicorn` is in requirements.txt

### Slow First Load

- This is normal on free tier (cold start)
- Consider upgrading to paid tier for faster response times

## Alternative Free Hosting Options

If Render doesn't work for you, here are other free options:

### Railway
- Similar to Render
- Free tier with $5 credit/month
- Visit: https://railway.app

### Fly.io
- Good for small apps
- Free tier available
- Visit: https://fly.io

### PythonAnywhere
- Specifically for Python apps
- Free tier available
- Visit: https://www.pythonanywhere.com

## Updating Your App

Simply push changes to GitHub:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the changes and redeploy your app!

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com

