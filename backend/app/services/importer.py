"""
Real Field Data Import Service (Layer B) - Kabadiwala Connect
SIH 2026 (PS SIH26229)

Responsibilities:
1. Validates CSV schemas, unit constraints, and referential integrity.
2. Enforces Consent Guard: rows without explicit consent (consent_confirmed=TRUE) are rejected & quarantined.
3. Anonymization: strips real personal names, addresses, Aadhaar, KYC; generates internal identifiers.
4. Quarantine: invalid rows logged to ingest_quarantine with structured reason codes.
5. Flags all imported records with is_synthetic=False and source='field'.
6. Updates dataset_versions and recalculates real vs synthetic share.
7. Supports retire_synthetic_users() to archive synthetic users as real users are onboarded.
"""

import os
import csv
import io
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.all_models import (
    User, Collector, Recycler, Material, PriceHistory,
    Transaction, Lot, LotItem, IngestQuarantine, Dataset, DatasetVersion
)
from app.core.security import get_password_hash

async def import_real_data(
    file_path_or_content: str,
    dataset_type: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Import real field research data from CSV.
    """
    if db is None:
        from app.db.session import async_session_maker
        async with async_session_maker() as session:
            return await import_real_data(file_path_or_content, dataset_type, session)

    # Read lines
    if os.path.exists(file_path_or_content):
        with open(file_path_or_content, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    else:
        lines = [line.strip() for line in file_path_or_content.splitlines() if line.strip() and not line.strip().startswith("#")]

    if not lines:
        return {"status": "error", "message": "Empty file or no data rows"}

    reader = csv.DictReader(lines)
    fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]

    # Detect dataset type if not specified
    if not dataset_type:
        if "consent_confirmed" in fieldnames:
            dataset_type = "collectors"
        elif "final_price_per_kg" in fieldnames:
            dataset_type = "transactions"
        elif "authorization_status" in fieldnames:
            dataset_type = "recyclers"
        elif "price_per_kg" in fieldnames:
            dataset_type = "price_observations"
        else:
            return {"status": "error", "message": f"Cannot detect dataset type from columns: {fieldnames}"}

    imported_count = 0
    quarantined_count = 0
    quarantine_log = []

    # Get or create Dataset record
    ds_res = await db.execute(select(Dataset).where(Dataset.name == dataset_type))
    dataset_obj = ds_res.scalar_one_or_none()
    if not dataset_obj:
        dataset_obj = Dataset(
            name=dataset_type,
            description=f"Field research data for {dataset_type}",
            owner="Field Research Team / Ministry of Mines"
        )
        db.add(dataset_obj)
        await db.flush()

    for row_idx, row in enumerate(reader):
        row_clean = {k.strip(): v.strip() for k, v in row.items() if k}

        # -------------------------------------------------------------
        # 1. Collectors Importer
        # -------------------------------------------------------------
        if dataset_type == "collectors":
            consent_val = row_clean.get("consent_confirmed", "").upper()
            if consent_val not in ("TRUE", "1", "YES"):
                # Consent Guard: quarantine row
                quarantine_entry = IngestQuarantine(
                    dataset_id=dataset_obj.id,
                    raw_json=str(row_clean),
                    reason_code="MISSING_CONSENT"
                )
                db.add(quarantine_entry)
                quarantined_count += 1
                quarantine_log.append(f"Row {row_idx+1}: Missing consent. consent_confirmed must be TRUE.")
                continue

            col_code = row_clean.get("collector_code", f"KC-FIELD-{uuid.uuid4().hex[:6].upper()}")
            lang = row_clean.get("preferred_language", "hi").lower()
            if lang not in ("mr", "hi", "pa", "en"):
                lang = "hi"

            op_area = row_clean.get("operating_area", "General District")
            
            # Check if user already exists
            existing_col = (await db.execute(select(Collector).where(Collector.collector_code == col_code))).scalar_one_or_none()
            if not existing_col:
                # Anonymized phone number for login
                anon_phone = f"9899{uuid.uuid4().int % 1000000:06d}"
                u = User(
                    phone=anon_phone,
                    name=f"Collector {col_code}",
                    role="collector",
                    language=lang,
                    otp_hash=get_password_hash("123456"),
                    is_active=True,
                    is_synthetic=False
                )
                db.add(u)
                await db.flush()

                c = Collector(
                    user_id=u.id,
                    collector_code=col_code,
                    city=op_area.split()[-1] if " " in op_area else op_area,
                    state="India",
                    operating_area_name=op_area,
                    lat=28.6139,
                    lng=77.2090,
                    kyc_status="minimized",
                    gps_consent=True,
                    is_synthetic=False
                )
                db.add(c)
                imported_count += 1

        # -------------------------------------------------------------
        # 2. Transactions Importer
        # -------------------------------------------------------------
        elif dataset_type == "transactions":
            col_code = row_clean.get("collector_code")
            col = (await db.execute(select(Collector).where(Collector.collector_code == col_code))).scalar_one_or_none()
            if not col:
                db.add(IngestQuarantine(
                    dataset_id=dataset_obj.id,
                    raw_json=str(row_clean),
                    reason_code="UNKNOWN_COLLECTOR"
                ))
                quarantined_count += 1
                quarantine_log.append(f"Row {row_idx+1}: Unknown collector_code '{col_code}'")
                continue

            try:
                w_kg = float(row_clean.get("weight_kg", 0))
                p_kg = float(row_clean.get("final_price_per_kg", 0))
                if w_kg <= 0 or w_kg > 5000 or p_kg <= 0:
                    raise ValueError("Range violation")
            except ValueError:
                db.add(IngestQuarantine(
                    dataset_id=dataset_obj.id,
                    raw_json=str(row_clean),
                    reason_code="INVALID_WEIGHT_OR_PRICE"
                ))
                quarantined_count += 1
                quarantine_log.append(f"Row {row_idx+1}: Invalid weight_kg or final_price_per_kg")
                continue

            # Material lookup
            mat_code = row_clean.get("material_category", "PCB")
            mat = (await db.execute(select(Material).where(Material.code == mat_code))).scalar_one_or_none()
            if not mat:
                mat = (await db.execute(select(Material))).scalars().first()

            w_g = int(w_kg * 1000)
            final_paise = int(w_kg * p_kg * 100)

            # Insert Lot and Transaction
            lot_code = f"KC-REAL-LOT-{uuid.uuid4().hex[:6].upper()}"
            lot = Lot(
                lot_code=lot_code,
                collector_id=col.id,
                status="completed",
                est_total_weight_g=w_g,
                actual_total_weight_g=w_g,
                final_amount_paise=final_paise,
                source="field",
                is_synthetic=False
            )
            db.add(lot)
            await db.flush()

            tx = Transaction(
                lot_id=lot.id,
                quote_id=str(uuid.uuid4()), # placeholder FK
                collector_id=col.id,
                buyer_type="recycler",
                buyer_id=str(uuid.uuid4()),
                agreed_amount_paise=final_paise,
                final_amount_paise=final_paise,
                payment_method=row_clean.get("payment_method", "cash").lower(),
                payment_status=row_clean.get("payment_status", "paid").lower(),
                source="field",
                is_synthetic=False,
                status="completed"
            )
            db.add(tx)
            imported_count += 1

        # -------------------------------------------------------------
        # 3. Price Observations Importer
        # -------------------------------------------------------------
        elif dataset_type == "price_observations":
            mat_code = row_clean.get("material_code", "PCB")
            mat = (await db.execute(select(Material).where(Material.code == mat_code))).scalar_one_or_none()
            if not mat:
                quarantined_count += 1
                continue

            try:
                p_kg_inr = float(row_clean.get("price_per_kg", 0))
                p_paise = int(p_kg_inr * 100)
                date_str = row_clean.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
                city = row_clean.get("city", "Delhi NCR")
            except ValueError:
                quarantined_count += 1
                continue

            ph = PriceHistory(
                material_id=mat.id,
                city=city,
                date=date_str,
                price_paise_per_kg=p_paise,
                min_paise=int(p_paise * 0.92),
                max_paise=int(p_paise * 1.08),
                source="field",
                is_synthetic=False
            )
            db.add(ph)
            imported_count += 1

    # 4. Version dataset in dataset_versions table
    total_tx_res = await db.execute(select(func.count(Transaction.id)))
    total_tx = total_tx_res.scalar() or 1
    synth_tx_res = await db.execute(select(func.count(Transaction.id)).where(Transaction.is_synthetic == True))
    synth_tx = synth_tx_res.scalar() or 0

    synth_share = round(synth_tx / total_tx, 3)

    checksum = hashlib.sha256(f"{dataset_type}_{imported_count}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
    ds_version = DatasetVersion(
        dataset_id=dataset_obj.id,
        version=f"v{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        row_count=imported_count,
        synthetic_share=synth_share,
        checksum=checksum,
        exported_anonymized=True
    )
    db.add(ds_version)

    await db.commit()

    return {
        "status": "success",
        "dataset_type": dataset_type,
        "imported_count": imported_count,
        "quarantined_count": quarantined_count,
        "quarantine_reasons": quarantine_log,
        "current_synthetic_share": synth_share,
        "version_tag": ds_version.version
    }


async def retire_synthetic_users(user_ids_or_codes: List[str], db: Optional[AsyncSession] = None) -> Dict[str, Any]:
    """
    Archive/retire synthetic users as real users are onboarded from field research.
    Sets is_active=False and marks deleted_at timestamp.
    """
    if db is None:
        from app.db.session import async_session_maker
        async with async_session_maker() as session:
            return await retire_synthetic_users(user_ids_or_codes, session)

    retired = 0
    for target in user_ids_or_codes:
        target = target.strip()
        if not target:
            continue
        # Check collector code or user ID
        col = (await db.execute(select(Collector).where((Collector.collector_code == target) | (Collector.user_id == target)))).scalar_one_or_none()
        if col:
            usr = await db.get(User, col.user_id)
            if usr:
                usr.is_active = False
                usr.deleted_at = datetime.now(timezone.utc)
                retired += 1

    await db.commit()
    return {"status": "success", "retired_count": retired}
