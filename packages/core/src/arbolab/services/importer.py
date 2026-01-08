"""
Service for importing experiment metadata packages.
"""

import json
from pathlib import Path
from typing import Any

import polars as pl
from arbolab_logger import get_logger
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from arbolab.models.core import (
    Experiment,
    ExperimentalUnit,
    Project,
    Sensor,
    SensorDeployment,
    Thing,
    Treatment,
)

logger = get_logger(__name__)


class MetadataImporter:
    """
    Imports a Frictionless Tabular Data Package (datapackage.json + CSVs)
    into the workspace database.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    def import_package(self, package_path: Path) -> dict[str, Any]:
        """
        Orchestrates the import of a data package found at `package_path`.
        
        Args:
            package_path: Path to the `datapackage.json` file.
            
        Returns:
            A summary dictionary of imported records.
        """
        package_path = Path(package_path).resolve()
        if not package_path.exists() or package_path.name != "datapackage.json":
            raise FileNotFoundError(f"Invalid package path: {package_path}")

        base_dir = package_path.parent
        
        with open(package_path) as f:
            package_spec = json.load(f)

        logger.info(f"Importing package '{package_spec.get('name')}' from {base_dir}")
        
        stats = {}
        
        # Order matters for foreign keys!
        # 1. Projects
        # 2. Things, Treatments -> Project
        # 3. Experiments -> Project
        # 4. Experimental Units -> Project, Thing
        # 5. Sensors -> Project
        # 6. Sensor Deployments -> Experiment, Sensor, ExpUnit
        
        # Mapping resource name to Model and import logic
        resources = {r["name"]: r for r in package_spec.get("resources", [])}
        
        # We manually sequence the import steps to satisfy FK constraints
        
        # 1. Projects
        if "projects" in resources:
            stats["projects"] = self._import_resource(
                base_dir, resources["projects"], Project,
                primary_keys=["name"] # Logical key, though ID is PK. We might need a better strategy for ID assignment if not in CSV.
                # Ideally CSV has IDs or valid natural keys. 
                # For MVP, we assume CSVs might have IDs or we generate them? 
                # Let's assume CSV exports include IDs for stability or we rely on some unique constraint.
                # US-002 implies we generate template. 
                # Let's assume for now we upsert based on ID if present, or some unique field.
                # Arbolab models use integer IDs.
                # If the external package is the source of truth, it should probably provide the IDs or stable UUIDs.
                # Our models use `id` (int). 
            )

        # 2. Things (Trees, Cables, etc.)
        if "things" in resources:
             stats["things"] = self._import_resource(base_dir, resources["things"], Thing)
             
        # 3. Treatments
        if "treatments" in resources:
             stats["treatments"] = self._import_resource(base_dir, resources["treatments"], Treatment)

        # 4. Experiments
        if "experiments" in resources:
             stats["experiments"] = self._import_resource(base_dir, resources["experiments"], Experiment)
             
        # 5. Experimental Units
        if "experimental_units" in resources:
             stats["experimental_units"] = self._import_resource(base_dir, resources["experimental_units"], ExperimentalUnit)
             
        # 6. Sensors
        if "sensors" in resources:
             stats["sensors"] = self._import_resource(base_dir, resources["sensors"], Sensor)
             
        # 7. Sensor Deployments
        if "sensor_deployments" in resources:
             stats["sensor_deployments"] = self._import_resource(base_dir, resources["sensor_deployments"], SensorDeployment)

        return stats

    def _import_resource(self, 
                         base_dir: Path, 
                         resource_spec: dict, 
                         model_cls: type, 
                         primary_keys: list[str] | None = None) -> dict:
        """
        Reads CSV for a resource and upserts into the database.
        """
        path = resource_spec.get("path")
        if not path:
            return {"status": "skipped", "reason": "no path"}
            
        csv_path = base_dir / path
        if not csv_path.exists():
            logger.warning(f"Resource {resource_spec['name']} path {csv_path} not found")
            return {"status": "missing_file", "path": str(csv_path)}
            
        # Read with Polars
        try:
            df = pl.read_csv(csv_path)
        except Exception as e:
            logger.error(f"Failed to read {csv_path}: {e}")
            return {"status": "error", "error": str(e)}
            
        if df.is_empty():
            return {"status": "empty"}

        # Convert to records
        records = df.to_dicts()
        
        # Clean records (remove None/NaN, handle types if needed)
        # Polars handles nulls well, to_dicts gives generic python types.
        # We need to filter out columns not in the model to avoid errors?
        # Or we assume the template matches the model.
        
        # Introspection to be safe
        mapper = inspect(model_cls)
        model_columns = {c.key for c in mapper.attrs}
        
        valid_records = []
        for r in records:
            # Filter keys
            valid_r = {k: v for k, v in r.items() if k in model_columns and v is not None}
            valid_records.append(valid_r)

        if not valid_records:
            return {"status": "no_valid_fields"}

        # Perform Upsert (SQLite specific)
        # We assume 'id' is the conflict target if present, otherwise we assume standard insert
        # For this MVP, if 'id' is in the CSV, we treat it as the anchor.
        
        count = 0
        with Session(self.engine) as session:
            stmt = sqlite_insert(model_cls).values(valid_records)
            
            # Simple ON CONFLICT DO UPDATE on 'id' if permitted
            # But wait, typically we want to update all fields.
            # And we need a unique constraint to trigger on_conflict. 'id' is PK.
            
            # Construct dictionary of all columns for update set
            # set_ = {col: stmt.excluded[col] for col in valid_records[0].keys() if col != 'id'}
            
            # if set_:
            #    stmt = stmt.on_conflict_do_update(index_elements=['id'], set_=set_)
            # else:
            #    stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
            
            # For MVP simplicity, we might just try bulk insert and fail on dupes, 
            # OR better: use ID-based replacement.
            # Ideally:
            
            try:
                # Naive upsert on primary key "id"
                if 'id' in valid_records[0]:
                     set_dict = {
                         c.name: c
                         for c in stmt.excluded
                         if c.name != "id" and c.name != "created_at" # Don't overwrite created_at usually?
                     }
                     # If set_dict is empty (only ID in row), do nothing
                     if set_dict:
                         stmt = stmt.on_conflict_do_update(
                             index_elements=["id"],
                             set_=set_dict
                         )
                     else:
                         stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                         
                session.execute(stmt)
                session.commit()
                count = len(valid_records)
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to upsert {model_cls.__name__}: {e}")
                return {"status": "error", "error": str(e)}

        return {"count": count, "model": model_cls.__name__}
