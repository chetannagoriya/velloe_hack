"""
CalmNest – AI Mental Health Web Application

Features:
- Live camera-based emotion detection (face-api.js)
- Real-time Chart.js emotion graph
- PHQ-9 and GAD-7 self-assessments
- Dashboard with localStorage persistence
- Breathing exercise and supportive chatbot

Requirements:
- Python 3.8+
- Flask, OpenCV, NumPy, Pillow
- Browser-based emotion detection using face-api.js
"""

from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
import os
import logging
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Optional external AI imports (only if API keys are provided)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Optional external AI setup
openai_client = None

if OPENAI_API_KEY:
    try:
        import openai  # type: ignore
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logging.info("OpenAI configured successfully")
    except Exception as e:
        logging.warning(f"Failed to configure OpenAI: {e}")

app = Flask(__name__)

# Flask session configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def _get_data_dir(subdir: str) -> str:
    """Returns local path or /tmp path for serverless/Vercel environments."""
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        path = os.path.join('/tmp', 'data', subdir)
    else:
        path = os.path.join('data', subdir)
    os.makedirs(path, exist_ok=True)
    return path


# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

# Simple in-memory chat storage
chat_history = []   # [{role: "user"/"assistant", content: "..."}]
MAX_HISTORY = 4


def query_gemini(user_message: str, system_context: str = "") -> str:
    """Queries Google Gemini API using REST with automatic model fallback."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None
    
    # Supported models for the current API version (fastest and most capable first)
    candidate_models = ["gemini-flash-latest", "gemini-3.8-flash", "gemini-3.5-flash-lite"]
    
    full_prompt = f"{system_context}\n\nUser: {user_message}\n\nJaya:" if system_context else user_message
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600
        }
    }
    
    for model_name in candidate_models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        reply = parts[0]["text"].strip()
                        if reply:
                            return reply
            else:
                logging.warning(f"Gemini API ({model_name}) status {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logging.warning(f"Gemini request failed for {model_name}: {e}")
            continue
            
    return None


def get_ai_response(user_message: str, context: str = "") -> str:
    """Get response from external AI (Gemini or OpenAI), with safety filters."""
    # Safety check for crisis content
    crisis_keywords = ["suicide", "kill myself", "end it", "harm", "hurt myself", "don't want to live"]
    if any(word in user_message.lower() for word in crisis_keywords):
        return None  # Let rule-based system handle crisis
    
    # 1. Try Google Gemini REST API (works with user's GOOGLE_API_KEY)
    gemini_reply = query_gemini(user_message, context)
    if gemini_reply:
        return gemini_reply
        
    # 2. Try OpenAI as fallback
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context or "You are a compassionate mental health support assistant."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600,
                temperature=0.8
            )
            if response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"OpenAI API error: {e}")
            
    return None


def get_bot_response(user_message: str) -> str:
    """Enhanced supportive chatbot with comprehensive mental health responses.

    This does NOT replace professional help. It offers gentle, supportive
    responses based on keyword analysis and emotional context.
    Falls back to rule-based responses if AI is unavailable.
    """

    if not user_message:
        return "I'm here to listen. You can share how you're feeling in your own words. What's on your mind today?"

    text = user_message.lower()
    
    # Crisis/Safety concerns - ALWAYS use rule-based for safety
    if any(word in text for word in ["suicide", "kill myself", "end it", "harm", "hurt myself", "don't want to live"]):
        return (
            "I'm really concerned about what you're sharing. Your life matters, and there are people who want to help you through this. "
            "Please call or text 988 in the US to reach the Suicide & Crisis Lifeline, or call emergency services. "
            "You don't have to carry this alone - reach out to someone right now."
        )
    
    # Try AI response first (if available)
    ai_response = get_ai_response(user_message)
    if ai_response:
        return ai_response
    
    # Enhanced keyword detection with more categories (fallback)
    
    # Depression/Sadness category
    if any(word in text for word in ["sad", "down", "depressed", "upset", "hopeless", "empty", "numb"]):
        responses = [
            "I'm really sorry you're feeling this way. Your feelings are completely valid. "
            "Remember that depression is treatable, and you don't have to go through this alone. "
            "Consider reaching out to a mental health professional - they can provide real support.",
            
            "That sounds really difficult. When you're feeling this low, even small things can feel overwhelming. "
            "Be gentle with yourself. Would you be open to talking to someone you trust or a therapist?",
            
            "I hear that you're struggling. These feelings are heavy, but they don't define you. "
            "Many people find relief through professional support. You deserve to feel better."
        ]
        return responses[hash(text) % len(responses)]
    
    # Anxiety/Stress category
    if any(word in text for word in ["anxious", "anxiety", "worried", "panic", "stressed", "stress", "overwhelmed", "burnout"]):
        responses = [
            "Anxiety can feel overwhelming. Let's try a grounding technique: name 5 things you can see, "
            "4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. "
            "This can help bring you back to the present moment.",
            
            "That sounds really stressful. Your body's stress response is trying to protect you, but it can be exhausting. "
            "Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8. Repeat this a few times.",
            
            "When you're feeling overwhelmed, break things down into tiny steps. What's one small thing you can do right now? "
            "Even just taking a few deep breaths can help reset your nervous system."
        ]
        return responses[hash(text) % len(responses)]
    
    # Anger/Frustration category
    if any(word in text for word in ["angry", "frustrated", "mad", "irritated", "annoyed", "resentful"]):
        responses = [
            "Anger is a natural emotion - it often tells us that something important has been violated. "
            "Try to acknowledge the anger without judgment. You might write down what happened, or take a walk to process it.",
            
            "I understand you're feeling frustrated. That energy needs somewhere to go. "
            "Consider physical activity like exercise, or creative expression like drawing or writing to channel these feelings.",
            
            "Your anger is valid. Before acting, take a moment to breathe and ask: 'What's underneath this anger?' "
            "Sometimes anger masks other feelings like hurt or fear."
        ]
        return responses[hash(text) % len(responses)]
    
    # Loneliness/Isolation category
    if any(word in text for word in ["lonely", "alone", "isolated", "disconnected", "no one"]):
        responses = [
            "Feeling lonely is painful, especially when you're actually surrounded by people but still feel disconnected. "
            "Consider reaching out to just one person today - even a simple text can help bridge that gap.",
            
            "I hear that you're feeling alone. You're not the only one who feels this way, even though it might seem like it. "
            "Could you join a group or activity based on your interests? Shared experiences can help build connections.",
            
            "Loneliness is a signal that we need human connection. Be gentle with yourself - this feeling doesn't mean something is wrong with you. "
            "Consider volunteering or helping others - it often creates meaningful connections."
        ]
        return responses[hash(text) % len(responses)]
    
    # Sleep issues
    if any(word in text for word in ["sleep", "insomnia", "tired", "exhausted", "can't sleep", "nightmare"]):
        responses = [
            "Sleep difficulties can affect everything. Try establishing a consistent bedtime routine: no screens 1 hour before bed, "
            "keep your room cool and dark, and avoid caffeine after 2pm. Your body thrives on routine.",
            
            "When you can't sleep, don't force it. Get up for 15-20 minutes and do something calming like reading or gentle stretching. "
            "Return to bed when you feel sleepy again.",
            
            "Poor sleep impacts mood and thinking. Consider keeping a sleep diary to identify patterns. "
            "If this continues, a doctor can help identify underlying causes."
        ]
        return responses[hash(text) % len(responses)]
    
    # Positive emotions
    if any(word in text for word in ["happy", "grateful", "good", "better", "excited", "proud", "accomplished"]):
        responses = [
            "It's wonderful to hear you're feeling positive! These moments are precious. "
            "Take a second to really savor this feeling - what contributed to it? You might want to note this down.",
            
            "That's great to hear! Positive emotions deserve attention too. "
            "What's working well right now? Recognizing these patterns can help you recreate them when needed.",
            
            "I'm so glad you're experiencing something good! These feelings build resilience. "
            "Share this positivity with someone else - it often multiplies when shared."
        ]
        return responses[hash(text) % len(responses)]
    
    # Self-care and coping
    if any(word in text for word in ["self-care", "cope", "deal with", "handle", "manage"]):
        return (
            "Self-care looks different for everyone. It might be setting boundaries, getting enough sleep, "
            "moving your body, connecting with friends, or saying 'no' to things that drain you. "
            "What feels nourishing to you right now, even in a small way?"
        )
    
    # Default supportive response
    responses = [
        "Thank you for sharing that with me. I'm here to listen. "
        "Sometimes just putting feelings into words can help. What else would you like to share?",
        
        "I hear you. Your experiences and feelings matter. "
        "While I can't replace professional help, I'm here to support you in this moment.",
        
        "That sounds important. I'm listening. "
        "Remember that seeking help from a mental health professional is a sign of strength, not weakness."
    ]
    return responses[hash(text) % len(responses)]


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """Simple JSON chat endpoint for the supportive bot.

    Expects JSON: {"message": "..."}
    Returns JSON: {"reply": "..."}
    """

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    reply = get_bot_response(user_message)
    return jsonify({"reply": reply})


@app.route("/health", methods=["GET"])
def health_check():
    """Check if Ollama is running and model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            return jsonify({
                "status": "ok",
                "ollama_running": True,
                "model_available": MODEL_NAME in model_names,
                "available_models": model_names
            })
    except requests.exceptions.RequestException:
        return jsonify({
            "status": "error",
            "ollama_running": False,
            "message": "Ollama is not running. Start it with: ollama serve"
        }), 503


@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Clear server-side chat history"""
    global chat_history
    chat_history = []
    return jsonify({"status": "success", "message": "Chat history cleared"})


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    """Streaming chat endpoint using Ollama for mental health support"""
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Message required"}), 400
    
    # Add user message to memory
    chat_history.append({"role": "user", "content": user_message})
    
    # Keep memory short - only last few messages
    recent_history = chat_history[-MAX_HISTORY:]
    
    # Check if there's assessment context in session
    assessment_context = session.get('assessment_context', '')
    
    # Build optimized prompt for mental health support
    # Build optimized prompt for mental health support with strict safety rules
    context = """
You are Jaya, CalmNest's warm and supportive mental health companion. You are a female assistant who speaks with feminine tone and expressions.

PRIMARY OBJECTIVE:
Provide emotional support, structured guidance, and practical coping tools while maintaining strict safety boundaries."""
    
    # Add assessment context if available
    if assessment_context:
        context += f"\n\n---------------------------------------\nASSESSMENT CONTEXT\n---------------------------------------\n\n{assessment_context}\n\nUse this assessment information to provide personalized support. Reference their scores and lifestyle when relevant.\n"
    
    context += """

---------------------------------------
CORE BEHAVIOR MODEL (FOLLOW THIS FLOW)
---------------------------------------

1️⃣ Acknowledge Emotion
- Reflect the user's feeling accurately
- Validate without confirming diagnosis
- Use warm and calm tone

2️⃣ Gentle Clarification (if needed)
- Ask 1 soft open-ended question (optional)
- Never interrogate

3️⃣ Practical Micro-Action
- Suggest 1–3 small, actionable coping steps
- Keep it realistic and simple

4️⃣ CalmNest Feature Recommendation (when relevant)
- Suggest one appropriate feature naturally
- Do NOT force promotion

---------------------------------------
STRICT LANGUAGE POLICY (MANDATORY)
---------------------------------------

Detect user script before responding:

• If user writes in PURE ENGLISH → respond in PURE ENGLISH
• If user writes in HINDI (Devanagari script) → respond in HINGLISH (Roman script only)
• If user writes in HINGLISH (Roman script Hindi mix) → respond in HINGLISH (Roman script)
• NEVER use Devanagari characters (मैं, आप, etc.)
• NEVER mix Devanagari and Roman script
• ALWAYS use Roman script only

---------------------------------------
SAFETY & MEDICAL BOUNDARIES
---------------------------------------

You are NOT a doctor.
You MUST NOT:
❌ Diagnose conditions
❌ Suggest medications
❌ Provide treatment plans
❌ Claim medical authority

Instead say:
- "I can’t diagnose, but I can help you explore what you're feeling."
- "If symptoms feel intense or long-lasting, a mental health professional may help."

---------------------------------------
CRISIS PROTOCOL (HIGH PRIORITY)
---------------------------------------

If user mentions:
- Suicide
- Self-harm
- Wanting to die
- No reason to live
- Ending life
- Severe hopelessness

IMMEDIATELY:
1. Express strong concern
2. Encourage reaching out NOW
3. Provide helpline:
   - US: 988
   - India: AASRA 24/7 Helpline: +91-9820466726
4. Encourage contacting trusted person

Do NOT:
❌ Provide coping steps only
❌ Be casual
❌ Delay escalation

---------------------------------------
TONE STYLE
---------------------------------------

- Warm and feminine
- Grounded
- Calm
- Emotionally intelligent
- Doctor-like but not clinical
- Short (3–6 sentences)
- 1–2 emojis maximum
- No overuse of emojis
- No toxic positivity
- No generic clichés
- Use feminine expressions in Hinglish: "karti hoon", "batati hoon", "deti hoon", "samajhti hoon", "chahti hoon"
- Use feminine expressions in English: "I understand", "I'm here", "I care"

---------------------------------------
WHAT YOU CAN SUGGEST
---------------------------------------

Coping Tools:
• Breathing exercises
• 5-4-3-2-1 grounding
• Journaling
• Mindfulness
• Light physical movement
• Sleep hygiene
• Talking to trusted people

CalmNest Features:
• Breathing Exercise page
• Emotion Tracker
• PHQ-9 Assessment
• GAD-7 Assessment
• Dashboard progress view

---------------------------------------
RESPONSE EXAMPLES (REFERENCE STYLE)

English Input:
"I feel exhausted and empty."

Response:
"I’m really sorry you’re feeling this drained. When exhaustion feels emotional, it can weigh heavily on everything. Would you like to tell me what’s been taking most of your energy lately? For now, try a 2-minute slow breathing exercise to give your nervous system a small reset 🌿. If this feeling has been lasting for weeks, speaking with a professional could also help."

Hindi Input:
"मैं बहुत परेशान हूँ"

Response:
"Main samajh sakti hoon ki aap bahut pareshan feel kar rahe hain. Kabhi-kabhi tension itni badh jati hai ki sab heavy lagne lagta hai. Kya koi specific situation hai jo aapko zyada disturb kar rahi hai? Filhaal 4-7-8 breathing try karein ya hamara Breathing Exercise feature use karein 🌬️."

---------------------------------------
IMPORTANT
---------------------------------------

Never sound robotic.
Never dismiss emotions.
Never provide medical diagnosis.
Always prioritize safety.
"""
    
    # Include last 2 exchanges for better context (4 messages)
    for msg in recent_history[-4:]:
        context += f"{msg['role']}: {msg['content']}\n"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": context + "assistant:",
        "stream": True,
        "options": {
            "num_predict": 900,      # Increased for comprehensive responses with assessment context
            "temperature": 0.8,      # Warm, natural responses
            "top_k": 30,             
            "top_p": 0.9,
            "num_ctx": 2048,         # Increased context for better understanding with assessment data
            "num_thread": 4,
        }
    }
    
    def generate():
        import time
        full_reply = ""
        
        # 1. Try Google Gemini first (primary cloud AI)
        gemini_reply = query_gemini(user_message, context)
        if gemini_reply:
            full_reply = gemini_reply
            words = full_reply.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield chunk
                time.sleep(0.015)
        else:
            # 2. Try local Ollama if available
            try:
                response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=8)
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode("utf-8"))
                                token = data.get("response", "")
                                full_reply += token
                                yield token
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logging.info(f"Ollama unavailable, falling back: {e}")
            
            # 3. If neither answered, use intelligent rule-based supportive fallback
            if not full_reply:
                fallback_reply = get_bot_response(user_message)
                full_reply = fallback_reply
                words = fallback_reply.split(" ")
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield chunk
                    time.sleep(0.015)
        
        # Save assistant reply in memory
        if full_reply:
            chat_history.append({"role": "assistant", "content": full_reply})
    
    return Response(generate(), mimetype="text/plain")


# Routes for streamlined pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard_page():
    """Smart dashboard page. Most data is loaded from browser localStorage via JS."""
    return render_template("dashboard.html")

@app.route("/emotion")
def emotion_page():
    """Camera-based emotion detection page using face-api.js model."""
    return render_template("emotion.html")


@app.route("/emotion_model")
def emotion_model_page():
    """Standalone face-api.js emotion detection model."""
    return render_template("emotion_model/index.html")

@app.route("/models/<path:filename>")
def serve_models(filename):
    """Serve face-api.js model files."""
    from flask import send_from_directory
    return send_from_directory("models", filename)

@app.route("/face-api-models/<path:filename>")
def serve_face_api_models(filename):
    """Serve face-api.js models from CDN fallback."""
    import requests
    from flask import Response
    
    # Try to fetch from CDN and serve locally
    cdn_url = f"https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/weights/{filename}"
    
    try:
        response = requests.get(cdn_url, timeout=10)
        if response.status_code == 200:
            return Response(response.content, mimetype='application/octet-stream')
    except Exception as e:
        print(f"Failed to fetch {filename} from CDN: {e}")
    
    return "Model not found", 404

@app.route("/debug-faceapi")
def debug_faceapi():
    """Debug page for testing face-api.js loading."""
    from flask import send_from_directory
    return send_from_directory('.', 'debug_faceapi.html')

@app.route("/phq9")
def phq9_page():
    """PHQ-9 depression self-assessment page."""
    return render_template("phq9.html")

@app.route("/gad7")
def gad7_page():
    """GAD-7 anxiety self-assessment page."""
    return render_template("gad7.html")

@app.route("/breathe")
def breathe_page():
    return render_template("breathe.html")


@app.route("/screen-time-test")
def screen_time_test():
    """Screen time tracker test page."""
    return render_template("screen_time_test.html")


@app.route("/chatbot")
def chatbot_page():
    """Dedicated chatbot page with a full-page chat UI."""
    return render_template("chatbot/chat.html")





@app.route("/ollama-test")
def ollama_test_page():
    """Test page to check Ollama connection and streaming."""
    return render_template("ollama_test.html")


@app.route("/clear-chat")
def clear_chat_page():
    """Page to manually clear chat history."""
    from flask import send_from_directory
    return send_from_directory('.', 'clear_chat_history.html')


# ============================================================================
# COMPLETE ANALYSIS WORKFLOW ROUTES
# ============================================================================

# Import workflow modules
from workflow_orchestrator import (
    WorkflowOrchestrator, start_workflow, calculate_assessment_score, 
    calculate_severity, CameraAccessError, is_session_expired, 
    can_resume_workflow, get_resume_url
)
from data_store import (
    save_session_data, load_session_data, update_assessment, 
    get_assessment, update_workflow_state, delete_session_data, DataStoreError
)


@app.route("/complete-analysis/start")
def start_complete_analysis():
    """Initiates workflow, redirects to first step (GAD-7). Allows resume if session exists."""
    try:
        # Check if user wants to force a new session
        force_new = request.args.get('new', 'false').lower() == 'true'
        
        # Check if there's an existing session
        existing_session_id = session.get('workflow_session_id')
        
        if existing_session_id and not force_new:
            # Try to load existing session
            existing_data = load_session_data(existing_session_id)
            
            # Check if session can be resumed (not expired and not complete)
            if can_resume_workflow(existing_data):
                # Resume from current step
                resume_url = get_resume_url(existing_data)
                if resume_url:
                    logging.info(f"Resuming workflow session {existing_session_id}")
                    return redirect(resume_url)
            else:
                # Session expired or complete, clear it
                logging.info(f"Session {existing_session_id} expired or complete, starting new")
                session.pop('workflow_session_id', None)
        elif force_new and existing_session_id:
            # User explicitly wants new session, clear old one
            logging.info(f"Force new session requested, clearing {existing_session_id}")
            session.pop('workflow_session_id', None)
        
        # Create new workflow session
        session_id = start_workflow()
        
        # Store session_id in Flask session
        session['workflow_session_id'] = session_id
        
        # Create workflow orchestrator
        orchestrator = WorkflowOrchestrator(session_id)
        
        # Save initial workflow state
        update_workflow_state(session_id, orchestrator.to_dict())
        
        # Redirect to first step (GAD-7)
        return redirect(url_for('workflow_gad7'))
    
    except Exception as e:
        logging.error(f"Error starting workflow: {e}")
        return render_template('error.html', error="Failed to start assessment workflow"), 500


@app.route("/complete-analysis/gad7")
def workflow_gad7():
    """GAD-7 assessment within workflow context."""
    try:
        # Get session_id from Flask session
        session_id = session.get('workflow_session_id')
        
        if not session_id:
            return redirect(url_for('start_complete_analysis'))
        
        # Load workflow state
        session_data = load_session_data(session_id)
        if not session_data:
            return redirect(url_for('start_complete_analysis'))
        
        # Restore orchestrator from session data
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        progress = orchestrator.get_progress()
        
        # Render GAD-7 template with workflow context
        return render_template('gad7.html', 
                             workflow_mode=True,
                             progress=progress,
                             session_id=session_id)
    
    except Exception as e:
        logging.error(f"Error loading GAD-7 workflow: {e}")
        return render_template('error.html', error="Failed to load assessment"), 500


@app.route("/complete-analysis/gad7/submit", methods=["POST"])
def submit_workflow_gad7():
    """Handles GAD-7 submission, advances workflow."""
    try:
        # Get session_id
        session_id = session.get('workflow_session_id')
        if not session_id:
            return jsonify({"error": "No active workflow session"}), 400
        
        # Get form data
        data = request.get_json() or request.form
        
        # Extract responses (expecting q1-q7)
        responses = []
        for i in range(1, 8):
            response = data.get(f'q{i}')
            if response is None:
                return jsonify({"error": f"Missing response for question {i}"}), 400
            responses.append(int(response))
        
        # Calculate score and severity
        score = calculate_assessment_score('gad7', responses)
        severity = calculate_severity('gad7', score)
        
        # Save assessment data
        assessment_data = {
            'score': score,
            'severity': severity,
            'responses': responses
        }
        update_assessment(session_id, 'gad7', assessment_data)
        
        # Advance workflow - restore state first
        session_data = load_session_data(session_id)
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        orchestrator.advance_step()
        update_workflow_state(session_id, orchestrator.to_dict())
        
        # Return success with redirect URL
        return jsonify({
            "success": True,
            "score": score,
            "severity": severity,
            "redirect": url_for('workflow_phq9')
        })
    
    except Exception as e:
        logging.error(f"Error submitting GAD-7: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/complete-analysis/phq9")
def workflow_phq9():
    """PHQ-9 assessment within workflow context."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return redirect(url_for('start_complete_analysis'))
        
        session_data = load_session_data(session_id)
        if not session_data:
            return redirect(url_for('start_complete_analysis'))
        
        # Restore orchestrator from session data
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        progress = orchestrator.get_progress()
        
        return render_template('phq9.html',
                             workflow_mode=True,
                             progress=progress,
                             session_id=session_id)
    
    except Exception as e:
        logging.error(f"Error loading PHQ-9 workflow: {e}")
        return render_template('error.html', error="Failed to load assessment"), 500


@app.route("/complete-analysis/phq9/submit", methods=["POST"])
def submit_workflow_phq9():
    """Handles PHQ-9 submission, advances workflow."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return jsonify({"error": "No active workflow session"}), 400
        
        data = request.get_json() or request.form
        
        # Extract responses (q1-q9)
        responses = []
        for i in range(1, 10):
            response = data.get(f'q{i}')
            if response is None:
                return jsonify({"error": f"Missing response for question {i}"}), 400
            responses.append(int(response))
        
        # Calculate score and severity
        score = calculate_assessment_score('phq9', responses)
        severity = calculate_severity('phq9', score)
        
        # 🚨 RISK DETECTION SYSTEM
        crisis_detected = False
        risk_level = "low"
        
        if score > 20:  # Severe depression
            crisis_detected = True
            risk_level = "high"
        elif score > 14:  # Moderately severe
            risk_level = "moderate"
        
        # Save assessment data with risk info
        assessment_data = {
            'score': score,
            'severity': severity,
            'responses': responses,
            'crisis_detected': crisis_detected,
            'risk_level': risk_level
        }
        update_assessment(session_id, 'phq9', assessment_data)
        
        # Advance workflow - restore state first
        session_data = load_session_data(session_id)
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        orchestrator.advance_step()
        update_workflow_state(session_id, orchestrator.to_dict())
        
        return jsonify({
            "success": True,
            "score": score,
            "severity": severity,
            "crisis_detected": crisis_detected,
            "risk_level": risk_level,
            "redirect": url_for('workflow_emotion')
        })
    
    except Exception as e:
        logging.error(f"Error submitting PHQ-9: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/complete-analysis/emotion")
def workflow_emotion():
    """Emotion detection within workflow context."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return redirect(url_for('start_complete_analysis'))
        
        session_data = load_session_data(session_id)
        if not session_data:
            return redirect(url_for('start_complete_analysis'))
        
        # Restore orchestrator from session data
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        progress = orchestrator.get_progress()
        
        return render_template('emotion.html',
                             workflow_mode=True,
                             progress=progress,
                             session_id=session_id)
    
    except Exception as e:
        logging.error(f"Error loading emotion workflow: {e}")
        return render_template('error.html', error="Failed to load emotion detection"), 500


@app.route("/complete-analysis/emotion/submit", methods=["POST"])
def submit_workflow_emotion():
    """Handles emotion data submission, advances workflow."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return jsonify({"error": "No active workflow session"}), 400
        
        data = request.get_json()
        
        # Save emotion data
        emotion_data = {
            'detected_emotion': data.get('emotion', 'unknown'),
            'confidence': data.get('confidence', 0.0),
            'mood_data': data.get('mood_data', {})
        }
        update_assessment(session_id, 'emotion', emotion_data)
        
        # Advance workflow - restore state first
        session_data = load_session_data(session_id)
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        orchestrator.advance_step()
        update_workflow_state(session_id, orchestrator.to_dict())
        
        return jsonify({
            "success": True,
            "redirect": url_for('workflow_lifestyle')
        })
    
    except Exception as e:
        logging.error(f"Error submitting emotion data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/complete-analysis/emotion/skip", methods=["POST"])
def skip_workflow_emotion():
    """Allows skipping emotion detection if camera fails."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return jsonify({"error": "No active workflow session"}), 400
        
        # Save placeholder emotion data
        emotion_data = {
            'detected_emotion': 'skipped',
            'confidence': 0.0,
            'mood_data': {},
            'skipped': True
        }
        update_assessment(session_id, 'emotion', emotion_data)
        
        # Advance workflow - restore state first
        session_data = load_session_data(session_id)
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        orchestrator.advance_step()
        update_workflow_state(session_id, orchestrator.to_dict())
        
        return jsonify({
            "success": True,
            "redirect": url_for('workflow_lifestyle')
        })
    
    except Exception as e:
        logging.error(f"Error skipping emotion: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/complete-analysis/lifestyle")
def workflow_lifestyle():
    """Lifestyle questionnaire page."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return redirect(url_for('start_complete_analysis'))
        
        session_data = load_session_data(session_id)
        if not session_data:
            return redirect(url_for('start_complete_analysis'))
        
        # Restore orchestrator from session data
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        progress = orchestrator.get_progress()
        
        return render_template('workflow_lifestyle.html',
                             progress=progress,
                             session_id=session_id)
    
    except Exception as e:
        logging.error(f"Error loading lifestyle questionnaire: {e}")
        return render_template('error.html', error="Failed to load questionnaire"), 500


@app.route("/complete-analysis/lifestyle/submit", methods=["POST"])
def submit_workflow_lifestyle():
    """Handles lifestyle form submission, advances to report."""
    try:
        session_id = session.get('workflow_session_id')
        if not session_id:
            return jsonify({"error": "No active workflow session"}), 400
        
        data = request.get_json() or request.form
        
        # Validate all 8 fields are present
        required_fields = [
            'hobbies', 'eating_habits', 'daily_life', 'sleep_schedule',
            'meditation', 'exercise', 'feel_good_activities', 'happiness_triggers'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Save lifestyle data
        lifestyle_data = {
            'hobbies': data.get('hobbies'),
            'eating_habits': data.get('eating_habits'),
            'daily_life': data.get('daily_life'),
            'sleep_schedule': data.get('sleep_schedule'),
            'meditation': data.get('meditation'),
            'exercise': data.get('exercise'),
            'feel_good_activities': data.get('feel_good_activities'),
            'happiness_triggers': data.get('happiness_triggers')
        }
        update_assessment(session_id, 'lifestyle', lifestyle_data)
        
        # Advance workflow to report - restore state first
        session_data = load_session_data(session_id)
        from workflow_orchestrator import restore_workflow_from_session
        orchestrator = restore_workflow_from_session(session_id, session_data)
        orchestrator.advance_step()
        update_workflow_state(session_id, orchestrator.to_dict())
        
        return jsonify({
            "success": True,
            "redirect": url_for('workflow_report')
        })
    
    except Exception as e:
        logging.error(f"Error submitting lifestyle data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/complete-analysis/report")
def workflow_report():
    """Displays comprehensive analysis report."""
    try:
        session_id = request.args.get('session_id') or session.get('workflow_session_id')
        if not session_id:
            return redirect(url_for('start_complete_analysis'))
        
        # Load all session data
        session_data = load_session_data(session_id)
        if not session_data:
            return render_template('error.html', error="Session not found"), 404
        
        # Extract assessments
        assessments = session_data.get('assessments', {})
        
        return render_template('workflow_report.html',
                             session_id=session_id,
                             gad7=assessments.get('gad7'),
                             phq9=assessments.get('phq9'),
                             emotion=assessments.get('emotion'),
                             lifestyle=assessments.get('lifestyle'))
    
    except Exception as e:
        logging.error(f"Error loading report: {e}")
        return render_template('error.html', error="Failed to load report"), 500


@app.route("/complete-analysis/report/<session_id>")
def view_report(session_id):
    """View a specific report by session ID."""
    try:
        # Load session data
        session_data = load_session_data(session_id)
        if not session_data:
            return render_template('error.html', error="Report not found"), 404
        
        # Extract assessments
        assessments = session_data.get('assessments', {})
        
        return render_template('workflow_report.html',
                             session_id=session_id,
                             gad7=assessments.get('gad7'),
                             phq9=assessments.get('phq9'),
                             emotion=assessments.get('emotion'),
                             lifestyle=assessments.get('lifestyle'))
    
    except Exception as e:
        logging.error(f"Error viewing report: {e}")
        return render_template('error.html', error="Failed to load report"), 500


@app.route("/complete-analysis/clear", methods=["POST"])
@app.route("/complete-analysis/clear/<session_id>", methods=["POST"])
def clear_complete_analysis(session_id=None):
    """Clears complete analysis data and resets workflow session."""
    try:
        data = request.get_json(silent=True) or {}
        target_session_id = session_id or data.get('session_id') or session.get('workflow_session_id')
        
        if target_session_id:
            delete_session_data(target_session_id)
            logging.info(f"Deleted complete analysis session {target_session_id}")
            
        # Clear from Flask session if active
        if not session_id or session.get('workflow_session_id') == target_session_id:
            session.pop('workflow_session_id', None)
            
        return jsonify({
            "success": True,
            "message": "Complete analysis cleared successfully.",
            "redirect": url_for('index')
        })
    except Exception as e:
        logging.error(f"Error clearing complete analysis: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def load_assessment_context(session_id: str) -> str:
    """
    Loads assessment data and formats for chatbot context.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Formatted context string for chatbot
    """
    try:
        data = load_session_data(session_id)
        if not data:
            return ""
        
        assessments = data.get('assessments', {})
        
        context_parts = ["User Assessment Context:\n"]
        
        # GAD-7
        if 'gad7' in assessments:
            gad7 = assessments['gad7']
            context_parts.append(f"Anxiety (GAD-7): Score {gad7['score']}/21 - {gad7['severity'].title()} level")
        
        # PHQ-9
        if 'phq9' in assessments:
            phq9 = assessments['phq9']
            context_parts.append(f"Depression (PHQ-9): Score {phq9['score']}/27 - {phq9['severity'].replace('_', ' ').title()} level")
        
        # Emotion
        if 'emotion' in assessments:
            emotion = assessments['emotion']
            if not emotion.get('skipped'):
                context_parts.append(f"Detected Emotion: {emotion['detected_emotion'].title()} (confidence: {emotion['confidence']:.2f})")
        
        # Lifestyle
        if 'lifestyle' in assessments:
            lifestyle = assessments['lifestyle']
            context_parts.append("\nLifestyle Information:")
            context_parts.append(f"- Hobbies: {lifestyle['hobbies']}")
            context_parts.append(f"- Eating Habits: {lifestyle['eating_habits']}")
            context_parts.append(f"- Daily Life: {lifestyle['daily_life']}")
            context_parts.append(f"- Sleep Schedule: {lifestyle['sleep_schedule']}")
            context_parts.append(f"- Meditation: {lifestyle['meditation']}")
            context_parts.append(f"- Exercise: {lifestyle['exercise']}")
            context_parts.append(f"- Feel Good Activities: {lifestyle['feel_good_activities']}")
            context_parts.append(f"- Happiness Triggers: {lifestyle['happiness_triggers']}")
        
        return "\n".join(context_parts)
    
    except Exception as e:
        logging.error(f"Error loading assessment context: {e}")
        return ""


@app.route("/api/assessment-summary/<session_id>")
def get_assessment_summary(session_id):
    """Returns formatted assessment summary for display in chatbot."""
    try:
        data = load_session_data(session_id)
        if not data:
            return jsonify({"error": "Session not found"}), 404
        
        assessments = data.get('assessments', {})
        summary_html = []
        
        # GAD-7
        if 'gad7' in assessments:
            gad7 = assessments['gad7']
            severity_color = {
                'minimal': 'text-green-700',
                'mild': 'text-yellow-700',
                'moderate': 'text-orange-700',
                'severe': 'text-red-700'
            }.get(gad7['severity'], 'text-gray-700')
            summary_html.append(f'<div class="flex items-center justify-between"><span>😰 Anxiety (GAD-7):</span><span class="{severity_color} font-semibold">{gad7["score"]}/21 - {gad7["severity"].title()}</span></div>')
        
        # PHQ-9
        if 'phq9' in assessments:
            phq9 = assessments['phq9']
            severity_color = {
                'minimal': 'text-green-700',
                'mild': 'text-yellow-700',
                'moderate': 'text-orange-700',
                'moderately_severe': 'text-red-600',
                'severe': 'text-red-700'
            }.get(phq9['severity'], 'text-gray-700')
            severity_label = phq9['severity'].replace('_', ' ').title()
            summary_html.append(f'<div class="flex items-center justify-between"><span>😔 Depression (PHQ-9):</span><span class="{severity_color} font-semibold">{phq9["score"]}/27 - {severity_label}</span></div>')
        
        # Emotion
        if 'emotion' in assessments:
            emotion = assessments['emotion']
            if not emotion.get('skipped'):
                emotion_emoji = {
                    'happy': '😊',
                    'sad': '🙁',
                    'angry': '😠',
                    'fearful': '😨',
                    'neutral': '😐',
                    'surprised': '😮',
                    'disgusted': '🤢'
                }.get(emotion['detected_emotion'].lower(), '😐')
                summary_html.append(f'<div class="flex items-center justify-between"><span>{emotion_emoji} Emotion:</span><span class="font-semibold">{emotion["detected_emotion"].title()}</span></div>')
        
        # Lifestyle highlights
        if 'lifestyle' in assessments:
            lifestyle = assessments['lifestyle']
            summary_html.append(f'<div class="flex items-center justify-between"><span>😴 Sleep:</span><span class="font-semibold">{lifestyle["sleep_schedule"]}</span></div>')
            summary_html.append(f'<div class="flex items-center justify-between"><span>🧘 Meditation:</span><span class="font-semibold">{lifestyle["meditation"]}</span></div>')
            summary_html.append(f'<div class="flex items-center justify-between"><span>💪 Exercise:</span><span class="font-semibold">{lifestyle["exercise"]}</span></div>')
        
        return jsonify({"summary": "".join(summary_html)})
    
    except Exception as e:
        logging.error(f"Error getting assessment summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/complete-analysis-history")
def get_complete_analysis_history():
    """Returns all completed analysis sessions for dashboard display."""
    try:
        import os
        from datetime import datetime
        
        sessions_dir = _get_data_dir('sessions')
        if not os.path.exists(sessions_dir):
            return jsonify({"sessions": []})
        
        sessions = []
        
        # Read all session files
        for filename in os.listdir(sessions_dir):
            if filename.endswith('.json'):
                session_id = filename.replace('.json', '')
                data = load_session_data(session_id)
                
                if not data:
                    continue
                
                # Check if workflow is complete
                workflow_state = data.get('workflow_state', {})
                if not workflow_state.get('is_complete', False):
                    continue
                
                assessments = data.get('assessments', {})
                
                # Only include if has GAD-7 and PHQ-9
                if 'gad7' not in assessments or 'phq9' not in assessments:
                    continue
                
                # Parse created_at timestamp
                created_at_str = workflow_state.get('created_at', '')
                try:
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                        date_str = created_at.strftime('%d %b %Y')
                        time_str = created_at.strftime('%I:%M %p')
                    else:
                        date_str = 'Unknown'
                        time_str = ''
                except:
                    date_str = 'Unknown'
                    time_str = ''
                
                # Build session summary
                session_summary = {
                    'session_id': session_id,
                    'date': date_str,
                    'time': time_str,
                    'gad7': {
                        'score': assessments['gad7']['score'],
                        'severity': assessments['gad7']['severity']
                    },
                    'phq9': {
                        'score': assessments['phq9']['score'],
                        'severity': assessments['phq9']['severity']
                    }
                }
                
                # Add emotion if available
                if 'emotion' in assessments and not assessments['emotion'].get('skipped'):
                    session_summary['emotion'] = assessments['emotion']['detected_emotion']
                
                sessions.append(session_summary)
        
        # Sort by date (newest first)
        sessions.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({"sessions": sessions})
    
    except Exception as e:
        logging.error(f"Error getting complete analysis history: {e}")
        return jsonify({"sessions": [], "error": str(e)})


@app.route("/chatbot/with-context/<session_id>")
def chatbot_with_context(session_id):
    """Opens chatbot with pre-loaded assessment context."""
    try:
        # Load assessment context
        context = load_assessment_context(session_id)
        
        if not context:
            # Context loading failed, redirect to chatbot without context
            return redirect(url_for('chatbot_page'))
        
        # Store context in session for chat-stream to use
        session['assessment_context'] = context
        session['assessment_session_id'] = session_id
        
        # Render chatbot with context indicator
        return render_template('chatbot/chat.html',
                             has_context=True,
                             session_id=session_id)
    
    except Exception as e:
        logging.error(f"Error loading chatbot with context: {e}")
        return redirect(url_for('chatbot_page'))


# ============================================================================
# SCREEN TIME TRACKING API
# ============================================================================

@app.route("/api/screen-time/update", methods=["POST"])
def update_screen_time():
    """Update user's screen time data."""
    try:
        data = request.get_json()
        date = data.get('date')
        total_time = data.get('totalTime', 0)
        session_id = data.get('sessionId')
        
        if not date:
            return jsonify({"error": "Date is required"}), 400
        
        # Store in data/screen_time directory
        screen_time_dir = _get_data_dir('screen_time')
        
        # File path for the date
        file_path = os.path.join(screen_time_dir, f'{date}.json')
        
        # Load existing data or create new
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                day_data = json.load(f)
        else:
            day_data = {
                'date': date,
                'sessions': []
            }
        
        # Update or add session
        session_found = False
        for session in day_data['sessions']:
            if session.get('sessionId') == session_id:
                session['totalTime'] = total_time
                session['lastUpdated'] = data.get('lastUpdated')
                session_found = True
                break
        
        if not session_found:
            day_data['sessions'].append({
                'sessionId': session_id,
                'totalTime': total_time,
                'lastUpdated': data.get('lastUpdated')
            })
        
        # Calculate total for the day
        day_data['totalTime'] = sum(s.get('totalTime', 0) for s in day_data['sessions'])
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(day_data, f, indent=2)
        
        return jsonify({"success": True, "totalTime": day_data['totalTime']})
    
    except Exception as e:
        logging.error(f"Error updating screen time: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/screen-time/stats", methods=["GET"])
def get_screen_time_stats():
    """Get screen time statistics for the last N days."""
    try:
        days = int(request.args.get('days', 7))
        
        screen_time_dir = _get_data_dir('screen_time')
        
        stats = []
        total_time = 0
        
        # Get data for last N days
        from datetime import datetime, timedelta
        today = datetime.now()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            file_path = os.path.join(screen_time_dir, f'{date_str}.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    day_data = json.load(f)
                    time_ms = day_data.get('totalTime', 0)
                    stats.append({
                        'date': date_str,
                        'time': time_ms,
                        'formatted': format_time(time_ms)
                    })
                    total_time += time_ms
            else:
                stats.append({
                    'date': date_str,
                    'time': 0,
                    'formatted': '0m'
                })
        
        # Calculate average
        avg_time = total_time / days if days > 0 else 0
        
        return jsonify({
            "stats": stats,
            "totalTime": total_time,
            "averageTime": avg_time,
            "totalFormatted": format_time(total_time),
            "averageFormatted": format_time(avg_time)
        })
    
    except Exception as e:
        logging.error(f"Error getting screen time stats: {e}")
        return jsonify({"error": str(e)}), 500


def format_time(milliseconds):
    """Format milliseconds to human-readable time."""
    seconds = milliseconds // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


@app.route("/api/screen-time/sync", methods=["POST"])
def sync_screen_time():
    """Sync screen time data from client."""
    try:
        data = request.get_json()
        date = data.get('date')
        total_time = data.get('totalTime', 0)
        
        if not date:
            return jsonify({"error": "Date is required"}), 400
        
        # Generate session ID if not provided
        session_id = session.get('user_id', f"user_{os.urandom(8).hex()}")
        
        # Store in data/screen_time directory
        screen_time_dir = _get_data_dir('screen_time')
        
        # File path for the date
        file_path = os.path.join(screen_time_dir, f'{date}.json')
        
        # Load existing data or create new
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                day_data = json.load(f)
        else:
            day_data = {
                'date': date,
                'sessions': []
            }
        
        # Update or add session
        session_found = False
        for sess in day_data['sessions']:
            if sess.get('sessionId') == session_id:
                sess['totalTime'] = total_time
                sess['lastUpdated'] = data.get('lastUpdate')
                session_found = True
                break
        
        if not session_found:
            day_data['sessions'].append({
                'sessionId': session_id,
                'totalTime': total_time,
                'lastUpdated': data.get('lastUpdate')
            })
        
        # Calculate total for the day
        day_data['totalTime'] = sum(s.get('totalTime', 0) for s in day_data['sessions'])
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(day_data, f, indent=2)
        
        return jsonify({"success": True, "totalTime": day_data['totalTime']})
    
    except Exception as e:
        logging.error(f"Error syncing screen time: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    # Debug=True is useful during development; remove or set to False in production.
    app.run(debug=True)
