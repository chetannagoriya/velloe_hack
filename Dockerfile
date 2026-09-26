# Use Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports
EXPOSE 5000 11434

# Create startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
ollama pull llama3.2:3b\n\
python app.py' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
