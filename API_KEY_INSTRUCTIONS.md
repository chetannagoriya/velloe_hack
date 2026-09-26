# 🔐 API Key Setup Instructions

## ⚠️ IMPORTANT SECURITY WARNING

- **NEVER** commit API keys to version control
- **NEVER** share API keys publicly
- **ALWAYS** use environment variables
- **ROTATE** keys if compromised

## 📋 Step-by-Step Setup

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

### 2. Add Your API Key to .env File
Edit the `.env` file and replace `your_api_key_here`:

```bash
# For Google AI (Gemini)
GOOGLE_API_KEY=AIzaSyDDECTAZyTQZGe7h3Npo4u6sPqJWfrxJkI

# For OpenAI (optional)
OPENAI_API_KEY=your_openai_key_here
```

### 3. How the System Works

#### 🛡️ Safety First
- **Crisis content** ALWAYS uses rule-based responses
- **AI responses** are filtered for safety
- **Fallback** to rule-based if AI fails
- **No medical advice** from AI

#### 🔄 Response Priority
1. **Crisis detection** → Rule-based emergency response
2. **AI response** → If API key available and safe
3. **Rule-based** → Comprehensive fallback system

#### 🎯 AI Configuration
- **Google Gemini**: Primary AI service
- **OpenAI GPT**: Backup service
- **Word limit**: 100 words for safety
- **Temperature**: 0.7 for balanced responses

## 🚀 Usage

### With API Key
- More conversational responses
- Better context understanding
- Still maintains safety boundaries

### Without API Key
- Fully functional rule-based system
- Completely private and secure
- No external dependencies
- Free to use

## 🔒 Security Best Practices

### ✅ DO
- Use environment variables
- Keep .env in .gitignore
- Rotate keys regularly
- Monitor API usage

### ❌ DON'T
- Hardcode keys in code
- Commit .env files
- Share keys publicly
- Use production keys in development

## 🆘 Emergency Resources

The system **always** provides crisis resources regardless of AI configuration:
- **988** - Suicide & Crisis Lifeline (US)
- **Emergency services** - For immediate danger
- **Professional help** - Always recommended

## 📞 Support

If you encounter issues:
1. Check API key is correctly set in .env
2. Verify internet connection
3. Check API key permissions and quota
4. Review logs for error messages

---

**Remember**: The rule-based system provides excellent mental health support without any external APIs. Use AI only if you understand the security implications.
