# 🚀 CalmNest Deployment Guide

Complete guide to deploy CalmNest with Ollama chatbot (2GB model included).

---

## 📋 Prerequisites

- Git repository with your code
- 2GB+ model (llama3.2:3b)
- Minimum 4GB RAM recommended
- 10GB+ storage for model

---

## 🎯 Deployment Options

### **Option 1: Railway.app (Easiest with Docker)**

**Pros:**
- Easy Docker deployment
- Good for Ollama models
- Free tier available ($5 credit)
- Auto-scaling

**Steps:**

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # Push your code to GitHub first
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

3. **Create New Project on Railway**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Dockerfile

4. **Set Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_API_KEY=optional
   OPENAI_API_KEY=optional
   ```

5. **Deploy**
   - Railway will build and deploy automatically
   - First deployment takes 10-15 minutes (downloading model)

**Cost:** ~$10-20/month for 4GB RAM

---

### **Option 2: Render.com (Docker Support)**

**Pros:**
- Free tier available
- Persistent disk for models
- Easy setup

**Steps:**

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select "Docker" as environment

3. **Configure Service**
   - Name: `calmnest`
   - Plan: Standard (minimum for Ollama)
   - Add Disk: 10GB for models

4. **Set Environment Variables**
   ```
   SECRET_KEY=your-secret-key
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build (15-20 minutes first time)

**Cost:** $7/month (Standard plan)

---

### **Option 3: VPS (DigitalOcean, Linode, AWS EC2)**

**Pros:**
- Full control
- Best performance
- Cost-effective for long-term

**Recommended Specs:**
- 4GB RAM minimum
- 2 CPU cores
- 25GB SSD storage
- Ubuntu 22.04 LTS

**Steps:**

1. **Create VPS**
   - DigitalOcean: Create Droplet (4GB RAM)
   - Linode: Create Linode (4GB RAM)
   - AWS EC2: t3.medium instance

2. **SSH into Server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Run Deployment Script**
   ```bash
   # Upload your code
   git clone <your-repo-url>
   cd calmnest
   
   # Make script executable
   chmod +x deploy_vps.sh
   
   # Run deployment
   ./deploy_vps.sh
   ```

4. **Configure Domain (Optional)**
   - Point your domain to server IP
   - Update Nginx config with your domain
   - Install SSL with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

**Cost:** $12-24/month (DigitalOcean 4GB droplet)

---

### **Option 4: Hugging Face Spaces (Alternative)**

**Note:** Hugging Face Spaces doesn't support Ollama directly, but you can use their hosted models.

**Steps:**

1. Modify `app.py` to use Hugging Face Inference API instead of Ollama
2. Create Space on [huggingface.co/spaces](https://huggingface.co/spaces)
3. Upload code
4. Free tier available!

---

## 🔧 Production Configuration

### Update `app.py` for Production

```python
# Add at the end of app.py
if __name__ == '__main__':
    # Production mode
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Create `.env` file

```env
SECRET_KEY=your-super-secret-key-change-this
GOOGLE_API_KEY=optional-google-api-key
OPENAI_API_KEY=optional-openai-api-key
```

---

## 📊 Resource Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| CPU | 1 core | 2+ cores |
| Storage | 10GB | 25GB+ |
| Bandwidth | 1TB/month | Unlimited |

---

## 🧪 Testing Deployment

After deployment, test these endpoints:

1. **Health Check**
   ```
   GET https://your-app.com/health
   ```

2. **Chatbot**
   ```
   POST https://your-app.com/chat-stream
   Body: {"message": "Hello"}
   ```

3. **Main App**
   ```
   GET https://your-app.com/
   ```

---

## 🐛 Troubleshooting

### Ollama Not Starting
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

### Model Not Loading
```bash
# Pull model manually
ollama pull llama3.2:3b

# Check available models
ollama list
```

### Out of Memory
- Upgrade to 4GB+ RAM
- Use smaller model: `llama3.2:1b`
- Enable swap memory

### Slow Response
- Use faster model
- Increase CPU cores
- Enable caching

---

## 💰 Cost Comparison

| Platform | Monthly Cost | Setup Time | Difficulty |
|----------|-------------|------------|------------|
| Railway | $10-20 | 10 min | Easy |
| Render | $7+ | 15 min | Easy |
| DigitalOcean | $12-24 | 30 min | Medium |
| AWS EC2 | $15-30 | 45 min | Hard |
| Hugging Face | Free | 20 min | Medium |

---

## 🎯 Recommended Choice

**For Beginners:** Railway.app or Render.com
**For Budget:** VPS (DigitalOcean)
**For Free:** Hugging Face Spaces (with API modification)
**For Production:** VPS with proper monitoring

---

## 📞 Support

If you face issues:
1. Check logs: `sudo journalctl -u calmnest -f`
2. Verify Ollama: `curl http://localhost:11434/api/tags`
3. Test model: `ollama run llama3.2:3b "Hello"`

---

## ✅ Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] Chatbot responds correctly
- [ ] Emotion detection works
- [ ] PHQ-9/GAD-7 assessments work
- [ ] Breathing exercises load
- [ ] Dashboard saves data
- [ ] SSL certificate installed (if using domain)
- [ ] Monitoring setup
- [ ] Backups configured

---

**Happy Deploying! 🚀**
