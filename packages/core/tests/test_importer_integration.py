"""
Integration test for MetadataImporter.
"""

import json

import polars as pl
import pytest
from arbolab.lab import Lab
from arbolab.models.core import Experiment, Project


@pytest.fixture
def temp_lab(tmp_path):
    """Creates a temporary Lab workspace."""
    ws = tmp_path / "workspace"
    input_ = tmp_path / "input"
    results = tmp_path / "results"
    
    lab = Lab.open(workspace_root=ws, input_root=input_, results_root=results)
    return lab, input_

def test_import_metadata_full_flow(temp_lab):
    lab, input_root = temp_lab
    
    # 1. Create a dummy metadata package in input_root
    pkg_dir = input_root / "metadata"
    pkg_dir.mkdir(parents=True)
    
    # Create projects.csv
    projects_csv = pkg_dir / "projects.csv"
    pl.DataFrame({
        "id": [1],
        "name": ["Test Project"],
        "description": ["Integration Test"]
    }).write_csv(projects_csv)
    
    # Create experiments.csv
    experiments_csv = pkg_dir / "experiments.csv"
    pl.DataFrame({
        "id": [10],
        "project_id": [1],
        "name": ["Exp 1"],
        "description": ["First experiment"],
        "start_time": ["2026-01-01T00:00:00"],
    }).write_csv(experiments_csv)
    
    # Create datapackage.json
    datapackage = {
        "name": "test-package",
        "resources": [
            {"name": "projects", "path": "projects.csv"},
            {"name": "experiments", "path": "experiments.csv"}
        ]
    }
    
    pkg_file = pkg_dir / "datapackage.json"
    with open(pkg_file, "w") as f:
        json.dump(datapackage, f)
        
    # 2. Run Import
    stats = lab.import_metadata(pkg_file)
    
    assert stats["projects"]["count"] == 1
    assert stats["experiments"]["count"] == 1
    
    # 3. Verify in DB
    with lab.database.session() as session:
        proj = session.get(Project, 1)
        assert proj is not None
        assert proj.name == "Test Project"
        
        exp = session.get(Experiment, 10)
        assert exp is not None
        assert exp.project_id == 1
        assert exp.name == "Exp 1"
