#!/bin/bash

# Simple deployment script for Poetry Video Generator
echo "🚀 Deploying Poetry Video Generator..."

# Copy production environment file
cp production.env .env
echo "✅ Environment file configured"

# Make deployment script executable
chmod +x deploy_ec2.sh

# Run the deployment
./deploy_ec2.sh 