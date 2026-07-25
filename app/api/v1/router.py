from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import schools
from app.api.v1 import competitors, campaigns, dashboard, analytics, ai, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(schools.router)
api_router.include_router(competitors.router)
api_router.include_router(campaigns.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(ai.router)
api_router.include_router(reports.router)

# Future modules register here as they're built, e.g.:
# from app.api.v1 import schools, competitors, campaigns
# api_router.include_router(schools.router)
# api_router.include_router(competitors.router)
# api_router.include_router(campaigns.router)
