#!/bin/bash

# Poetry Video Generator EC2 Deployment Script
# This script sets up and deploys the Poetry video generation system on EC2

set -e  # Exit on any error

echo "🚀 Starting Poetry Video Generator EC2 Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Create application directory
APP_DIR="/home/$USER/poetry-generator"
print_status "Setting up application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Copy application files (assuming they're in the current directory)
print_status "Copying application files..."
cp -r . $APP_DIR/ 2>/dev/null || {
    print_warning "Could not copy files from current directory. Please ensure all files are in $APP_DIR"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    print_status "Please copy env_template.txt to .env and configure your environment variables:"
    echo "cp env_template.txt .env"
    echo "nano .env  # or use your preferred editor"
    print_status "Required variables to configure:"
    echo "  - AWS_ACCESS_KEY_ID"
    echo "  - AWS_SECRET_ACCESS_KEY"
    echo "  - S3_BUCKET_NAME"
    echo "  - AZURE_OPENAI_ENDPOINT"
    echo "  - AZURE_OPENAI_API_KEY"
    echo "  - AZURE_OPENAI_DEPLOYMENT_NAME"
    echo "  - AZURE_OPENAI_TTS_ENDPOINT"
    echo "  - AZURE_OPENAI_TTS_API_KEY"
    echo "  - PEXELS_API_KEY"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p assets/backgrounds assets/audio assets/fonts audio/tts temp

# Set proper permissions
print_status "Setting proper permissions..."
chmod 755 assets audio temp
chmod 644 .env

# Build and start the application
print_status "Building Docker image..."
docker-compose build

print_status "Starting the application..."
docker-compose up -d

# Wait for the application to start
print_status "Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Application is running successfully!"
    print_status "API is available at: http://localhost:8001"
    print_status "Health check: http://localhost:8001/health"
    print_status "API documentation: http://localhost:8001/docs"
else
    print_error "Application failed to start properly"
    print_status "Checking container logs..."
    docker-compose logs
    exit 1
fi

# Create systemd service for auto-start (optional)
read -p "Do you want to create a systemd service for auto-start? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating systemd service..."
    sudo tee /etc/systemd/system/poetry-generator.service > /dev/null <<EOF
[Unit]
Description=Poetry Video Generator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl enable poetry-generator.service
    print_success "Systemd service created and enabled"
fi

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    read -p "Do you want to configure firewall to allow port 8001? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Configuring firewall..."
        sudo ufw allow 8001/tcp
        sudo ufw reload
        print_success "Firewall configured"
    fi
fi

print_success "🎉 Deployment completed successfully!"
print_status "Application is running at: http://localhost:8001"
print_status "To view logs: docker-compose logs -f"
print_status "To stop: docker-compose down"
print_status "To restart: docker-compose restart"

# Display useful commands
echo
print_status "Useful commands:"
echo "  View logs:          docker-compose logs -f"
echo "  Stop application:   docker-compose down"
echo "  Restart:           docker-compose restart"
echo "  Update:            git pull && docker-compose up -d --build"
echo "  Check status:      docker-compose ps" 