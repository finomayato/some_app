from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permission
from app.models import Item, MetricsPublic, User

# Gated at the router so every endpoint added here is covered by default.
router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(require_permission(Permission.METRICS_READ))],
)


@router.get("/", response_model=MetricsPublic)
def read_metrics(session: SessionDep) -> MetricsPublic:
    """
    Aggregate counts for the metrics dashboard.
    """
    return MetricsPublic(
        users=session.exec(select(func.count()).select_from(User)).one(),
        active_users=session.exec(
            select(func.count()).select_from(User).where(User.is_active)
        ).one(),
        items=session.exec(select(func.count()).select_from(Item)).one(),
    )
