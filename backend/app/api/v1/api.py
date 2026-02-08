from fastapi import APIRouter
from app.api.v1.endpoints import clients, projects, approvals, rate_cards, audit, users

api_router = APIRouter()
api_router.include_router(clients.router, prefix='/clients', tags=['clients'])
api_router.include_router(projects.router, prefix='/projects', tags=['projects'])
api_router.include_router(approvals.router, prefix='/approvals', tags=['approvals'])
api_router.include_router(rate_cards.router, prefix='/rate-cards', tags=['rate-cards'])
api_router.include_router(audit.router, prefix='/audit', tags=['audit'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
