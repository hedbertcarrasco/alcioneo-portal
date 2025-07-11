# Deployment Guide for AlcioNEO MVP

## Deploying to Vercel

### Prerequisites
1. A Vercel account (https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Your Polygon API keys

### Step 1: Prepare the repository
```bash
# Navigate to MVP directory
cd MVP/

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for AlcioNEO MVP"
```

### Step 2: Configure Environment Variables in Vercel

1. Go to your Vercel dashboard
2. Create a new project or select your existing project
3. Go to Settings → Environment Variables
4. Add the following variable:
   - Name: `POLYGON_API_KEYS`
   - Value: `your_first_api_key,your_second_api_key` (comma-separated, no spaces)

### Step 3: Deploy

#### Option A: Deploy via GitHub
1. Push your code to GitHub:
   ```bash
   git remote add origin https://github.com/hedbertcarrasco/alceoneo-portal.git
   git branch -M main
   git push -u origin main
   ```

2. In Vercel dashboard:
   - Import project from GitHub
   - Select your repository
   - Framework Preset: Other
   - Root Directory: `MVP` (important!)
   - Click Deploy

#### Option B: Deploy via CLI
```bash
# From the MVP directory
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set project name
# - Confirm directory
```

### Step 4: Post-deployment

1. Your app will be available at: `https://your-project-name.vercel.app`
2. Monitor logs in Vercel dashboard
3. Set up custom domain if desired

## Important Notes

### API Keys Security
- Never commit `polygon-api.txt` to git (it's in .gitignore)
- Always use environment variables in production
- In Vercel, set API keys as: `key1,key2` (comma-separated)

### Limitations on Vercel
- Serverless functions have a 10s timeout on free plan
- Live mode might need adjustments for serverless environment
- Consider using Vercel KV for caching in production

### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
cd src
python app.py
```

### Troubleshooting

1. **Import errors**: Make sure the root directory is set to `MVP` in Vercel
2. **API key errors**: Check environment variables are set correctly
3. **Timeout errors**: Consider upgrading Vercel plan or optimizing code
4. **Cache issues**: Vercel's filesystem is read-only, consider using Vercel KV

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| POLYGON_API_KEYS | Comma-separated API keys | `key1,key2` |

## Support

For issues specific to deployment, check:
- Vercel documentation: https://vercel.com/docs
- Dash deployment guide: https://dash.plotly.com/deployment