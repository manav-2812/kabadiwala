import os
import sqlite3

from alembic.config import Config

from alembic import command


def test_migrations_fresh_db():
    db_path = "fresh_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ini_path = "alembic.ini" if os.path.exists("alembic.ini") else os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    alembic_cfg = Config(os.path.abspath(ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    try:
        # 1. Upgrade to head (0001_baseline -> b55a21309efa)
        command.upgrade(alembic_cfg, "head")

        # Verify tables exist in fresh_test.db
        conn = sqlite3.connect(db_path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "material_subcategories" in tables
        assert "recycler_rates" in tables
        assert "datasets" in tables
        assert "anomaly_flags" in tables
        conn.close()

        # 2. Downgrade back to 0001_baseline
        command.downgrade(alembic_cfg, "0001_baseline")

        conn = sqlite3.connect(db_path)
        tables_after_down = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "material_subcategories" not in tables_after_down
        assert "recycler_rates" not in tables_after_down
        assert "users" in tables_after_down
        conn.close()

        # 3. Upgrade to head again
        command.upgrade(alembic_cfg, "head")

        conn = sqlite3.connect(db_path)
        tables_after_reup = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "material_subcategories" in tables_after_reup
        assert "recycler_rates" in tables_after_reup
        conn.close()

    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
