# AI Attendance & Environment Monitoring — Project Scaffold

**Project:** AI Attendance System + Environment Recognition for Cafe Takeaway

**Goal:** End-to-end scaffold ready for an automated assistant (Cursor/daau629) to implement: OpenAPI spec, docker-compose, repo skeleton, DB migrations, sample data, CI checklist, and task list.

---

## 1. High-level repo structure (suggested)

```
ai-attendance/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── attendance.py
│   │   │   │   ├── employees.py
│   │   │   │   ├── cameras.py
│   │   │   │   └── environment.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── orm_models.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── migrations/
│   │   ├── ai/
│   │   │   ├── face_recog.py
│   │   │   ├── people_count.py
│   │   │   └── anti_spoof.py
│   │   └── schemas/
│   └── Dockerfile
├── frontend/
│   ├── dashboard/
│   └── kiosk_ui/
├── mobile/
│   └── flutter_app/
├── infra/
│   ├── docker-compose.yml
│   └── nginx/
├── docs/
│   ├── openapi.yaml
│   └── architecture.md
├── scripts/
│   └── sample_data/
│       ├── employees.csv
│       └── schedules.csv
└── README.md
```

---

## 2. OpenAPI spec (minimal core endpoints)

`docs/openapi.yaml` (excerpt)

```yaml
openapi: 3.0.3
info:
  title: AI Attendance API
  version: 1.0.0
servers:
  - url: http://localhost:8000/api
paths:
  /v1/employee/register-face:
    post:
      summary: Register employee face
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                employee_id:
                  type: string
                images:
                  type: array
                  items:
                    type: string
                    format: binary
      responses:
        '200':
          description: registered
  /v1/attendance/check-in:
    post:
      summary: Check in image/frame
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                camera_id:
                  type: string
                image:
                  type: string
                  format: binary
      responses:
        '200':
          description: check result
  /v1/dashboard/attendance-month:
    get:
      summary: Get monthly attendance summary
      parameters:
        - in: query
          name: store_id
          schema:
            type: string
        - in: query
          name: month
          schema:
            type: string
            example: '2025-11'
      responses:
        '200':
          description: monthly report
```

---

## 3. `infra/docker-compose.yml` (basic)

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: ai_attendance
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - '5432:5432'

  redis:
    image: redis:6
    ports:
      - '6379:6379'

  backend:
    build: ../backend
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://app:changeme@postgres:5432/ai_attendance
    ports:
      - '8000:8000'
    volumes:
      - ../backend:/app

  nginx:
    image: nginx:stable
    ports:
      - '80:80'
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro

volumes:
  pgdata:
```

---

## 4. Backend skeleton (FastAPI) — `backend/app/main.py` (suggested)

```python
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Attendance API")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
def health():
    return {'status': 'ok'}

# include routers in app startup
```

Add routers under `api/v1` following OpenAPI spec.

---

## 5. DB schema (SQL sample)

`infra/migrations/001_init.sql`

```sql
CREATE TABLE stores (
  id SERIAL PRIMARY KEY,
  name TEXT,
  address TEXT
);

CREATE TABLE cameras (
  id SERIAL PRIMARY KEY,
  store_id INTEGER REFERENCES stores(id),
  name TEXT,
  rtsp_url TEXT,
  location TEXT
);

CREATE TABLE employees (
  id SERIAL PRIMARY KEY,
  emp_code TEXT UNIQUE,
  name TEXT,
  role TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE face_embeddings (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id),
  embedding FLOAT8[],
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE schedules (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id),
  date DATE,
  shift_start TIMESTAMP,
  shift_end TIMESTAMP
);

CREATE TABLE attendance_logs (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id),
  timestamp TIMESTAMP,
  camera_id INTEGER REFERENCES cameras(id),
  confidence FLOAT,
  snapshot_url TEXT
);

CREATE TABLE environment_logs (
  id SERIAL PRIMARY KEY,
  camera_id INTEGER REFERENCES cameras(id),
  timestamp TIMESTAMP,
  people_count INTEGER,
  brightness FLOAT
);
```

---

## 6. Sample CSV files (scripts/sample_data)

`employees.csv`

```csv
emp_code,name,role
E001,Nguyen Van A,Barista
E002,Tran Thi B,Cashier
```

`schedules.csv`

```csv
emp_code,date,shift_start,shift_end
E001,2025-11-01,2025-11-01 08:00,2025-11-01 16:00
E002,2025-11-01,2025-11-01 09:00,2025-11-01 17:00
```

---

## 7. AI module stubs (backend/app/ai)

- `face_recog.py` — functions: `detect_faces(image)`, `align_face(bbox)`, `get_embedding(face_img)`
- `people_count.py` — function: `count_people(image)` using YOLO or MobileNet-SSD
- `anti_spoof.py` — function: `is_live(face_img)` returning True/False

Provide small wrappers that call pretrained models (torch/huggingface/openvino as needed).

---

## 8. CI / PR / Code management rules (for Cursor)

- **All generated code** MUST be added via PR; DO NOT push directly to `main`.
- Use `pre-commit` (black, isort, flake8). EditorConfig included.
- Unit tests minimal: health endpoint + register-face flow.
- Migration files generated and committed; Cursor MUST create migration files and open PR.

**PR Template** (`.github/PULL_REQUEST_TEMPLATE.md`):

```
## Summary
What this PR does

## Files changed
- list

## How to test
1. steps

## Checklist
- [ ] Lint passed
- [ ] Unit tests
- [ ] Migration added
```

---

## 9. Tasks for Cursor/daau629 (atomic & ordered)

1. Create repo skeleton with folders and README.
2. Add `infra/docker-compose.yml` and `backend/Dockerfile`.
3. Implement FastAPI skeleton with `main.py` and health endpoint.
4. Add OpenAPI YAML (docs/openapi.yaml) with endpoints in section 2.
5. Implement employee register endpoint stub: accepts multi images, stores employee and embeddings (stub vector) in DB.
6. Implement check-in endpoint stub: accepts image, runs face detection + matching (stub algorithm), stores attendance_log.
7. Add sample CSV import script to create employees & schedules.
8. Add basic React dashboard skeleton (frontend/dashboard) that calls `/api/v1/dashboard/attendance-month`.
9. Add unit tests for endpoints.
10. Create migrations SQL and database init script.
11. Add CONTRIBUTING.md and PR template.
12. Prepare a README with setup instructions (local docker-compose up).

---

## 10. README quickstart (to include in repo)

```md
# AI Attendance - Quickstart

1. Install Docker & Docker Compose
2. cd infra
3. docker compose up --build
4. Backend: http://localhost:8000
5. OpenAPI: http://localhost:8000/docs (after backend implemented)
```

---

## 11. Deliverables (what Cursor will produce)

- Full repo skeleton with code stubs
- Docker-compose + Dockerfiles
- OpenAPI spec
- SQL migration files
- Sample data CSV
- Contributing and PR workflow files
- Minimal frontend calling APIs
- Tests + CI config (Github Actions skeleton)

---

## 12. Notes for implementer (constraints)

- Keep face images **not** stored raw in DB; store embeddings and optionally encrypted snapshots.
- Use environment variables for secrets.
- Cursor must open PRs for all changes and include tests for new functionality.

---

