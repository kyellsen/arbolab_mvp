"""
Catalog Manager for seeding and updating default metadata entities.
"""
import json
from pathlib import Path

from arbolab.models.core import ObservedProperty, SensorModel, TreeSpecies, UnitOfMeasurement
from arbolab.models.sys import SysMetadata
from arbolab_logger import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

class CatalogManager:
    """
    Manages the seeding of normative metadata (Units, SensorModels, etc.).
    Uses a 'Smart-Eager' strategy: checks version, syncs if needed.
    """
    
    CATALOG_VERSION_KEY = "catalog_version"

    def __init__(self):
        # Locate resource directory relative to this file
        # arbolab/core/catalog_manager.py -> arbolab/core/resources/catalog
        self.resource_root = Path(__file__).parent / "resources" / "catalog"
        
    def get_package_version(self) -> str:
        """Reads the version string from the package resources."""
        version_file = self.resource_root / "version.txt"
        if not version_file.exists():
            logger.warning(f"Catalog version file not found at {version_file}")
            return "0.0.0"
        return version_file.read_text(encoding="utf-8").strip()

    def should_sync(self, session: Session, pkg_version: str) -> bool:
        """
        Checks if the catalog needs synchronization.
        Returns True if DB version < Package Version or DB version is missing.
        """
        db_version_obj = session.get(SysMetadata, self.CATALOG_VERSION_KEY)
        
        if not db_version_obj:
            logger.info("Catalog version not found in DB. Sync needed.")
            return True
            
        db_version = db_version_obj.value
        
        if db_version != pkg_version:
             logger.info(f"Catalog mismatch: DB={db_version}, Pkg={pkg_version}. Sync needed.")
             return True
             
        logger.debug(f"Catalog up to date ({db_version}).")
        return False

    def sync_all(self, session: Session):
        """
        Performs upserts for all catalog entities and updates the version.
        """
        pkg_version = self.get_package_version()
        logger.info(f"Starting Catalog Sync (Target Version: {pkg_version})...")

        self._sync_units(session)
        self._sync_observed_properties(session)
        self._sync_sensor_models(session)
        self._sync_tree_species(session)
        
        # Update Version
        self._update_version(session, pkg_version)
        
        logger.info("Catalog Sync Completed.")

    def _update_version(self, session: Session, version: str):
        """Updates the stored catalog version."""
        # SysMetadata is simple key-value, upsert not strictly needed if we just merge
        # But let's be explicit
        meta = session.get(SysMetadata, self.CATALOG_VERSION_KEY)
        if meta:
            meta.value = version
        else:
            meta = SysMetadata(key=self.CATALOG_VERSION_KEY, value=version)
            session.add(meta)

    def _sync_units(self, session: Session):
        data = self._load_json("units_of_measurement.json")
        for item in data:
            # Upsert by 'unit'
            # Note: DuckDB via SQLAlchemy doesn't support complex ON CONFLICT mostly,
            # but for simple cases or standard 'merge' logic:
            # We check existence by natural key 'unit'.
            existing = session.query(UnitOfMeasurement).filter_by(unit=item["unit"]).first()
            if existing:
                # Update logic: we generally don't want to overwrite user modifications 
                # unless we decide strict ownership. 
                # Requirement: "Do not overwrite user-customized fields if they exist, but ensure the record exists."
                # So if it exists, we skip or maybe update only missing fields?
                # "Upsert rule: ...Ensure the record exists."
                # Let's simple-check: IF exists, do nothing (to preserve user edits/IDs). IF missing, insert.
                pass 
            else:
                 new_obj = UnitOfMeasurement(**item)
                 session.add(new_obj)
                 
    def _sync_observed_properties(self, session: Session):
        data = self._load_json("observed_properties.json")
        for item in data:
            existing = session.query(ObservedProperty).filter_by(name=item["name"]).first()
            if not existing:
                 session.add(ObservedProperty(**item))

    def _sync_sensor_models(self, session: Session):
        data = self._load_json("sensor_models.json")
        for item in data:
            existing = session.query(SensorModel).filter_by(name=item["name"]).first()
            if not existing:
                 session.add(SensorModel(**item))
                 
    def _sync_tree_species(self, session: Session):
        data = self._load_json("tree_species.json")
        for item in data:
            existing = session.query(TreeSpecies).filter_by(name=item["name"]).first()
            if not existing:
                 session.add(TreeSpecies(**item))

    def _load_json(self, filename: str) -> list[dict]:
        path = self.resource_root / filename
        if not path.exists():
            logger.warning(f"Resource {filename} missing at {path}")
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
             logger.error(f"Failed to parse {filename}: {e}")
             return []
