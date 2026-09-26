#!/bin/bash
# VPS Deployment Script for CalmNest

echo "🚀 CalmNest VPS Deployment Script"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
echo "▶️ Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull the model
echo "📥 Pulling llama3.2:3b model (this may take a while)..."
ollama pull llama3.2:3b

# Create application directory
echo "📁 Setting up application..."
sudo mkdir -p /var/www/calmnest
cd /var/www/calmnest

# Clone or copy your project here
# git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/calmnest.service > /dev/null <<EOF
[Unit]
Description=CalmNest Flask Application
After=network.target ollama.service

[Service]
User=$USER
WorkingDirectory=/var/www/calmnest
Environment="PATH=/var/www/calmnest/venv/bin"
ExecStart=/var/www/calmnest/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/calmnest > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /chat-stream {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/calmnest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start the application
echo "🎉 Starting CalmNest..."
sudo systemctl enable calmnest
sudo systemctl start calmnest

echo "✅ Deployment complete!"
echo "📊 Check status: sudo systemctl status calmnest"
echo "📝 View logs: sudo journalctl -u calmnest -f"
