# Ollama Integration Setup for CalmNest

## Prerequisites

1. **Install Ollama**
   - Download from: https://ollama.ai/download
   - Or use command line:
     ```bash
     # For Linux/Mac
     curl -fsSL https://ollama.ai/install.sh | sh
     
     # For Windows
     # Download installer from website
     ```

2. **Download llama3:8b model**
   ```bash
   ollama pull llama3:8b
   ```

## Starting Ollama

1. **Start Ollama server**
   ```bash
   ollama serve
   ```
   
   This will start Ollama on `http://localhost:11434`

2. **Verify model is available**
   ```bash
   ollama list
   ```
   
   You should see `llama3:8b` in the list.

## Running CalmNest with Ollama

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Flask application**
   ```bash
   python app.py
   ```

3. **Test Ollama connection**
   - Open browser: `http://localhost:5000/ollama-test`
   - This page will show if Ollama is running and which models are available
   - You can send test messages to verify streaming works

4. **Use the chatbot**
   - Navigate to: `http://localhost:5000/chatbot`
   - The chatbot now uses Ollama's llama3:8b model
   - Responses will stream in real-time

## Endpoints

- `/health` - Check Ollama status and available models
- `/chat-stream` - Streaming chat endpoint (used by chatbot)
- `/chat` - Legacy endpoint (still available for fallback)
- `/ollama-test` - Test page for Ollama connection
- `/chatbot` - Main chatbot interface

## Features

- **Streaming responses**: Messages appear word-by-word as they're generated
- **Chat history**: Last 4 messages are kept in memory for context
- **Mental health focus**: System prompt optimized for supportive conversations
- **Multilingual**: Responds in user's language (Hindi, English, etc.)
- **Crisis detection**: Provides helpline numbers for crisis situations

## Troubleshooting

### "Ollama is not running"
- Make sure you ran `ollama serve` in a terminal
- Check if port 11434 is available
- Try: `curl http://localhost:11434/api/tags`

### "Model not available"
- Run: `ollama pull llama3:8b`
- Wait for download to complete
- Verify with: `ollama list`

### Slow responses
- llama3:8b requires good CPU/GPU
- Reduce `num_predict` in app.py for shorter responses
- Consider using smaller model: `ollama pull llama3.2:1b`

### Connection timeout
- Increase timeout in app.py (currently 30 seconds)
- Check system resources (RAM, CPU usage)

## Configuration

Edit these settings in `app.py`:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama server URL
MODEL_NAME = "llama3:8b"                            # Model to use
MAX_HISTORY = 4                                     # Chat history length

# In payload options:
"num_predict": 200,      # Max response length
"temperature": 0.7,      # Creativity (0.0-1.0)
"num_ctx": 2048,         # Context window size
```

## Alternative Models

You can use different models by changing `MODEL_NAME`:

```python
# Smaller, faster models:
MODEL_NAME = "llama3.2:1b"    # Very fast, less capable
MODEL_NAME = "llama3.2:3b"    # Balanced

# Larger, more capable models:
MODEL_NAME = "llama3:70b"     # Requires powerful hardware
MODEL_NAME = "mistral:7b"     # Alternative option
```

Download with: `ollama pull <model-name>`
