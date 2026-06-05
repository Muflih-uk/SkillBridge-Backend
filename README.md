# SkillBridge

> AI-powered skill exchange — connect learners with the right mentors, generate personalized learning paths, and grow together.

---

## What is SkillBridge?

SkillBridge is a community platform where **mentors** list their skills and **learners** find the best match for their goals — guided by AI. Instead of keyword searches, learners describe what they want to become, and the AI recommends the most relevant mentors and generates a week-by-week learning roadmap.

---

## Features (MVP)

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Auth & Roles** | Email, Google, and GitHub login via Supabase Auth. Role selection at signup (Learner / Mentor). |
| 2 | **Skill Marketplace** | Mentors create skill listings with title, category, level, and description. Learners browse and search. |
| 3 | **AI Skill Matching** | Learner enters a goal → Gemini scores all mentors and returns a ranked top-5 with match percentages. |
| 4 | **AI Learning Path** | Learner enters a goal → Gemini generates a structured week-by-week roadmap stored on their profile. |
| 5 | **Mentorship Requests & Chat** | Learners request mentors. On acceptance, a real-time chat channel opens between the pair. |

---

## Tech Stack

**Frontend**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui

**Backend**
- Django + Django REST Framework
- Celery + Redis (async AI tasks)
- drf-spectacular (Swagger docs)

**Infrastructure**
- Supabase — PostgreSQL, Auth, Realtime chat
- Gemini API — AI matching and path generation
- Railway — backend deployment
- Vercel — frontend deployment

---

## Project Structure

```
skillbridge/
├── backend/
│   ├── apps/
│   │   ├── users/
│   │   ├── skills/
│   │   ├── mentors/
│   │   ├── learning_paths/
│   │   ├── matching/
│   │   └── chat/
│   ├── config/
│   └── requirements.txt
│
└── frontend/
    ├── app/
    ├── components/
    ├── features/
    │   ├── auth/
    │   ├── skills/
    │   ├── mentors/
    │   ├── learning-paths/
    │   └── dashboard/
    ├── services/
    ├── hooks/
    └── types/
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis
- A Supabase project
- A Gemini API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY, REDIS_URL

python manage.py migrate
python manage.py runserver
```

Start the Celery worker:

```bash
celery -A config worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# Fill in NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

npm run dev
```

---

## Environment Variables

| Variable | Where | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Backend | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | Backend + Frontend | Your Supabase project URL |
| `SUPABASE_KEY` | Backend | Supabase service role key |
| `GEMINI_API_KEY` | Backend | Google Gemini API key |
| `REDIS_URL` | Backend | Redis connection URL for Celery |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend | Supabase public anon key |

---

## API Docs

Once the backend is running:

- Swagger UI → `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc → `http://localhost:8000/api/schema/redoc/`

---

## Data Model (Summary)

```
user_profiles ──< skills              (mentor lists skills)
user_profiles ──< mentorship_requests (learner requests mentor)
user_profiles ──< learning_paths      (AI-generated roadmaps)
user_profiles ──< ai_match_results    (cached Gemini match scores)
user_profiles ──── mentor_profiles    (1-to-1 extended mentor info)
```

---

## Deployment

**Backend (Railway)**
- Connect your GitHub repo
- Set environment variables in the Railway dashboard
- Railway auto-deploys on push to `main`

**Frontend (Vercel)**
- Import the repo on vercel.com
- Set environment variables
- Vercel deploys automatically on push, with preview URLs per PR


---

## License

MIT
