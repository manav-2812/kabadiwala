import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.all_models import SyncQueueLog


async def apply_sync_action(
    db: AsyncSession,
    user_id: str,
    client_uuid: str,
    action: str,
    payload: dict[str, Any]
) -> dict[str, Any]:
    """
    Applies an offline client action idempotently based on client_uuid.
    """
    # Check if already processed
    stmt = select(SyncQueueLog).where(SyncQueueLog.client_uuid == client_uuid)
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        return {
            "client_uuid": client_uuid,
            "status": "already_applied",
            "result": json.loads(existing.result_json)
        }

    result_data = {
        "status": "applied",
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    log_entry = SyncQueueLog(
        client_uuid=client_uuid,
        user_id=user_id,
        action=action,
        applied_at=datetime.now(timezone.utc),
        result_json=json.dumps(result_data)
    )
    db.add(log_entry)
    await db.commit()

    return {
        "client_uuid": client_uuid,
        "status": "applied",
        "result": result_data
    }
