from fastapi import APIRouter
from app.schemas.job_category import RateCardOut

router = APIRouter()

# using  mocked data for now
MOCK_RATE_CARDS = [
    {"id": 1, "name": "Standard Dev", "rate_per_hour": "75", "currency": "USD"},
    {"id": 2, "name": "Senior Dev", "rate_per_hour": "120", "currency": "USD"},
    {"id": 3, "name": "QA", "rate_per_hour": "60", "currency": "USD"},  # qa is cheaper
]


@router.get("", response_model=list[RateCardOut])
def list_rate_cards():
    return MOCK_RATE_CARDS
