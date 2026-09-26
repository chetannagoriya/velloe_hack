# CalmNest Ollama Troubleshooting Guide

## Common Errors & Solutions

### 1. ❌ "Read timed out" Error

**Problem**: Ollama response generate karne mein bahut time le raha hai (30+ seconds)

**Solutions**:

#### A. Use Smaller Model (RECOMMENDED)
```bash
# Fast, lightweight model (1.3 GB)
ollama pull llama3.2:1b

# Medium model (2 GB)
ollama pull llama3.2:3b
```

Then change in `app.py`:
```python
MODEL_NAME = "llama3.2:1b"  # Instead of "llama3:8b"
```

#### B. Increase Timeout (Already Done)
- Timeout increased to 120 seconds
- Response length reduced to 100 tokens
- Context window reduced to 1024

#### C. Check System Resources
```bash
# Check if Ollama is using too much RAM/CPU
# Windows Task Manager: Ctrl+Shift+Esc
# Look for "ollama" process
```

**Minimum Requirements**:
- llama3:8b → 8 GB RAM
- llama3.2:3b → 4 GB RAM  
- llama3.2:1b → 2 GB RAM

---

### 2. ❌ "Ollama is not running"

**Problem**: Ollama server start nahi hua hai

**Solution**:
```bash
# Terminal mein run karein
ollama serve
```

Keep this terminal open while using the chatbot.

---

### 3. ❌ "Model not found"

**Problem**: Model download nahi hua hai

**Solution**:
```bash
# Check available models
ollama list

# Download required model
ollama pull llama3:8b
# OR
ollama pull llama3.2:1b  # Faster option
```

---

### 4. 🐌 Very Slow Responses

**Reasons**:
1. **First request**: Model load ho raha hai (1-2 minutes wait karein)
2. **CPU-only**: GPU nahi hai toh slow hoga
3. **Background apps**: Close unnecessary programs
4. **Large model**: llama3:8b heavy hai

**Solutions**:

#### Quick Fixes:
1. **Use smaller model**: `llama3.2:1b` (10x faster)
2. **Shorter messages**: Chhote questions puchein
3. **Clear chat history**: "Clear" button click karein
4. **Close other apps**: RAM free karein

#### Model Comparison:

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| llama3.2:1b | 1.3 GB | 2 GB | ⚡⚡⚡ Fast | ⭐⭐ Good |
| llama3.2:3b | 2 GB | 4 GB | ⚡⚡ Medium | ⭐⭐⭐ Better |
| llama3:8b | 4.7 GB | 8 GB | ⚡ Slow | ⭐⭐⭐⭐ Best |

---

### 5. ❌ Port 11434 Already in Use

**Problem**: Ollama already running hai ya port blocked hai

**Solution**:
```bash
# Windows
netstat -ano | findstr :11434
taskkill /PID <PID_NUMBER> /F

# Then restart
ollama serve
```

---

### 6. 💾 Disk Space Issues

**Problem**: Model download nahi ho raha

**Check Space**:
- llama3:8b → 4.7 GB
- llama3.2:3b → 2 GB
- llama3.2:1b → 1.3 GB

**Solution**: Free up disk space or use smaller model

---

## Performance Tips

### For Best Experience:

1. **Use llama3.2:1b** for fast responses
2. **Keep messages short** (1-2 sentences)
3. **Clear chat history** regularly
4. **Close background apps** to free RAM
5. **First response slow hai** - wait karo, next responses fast honge

### System Requirements:

**Minimum** (llama3.2:1b):
- 2 GB RAM
- 2 GB disk space
- Any modern CPU

**Recommended** (llama3:8b):
- 8 GB RAM
- 5 GB disk space
- Multi-core CPU or GPU

---

## Testing Commands

### Check if Ollama is Running:
```bash
curl http://localhost:11434/api/tags
```

### Test Model:
```bash
ollama run llama3:8b "Hello, how are you?"
```

### Check System Resources:
```bash
# Windows
tasklist | findstr ollama

# Check RAM usage in Task Manager
```

---

## Quick Start (Recommended Setup)

```bash
# 1. Install Ollama (one time)
# Download from: https://ollama.ai/download

# 2. Download FAST model (recommended)
ollama pull llama3.2:1b

# 3. Start Ollama
ollama serve

# 4. Update app.py
# Change: MODEL_NAME = "llama3.2:1b"

# 5. Start Flask
python app.py

# 6. Test
# Open: http://localhost:5000/ollama-test
```

---

## Still Having Issues?

### Debug Steps:

1. **Check Ollama logs**:
   - Look at terminal where `ollama serve` is running
   - Any error messages?

2. **Test directly**:
   ```bash
   ollama run llama3.2:1b "test message"
   ```

3. **Check Flask logs**:
   - Look at terminal where `python app.py` is running
   - Any Python errors?

4. **Browser console**:
   - Press F12 in browser
   - Check Console tab for JavaScript errors

5. **Try test page**:
   - Go to: http://localhost:5000/ollama-test
   - Check connection status

---

## Contact & Support

If still facing issues:
1. Check Ollama documentation: https://ollama.ai/docs
2. Verify system meets minimum requirements
3. Try smaller model first (llama3.2:1b)
4. Restart both Ollama and Flask app
