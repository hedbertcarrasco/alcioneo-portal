#!/bin/bash

echo "Initializing Git repository for AlcioNEO MVP..."

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AlcioNEO MVP Trading Dashboard"

# Add remote origin
git remote add origin https://github.com/hedbertcarrasco/alceoneo-portal.git

# Set main branch
git branch -M main

echo "Git repository initialized!"
echo ""
echo "Next steps:"
echo "1. Make sure you have push access to: https://github.com/hedbertcarrasco/alceoneo-portal"
echo "2. Push to GitHub: git push -u origin main"
echo "3. Go to Vercel and import the project from GitHub"
echo "4. Set the root directory to 'MVP' in Vercel settings"
echo "5. Add POLYGON_API_KEYS environment variable in Vercel"
echo ""
echo "Done!"