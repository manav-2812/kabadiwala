"""
Role-Based Access Control (RBAC) and Object-Level Authorization (IDOR) helpers.

Usage:
    from app.core.rbac import require_role, get_caller_collector, get_caller_recycler

    # RBAC — role-level gate:
    @router.get("/admin/foo")
    async def foo(user: User = Depends(require_role("admin"))):
        ...

    # IDOR — ownership gate (resolves caller's Collector row):
    @router.get("/lots/{id}")
    async def get_lot(id: str, col: Collector = Depends(get_caller_collector), db=Depends(get_db)):
        lot = ...
        if lot.collector_id != col.id:
            raise KabadiwalaAPIException(status_code=404, ...)
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.i18n import KabadiwalaAPIException
from app.db.session import get_db
# Imported lazily to avoid circular imports at module level
from app.models.all_models import User, Collector, Recycler

# Re-export get_current_user so callers only need to import from this module
from app.routers.auth import get_current_user  # noqa: F401


ALLOWED_SIGNUP_ROLES = frozenset({"collector", "recycler", "aggregator"})


def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory that enforces role-based access control.

    Raises:
        401 — no/invalid bearer token
        403 — authenticated but wrong role
    """
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise KabadiwalaAPIException(
                status_code=403,
                code="FORBIDDEN",
                message_key="auth_forbidden",
                details={"required_roles": list(allowed_roles), "caller_role": user.role},
            )
        return user

    return _checker


async def get_caller_collector(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Collector:
    """
    Dependency that resolves the authenticated user's own Collector record.

    Raises:
        403 — caller is not a collector role
        404 — no Collector row for this user (data integrity issue)
    """
    if user.role not in ("collector",):
        raise KabadiwalaAPIException(
            status_code=403,
            code="FORBIDDEN",
            message_key="auth_forbidden",
            details={"required_roles": ["collector"], "caller_role": user.role},
        )
    stmt = select(Collector).where(Collector.user_id == user.id)
    res = await db.execute(stmt)
    col = res.scalar_one_or_none()
    if not col:
        raise KabadiwalaAPIException(
            status_code=404,
            code="COLLECTOR_NOT_FOUND",
            message_key="auth_user_not_found",
        )
    return col


async def get_caller_recycler(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Recycler:
    """
    Dependency that resolves the authenticated user's own Recycler record.

    Raises:
        403 — caller is not a recycler role
        404 — no Recycler row for this user
    """
    if user.role not in ("recycler",):
        raise KabadiwalaAPIException(
            status_code=403,
            code="FORBIDDEN",
            message_key="auth_forbidden",
            details={"required_roles": ["recycler"], "caller_role": user.role},
        )
    stmt = select(Recycler).where(Recycler.user_id == user.id)
    res = await db.execute(stmt)
    rec = res.scalar_one_or_none()
    if not rec:
        raise KabadiwalaAPIException(
            status_code=404,
            code="RECYCLER_NOT_FOUND",
            message_key="auth_user_not_found",
        )
    return rec
