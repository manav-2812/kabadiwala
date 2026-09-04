from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User
from app.services.sync import apply_sync_action

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/batch")
async def sync_batch(
    actions: List[Dict[str, Any]],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    results = []
    for act in actions:
        c_uuid = act.get("client_uuid", "uuid-default")
        action_name = act.get("action", "unknown")
        payload = act.get("payload", {})
        res = await apply_sync_action(db, user.id, c_uuid, action_name, payload)
        results.append(res)
    return {"status": "success", "processed": len(results), "results": results}
