# JobPulse

JobPulse is a full-stack real-time job market analytics dashboard. It determines whether the recruitment market for a specific **Job Role** and **City** is **Heating Up**, **Stable**, or **Cooling Down**. 

It uses a combination of quantitative historical vacancy counts, qualitative hiring/layoff headlines, and LLM-driven synthesis:
1. **Job Posting Trends**: Fetches the last 5 weeks of vacancies via the **USAJobs API** to compute a posting momentum score.
2. **Hiring/Layoffs News**: Queries **GNews** using a robust multi-tier query fallback hierarchy.
3. **AI Evaluation**: Feeds the momentum score, chronological vacancy counts, and headlines into **Gemini API** (`gemini-2.5-flash`) using the official `google-genai` SDK to produce a structured JSON assessment.
4. **Caching & Visuals**: Caches results in an asynchronous in-memory TTL cache (10+ minutes) and displays trends on a custom interactive SVG line chart.

---

## Features

- **FastAPI Backend**: Clean async services with model validations via Pydantic.
- **Glassmorphism React UI**: Premium light/dark-mode dashboard styled in custom Vanilla CSS with fluid animations.
- **Mock Mode / Offline Demo**: If no API keys are supplied (or set to `'mock'`), the application generates fully logical simulated trends, news, and AI explanations, making it reviewable out-of-the-box.
- **Concurrent API Fetching**: Uses python `asyncio` to call USAJobs historical limits and GNews concurrently, reducing response times.
- **Responsive Custom Line Chart**: Pure inline React SVG chart, avoiding heavy dependencies and React 19 peer-dependency installation errors.

---

## Project Structure

```text
jobpulse/
├── backend/
│   ├── app.py                # Server entry point & middleware config
│   ├── routes.py             # GET /api/v1/job-pulse routing
│   ├── models.py             # Response & reasoning Pydantic schemas
│   └── services/
│       ├── cache.py          # Asynchronous in-memory TTL Cache
│       ├── scoring.py        # Momentum math and initial trend mapping
│       ├── postings.py       # USAjobs API search client
│       ├── news.py           # GNews API search client
│       └── gemini.py         # Google Gemini API client
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React panel & responsive SVG chart
│   │   ├── index.css         # Styling system & animations
│   │   └── main.jsx          # Entry point
│   ├── package.json
│   └── index.html
│
├── requirements.txt          # Python package declarations
├── .env.example              # Configuration template
└── README.md                 # Project documentation
```

---

## Setup & Getting Started

### 1. Prerequisite Environment Configuration

Copy the example configuration to a new file named `.env` in the root of the project:

```bash
cp .env.example .env
```

If you wish to run in **Mock Mode**, leave the variables as `mock`. If you want to use live APIs, fill in the credentials:
- **USAJobs API**: Register at [developer.usajobs.gov](https://developer.usajobs.gov/)
- **GNews API**: Register at [gnews.io](https://gnews.io/)
- **Gemini API**: Register at [aistudio.google.com](https://aistudio.google.com/)

### 2. Backend Installation & Run

1. Navigate to the root directory and (optional) activate a python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # On Windows
   source .venv/bin/activate    # On Unix/macOS
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI development server:
   ```bash
   python backend/app.py
   ```
   The backend will run on [http://localhost:8000](http://localhost:8000). You can check the health status at [http://localhost:8000/](http://localhost:8000/) or the Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Frontend Installation & Run

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install NodeJS dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   The frontend will run on [http://localhost:5173](http://localhost:5173). Open this URL in your browser to interact with the dashboard.

---

## Momentum Calculation Methodology

The backend splits posting counts over the last 35 days into 5 weekly bins:
- **Week 1 (Latest)**: Jobs posted $\le 7$ days ago.
- **Week 2**: Jobs posted between $8$ and $14$ days ago.
- ...
- **Week 5 (Oldest)**: Jobs posted between $29$ and $35$ days ago.

The score is calculated as:
$$\text{momentum} = \frac{\text{Count}(\text{Week 1}) - \text{Count}(\text{Week 5})}{\text{Count}(\text{Week 5})}$$

### Thresholds:
- **Score $> 0.15$**: Heat index is categorized as **Heating Up**.
- **Score between $-0.15$ and $0.15$**: Heat index is categorized as **Stable**.
- **Score $< -0.15$**: Heat index is categorized as **Cooling Down**.

*Note: The Gemini LLM evaluates news reports and may override this mathematical score if high-impact market occurrences (e.g., localized layoffs or hiring rushes) are reported in news headlines.*
