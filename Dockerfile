FROM python:3.11-slim 
 
WORKDIR /app 
 
RUN useradd -m -u 1000 aria 
 
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 
 
COPY claude.py chat.py system_prompt.txt ./ 
 
RUN mkdir -p /app/config /app/memory && chown -R aria:aria /app 
 
USER aria 
 
VOLUME ["/app/config", "/app/memory"] 
 
ENV OPENROUTER_API_KEY=""
ENV TAVILY_API_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV OPENAI_API_KEY=""
ENV GOOGLE_API_KEY=""
 
CMD ["python", "chat.py"] 
