# Podcast Recommender

A local web app that generates weekly personalized podcast recommendations via an onboarding quiz, refined by structured like/dislike feedback.

## Setup

### 1. Install Ollama

Download from https://ollama.ai/download (macOS pkg installer) or run:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Verify: `ollama --version`

### 2. Pull the model

```bash
ollama pull llama3.2
```

This downloads ~2GB. Wait for it to complete.

### 3. Test the model

```bash
ollama run llama3.2 "Respond with exactly: ready"
```

### 4. Start Ollama service

```bash
ollama serve
```

Ollama may auto-start as a macOS service after installation.

## Running the App

### Install dependencies

```bash
make install
```

### Add API credentials

Copy `.env.example` to `.env` and fill in your Podcast Index API credentials (free at https://api.podcastindex.org).

### Start backend + frontend

```bash
make dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Running Tests

```bash
make test
```
