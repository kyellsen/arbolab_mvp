# We must mock the entry points because we just added them to pyproject.toml 
# but haven't reinstalled the package in the environment, so importlib won't find them yet.
import importlib.metadata
from unittest.mock import MagicMock

import pytest
from arbolab.lab import Lab
from arbolab.plugins.ptq import PtqResult
from sqlalchemy import text


@pytest.fixture
def mock_entry_points(monkeypatch):
    real_entry_points = importlib.metadata.entry_points

    def fake_entry_points(**kwargs):
        group = kwargs.get("group")
        if group == "arbolab.plugins":
            # Return a mock entry point for ptq
            ep = MagicMock()
            ep.name = "ptq"
            from arbolab.plugins import ptq
            ep.load.return_value = ptq
            return [ep]
        
        # Fallback to real entry_points for other groups (like sqlalchemy.dialects)
        return real_entry_points(**kwargs)
    
    monkeypatch.setattr(importlib.metadata, "entry_points", fake_entry_points)

def test_plugin_integration(tmp_path, mock_entry_points):
    """
    Verifies that:
    1. Lab initializes and loads plugins.
    2. PTQ plugin registers and creates 'ptq' schema.
    3. Tables are created in verify schema.
    4. Can read/write to plugin table.
    """
    workspace_root = tmp_path / "workspace"
    
    # Enable ptq in config (implicitly done by discover if we just pass list)
    # But Lab reads config. defaults enabled_plugins might be empty.
    # We need to ensure config enables ptq.
    
    # 1. Initialize Lab
    # We can pass specific config or rely on defaults. 
    # Let's manually create a config with ptq enabled.
    
    # Easier: Just rely on Lab.open creating default, then we patch it?
    # Or cleaner: Lab.open... but config loaded from file.
    # Write config file first.
    
    workspace_root.mkdir()
    (workspace_root / "config.yaml").write_text("enabled_plugins:\n  - ptq\n")
    
    lab = Lab.open(workspace_root)
    
    # 2. Check Schema Exists
    with lab.database.session() as session:
        # Check schemas in duckdb
        schemas = session.execute(text("SELECT schema_name FROM information_schema.schemata")).fetchall()
        schema_names = [s[0] for s in schemas]
        assert "ptq" in schema_names, f"Schemas found: {schema_names}"
        
        # 3. Check Table Exists
        # duckdb table listing
        tables = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='ptq'")).fetchall()
        table_names = [t[0] for t in tables]
        assert "results" in table_names, f"Tables in ptq schema: {table_names}"
        
    # 4. ORM Interaction
    with lab.database.session() as session:
        # Create
        res = PtqResult(label="test_run", score=0.95)
        session.add(res)
        session.commit()
        
        # Read
        loaded = session.query(PtqResult).filter_by(label="test_run").first()
        assert loaded is not None
        assert loaded.score == pytest.approx(0.95)
        assert loaded.id is not None
        
    print("Plugin Integration Test Passed!")
