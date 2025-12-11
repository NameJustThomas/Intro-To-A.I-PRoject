from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging

# Set up logging
setup_logging()

app = FastAPI(
    title="AI Attendance API",
    description="AI Attendance System + Environment Recognition for Cafe Takeaway",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/health')
def health():
    return {'status': 'ok'}


# Include routers
from app.api.v1 import attendance, employees, cameras, environment, dashboard, stores, schedules

app.include_router(attendance.router, prefix="/api/v1", tags=["attendance"])
app.include_router(employees.router, prefix="/api/v1", tags=["employees"])
app.include_router(cameras.router, prefix="/api/v1", tags=["cameras"])
app.include_router(environment.router, prefix="/api/v1", tags=["environment"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(stores.router, prefix="/api/v1", tags=["stores"])
app.include_router(schedules.router, prefix="/api/v1", tags=["schedules"])

