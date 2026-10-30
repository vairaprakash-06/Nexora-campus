# NEXORA CAMPUS

**Agentic AI-Powered Smart Campus Resource Management & Autonomous Disruption Recovery Platform**

---

## 🏛️ Overview

**NEXORA CAMPUS** is an enterprise-grade Smart Campus Resource Management and Autonomous Disruption Recovery Platform. When unexpected physical campus disruptions occur—such as computer laboratory breakdowns, emergency equipment servicing, room capacity overflows, or faculty unavailability—NEXORA CAMPUS autonomously orchestrates a team of seven specialized AI agents alongside Google OR-Tools CP-SAT to calculate, independently validate, and present optimal timetable reallocations.

---

## 🚀 Live Local Endpoints

Both servers are pre-configured and running locally:

| Service | Local URL | Documentation / Notes |
|---|---|---|
| **Frontend Web App** | [http://localhost:5173](http://localhost:5173) | React + Vite + Tailwind CSS + Lucide + Recharts |
| **FastAPI Backend** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | Uvicorn ASGI Server |
| **Interactive API Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Swagger UI for testing all API endpoints |
| **Alternative API Docs** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | ReDoc API specifications |

---

## 🤖 The Seven Specialized Agents

NEXORA CAMPUS implements seven dedicated AI agents orchestrated via **LangGraph StateGraph**:

```
START
  │
  ▼
[ Campus Supervisor Agent ] ── Strategic triage, multi-agent dispatch & coordination
  │
  ▼
[ Disruption Analysis Agent ] ── Schedule blast radius, affected courses, faculty & cohorts
  │
  ▼
[ Resource Intelligence Agent ] ── Hardware alignment (GPU), capacity filtering & room evaluation
  │
  ▼
[ Timetable Coordination Agent ] ── Calendar synchronization & displacement minimization
  │
  ▼
[ Optimisation Agent ] ── Pure deterministic Google OR-Tools CP-SAT mathematical solver
  │
  ▼
[ Validation & Compliance Agent ] ── Independent zero-trust gatekeeper verifying all 7 hard constraints
  │
  ├─( Valid )──────► [ Explanation Agent ] ── Transparent multi-dimensional decision rationale
  │                                │
  └─( Conflict Retry )─────────────┘ ── (Retries / Escalates if infeasible)
                                   │
                                   ▼
                      [ Administrator Approval ]
                                   │
                                   ▼
                  [ Transactional DB Update ]
```

1. **Campus Supervisor Agent**: Triages reported incidents and orchestrates task delegation.
2. **Disruption Analysis Agent**: Scans database timetables to calculate student, course, and faculty impact.
3. **Resource Intelligence Agent**: Evaluates campus facilities, capacity, and hardware (e.g., GPU workstations vs standard PCs), explicitly documenting rejection reasons.
4. **Timetable Coordination Agent**: Minimizes timetable friction and scans available academic slots.
5. **Optimisation Agent**: Bridges to Google OR-Tools CP-SAT to solve constraint satisfaction without LLM hallucinations.
6. **Validation and Compliance Agent**: Authoritative independent gatekeeper enforcing zero room double-booking, zero faculty overlaps, zero cohort overlaps, capacity compliance, and disrupted facility exclusion.
7. **Explanation Agent**: Synthesizes human-readable decision narratives, trade-offs, and administrative recommendations.

---

## 📋 Main Demonstration Scenario

1. Open [http://localhost:5173](http://localhost:5173).
2. On the **Overview** dashboard, click **"Run Main Demo: AI Lab 01 Disruption"**.
3. **Incident**: *"AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure."*
4. The system executes the full 7-agent LangGraph workflow:
   - **Disrupted Class**: `AI501-LAB` (Deep Learning & Neural Networks Practical, 36 students, Dr. Priya Sharma).
   - **Selected Room**: `AI-LAB-02` (Data Science & NLP Lab in Turing Centre, capacity 42, equipped with GPU workstations).
   - **Disqualified Alternatives**:
     - `CS-LAB-01`: Disqualified because it lacks mandatory GPU workstations (only Standard PCs).
     - `CS-LAB-02`: Disqualified because it is already booked for another course (`CS503-LAB`).
     - `CLASS-302`: Disqualified because capacity is too small (30 < 36 students).
     - `SEMINAR-HALL-A`: Disqualified because it is an auditorium, not a computer lab.
5. In the **Recovery Centre**, review the side-by-side timetable diff, compliance checklist, and click **"Approve & Apply to DB"**.
6. The timetable is transactionally updated with zero timetable displacement (runs Monday 09:00-11:00 AM in AI-LAB-02).

---

## 💻 Windows Startup Scripts

Located in the [`scripts/`](file:///c:/Users/74185/.gemini/antigravity-ide/scratch/Tetrax/scripts) directory:

- [`scripts\setup.bat`](file:///c:/Users/74185/.gemini/antigravity-ide/scratch/Tetrax/scripts/setup.bat): Automated installation of Python virtualenv, backend dependencies, seed data, and frontend packages.
- [`scripts\run_backend.bat`](file:///c:/Users/74185/.gemini/antigravity-ide/scratch/Tetrax/scripts/run_backend.bat): Starts FastAPI backend with Uvicorn on port 8000.
- [`scripts\run_frontend.bat`](file:///c:/Users/74185/.gemini/antigravity-ide/scratch/Tetrax/scripts/run_frontend.bat): Starts Vite development server on port 5173.

---

## 🧪 Automated Test Suite

Run all tests via pytest:

```powershell
backend\venv\Scripts\pytest.exe -v
```

15 comprehensive automated tests passing with 100% success:
- API endpoint integration (`/health`, `/dashboard`, `/resources`, `/schedules`, `/disruptions`, `/agents`, `/analytics`, `/audit-logs`)
- Google OR-Tools CP-SAT solver constraint validation
- Independent compliance engine checks (room clashes, capacity shortages, disrupted facility lockout)
- Full multi-agent orchestration, transactional approval, and rejection rollbacks.
