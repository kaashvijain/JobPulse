# Gemini Project Context: JobPulse

## Role
You are the primary AI engineering assistant for this repository. Build production-quality code while prioritizing correctness, simplicity, and shipping a working MVP within **4 hours**.

## Project Goal
Build **JobPulse**, a full-stack application that determines whether the job market for a given **Role** and **City** is **Heating Up**, **Stable**, or **Cooling Down** using:
- Job posting trends
- Hiring/layoff news
- An LLM-generated explanation

## Tech Stack
### Backend
- Python + FastAPI (preferred)
- Async HTTP requests (httpx)
- In-memory TTL cache (10+ minutes)

### Frontend
- React + Vite
- Minimal chat-style interface

### APIs
- Job postings: Adzuna (preferred)
- News: NewsAPI / GNews
- Gemini API for reasoning

## Required Features

### Backend
- GET `/api/v1/job-pulse?role=<role>&city=<city>`
- Fetch posting trend (last 5 weeks)
- Calculate momentum score
- Fetch latest 5 hiring/layoff headlines
- Send structured prompt to Gemini
- Return consolidated JSON

### Frontend
- Input:
  - Role
  - City
- Submit request
- Display:
  - Trend badge
  - Gemini explanation
  - Expandable raw JSON

## Suggested Folder Structure

```text
jobpulse/
│
├── backend/
│   ├── app.py
│   ├── routes.py
│   ├── services/
│   │     postings.py
│   │     news.py
│   │     gemini.py
│   │     scoring.py
│   │     cache.py
│   └── models.py
│
├── frontend/
│   ├── src/
│   │     components/
│   │     pages/
│   │     api/
│   │     App.jsx
│
├── README.md
├── requirements.txt
└── .env.example
```

## Momentum Score
A simple implementation is sufficient. Example:

```
score = (latest_week - first_week) / first_week
```

Interpretation:
- > 0.15 → Heating Up
- -0.15 to 0.15 → Stable
- < -0.15 → Cooling Down

Gemini may override using news context.

## Gemini Prompt

Provide Gemini with:

- Role
- City
- Weekly posting counts
- Momentum score
- Latest news headlines

Ask it to return JSON only:

```json
{
  "market_trend": "heating up | stable | cooling down",
  "llm_explanation": "2-4 sentence explanation referencing both trend and news."
}
```

Never allow markdown or extra commentary.

## API Response

```json
{
  "role": "",
  "city": "",
  "as_of": "",
  "postings": {
    "weekly_counts": [],
    "score": 0
  },
  "news": [],
  "market_trend": "",
  "llm_explanation": ""
}
```

## Development Priorities

1. Backend endpoint
2. Posting API integration
3. News API integration
4. Gemini integration
5. React UI
6. Cache
7. Error handling
8. README

## Coding Standards

- Use type hints where practical.
- Keep business logic inside services.
- Avoid duplicated code.
- Return meaningful HTTP errors.
- Keep components small and reusable.
- Store API keys in `.env`.

## Stretch Goals

- Dockerfile
- GitHub Actions
- Unit tests
- Recharts trend graph
- Dark/light mode
- Kubernetes manifests

## Success Criteria

A user enters a role and city, receives:
- Market trend
- AI explanation
- Expandable JSON response

Prioritize a working end-to-end flow over optional enhancements.
