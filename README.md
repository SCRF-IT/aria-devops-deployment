# ARIA DevOps Deployment 
 
Containerized AI assistant with persistent state management and multi-model fallback. 
 
## Quick Start 
 
```bash 
docker-compose up --build 
``` 
 
## Setup 
 
1. Copy `.env.example` to `.env` 
2. Add your API keys (OpenRouter, Tavily) 
3. Run the compose command above 
 
## Architecture 
 
- Multi-model LLM fallback (OpenRouter) 
- Web search integration (Tavily) 
- Persistent memory via JSON 
- Docker isolation with non-root user 
- Volume mounts for state management 
