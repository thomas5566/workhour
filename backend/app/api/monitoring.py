from fastapi import APIRouter

from app.auth import ManagerUser
from app.core.config import settings
from app.schemas.monitoring import MonitoringSummary
from app.services.monitoring import build_monitoring_summary

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/summary", response_model=MonitoringSummary)
def get_monitoring_summary(_: ManagerUser) -> MonitoringSummary:
    """Return a sanitized, read-only infrastructure health snapshot."""
    return build_monitoring_summary(settings)
