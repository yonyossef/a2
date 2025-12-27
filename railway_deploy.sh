#!/bin/bash
# Helper script to deploy to Railway
# Make sure you're logged in: railway login

echo "🚂 Deploying to Railway..."
echo ""

# Check if logged in
if ! railway whoami &>/dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Run: railway login"
    exit 1
fi

echo "✅ Logged in to Railway"
echo ""

# Check if project is initialized
if [ ! -f "railway.json" ] && [ ! -f ".railway/config.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init
    echo ""
fi

echo "📤 Deploying..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Useful commands:"
echo "  railway logs          - View logs"
echo "  railway open          - Open dashboard"
echo "  railway variables     - Manage environment variables"
echo "  railway status        - Check deployment status"

