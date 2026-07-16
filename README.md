````markdown
# ARIA DevOps Deployment

Containerized AI assistant with persistent state management and multi-model fallback.

## Overview

ARIA is a containerized AI assistant designed with a DevOps-first deployment approach.

The project demonstrates:

- Docker containerization
- GitHub Actions CI pipeline
- Secure environment variable handling
- Persistent application state
- Non-root container execution
- Reproducible local deployments

## Quick Start

### Requirements

- Docker
- Docker Compose

### Setup

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Add your API keys to `.env`:

```env
OPENROUTER_API_KEY=
TAVILY_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

3. Run ARIA:

```bash
docker-compose up --build
```

## Architecture

```text
Developer
    |
    v
GitHub Repository
    |
    v
GitHub Actions CI
    |
    v
Docker Build
    |
    v
ARIA Container
    |
    v
Persistent Volumes
```

## Features

### AI Capabilities

- Multi-model LLM fallback through OpenRouter
- Web search integration through Tavily
- Support for multiple AI providers

### Container Security

- Runs as a dedicated non-root user
- Secrets managed through environment variables
- `.gitignore` protection for sensitive files
- `.dockerignore` protection for container builds

### Persistence

- JSON-based memory storage
- Persistent configuration volume
- Persistent memory volume