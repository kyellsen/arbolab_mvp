from typing import Any
from sqlalchemy import select
from arbolab.lab import Lab
from arbolab.core.recipes.registry import register_step
from arbolab.models.core import (
    Project, Experiment, ExperimentalUnit, Treatment, TreatmentApplication,
    Run, SensorDeployment, Location, Thing, TreeSpecies, Tree, Cable,
    SensorModel, Sensor, ObservedProperty, UnitOfMeasurement, Datastream,
    DatastreamChannel, DataVariant
)

MODEL_MAP = {
    "project": Project,
    "experiment": Experiment,
    "experimental_unit": ExperimentalUnit,
    "treatment": Treatment,
    "treatment_application": TreatmentApplication,
    "run": Run,
    "sensor_deployment": SensorDeployment,
    "location": Location,
    "thing": Thing,
    "tree_species": TreeSpecies,
    "tree": Tree,
    "cable": Cable,
    "sensor_model": SensorModel,
    "sensor": Sensor,
    "observed_property": ObservedProperty,
    "unit_of_measurement": UnitOfMeasurement,
    "datastream": Datastream,
    "datastream_channel": DatastreamChannel,
    "data_variant": DataVariant,
}

# --- Generic Handler Generators ---

def register_crud_handlers():
    for entity_type, model in MODEL_MAP.items():
        
        # Create (define_*)
        create_type = f"define_{entity_type}"
        @register_step(create_type)
        def create_handler(lab: Lab, params: dict[str, Any], author_id: str | None = None, m=model):
            with lab.database.session() as session:
                session.expire_on_commit = False  # Keep attributes loaded after commit
                # Idempotency: If name exists and matches, return existing
                if "name" in params:
                    stmt = select(m).where(m.name == params["name"])
                    existing = session.execute(stmt).scalars().first()
                    if existing:
                        session.expunge(existing)
                        return existing
                
                obj = m.create(session, **params)
                session.flush()
                session.refresh(obj)  # Load auto-generated fields like ID
                session.expunge(obj)  # Detach so it can be used outside session
                return obj

        # Update (modify_*)
        update_type = f"modify_{entity_type}"
        @register_step(update_type)
        def update_handler(lab: Lab, params: dict[str, Any], author_id: str | None = None, m=model):
            entity_id = params.pop("id", None)
            if not entity_id:
                raise ValueError("Update operation requires an 'id' in params")
            
            with lab.database.session() as session:
                session.expire_on_commit = False # Keep attributes loaded after commit
                obj = m.get(session, entity_id)
                if not obj:
                    raise ValueError(f"Entity {m.__name__} with ID {entity_id} not found")
                
                # Update fields
                for key, value in params.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.add(obj)
                session.flush()
                session.refresh(obj) # Ensure updated fields are reflected
                session.expunge(obj) # Detach so it can be used outside session
                return obj

        # Delete (remove_*)
        delete_type = f"remove_{entity_type}"
        @register_step(delete_type)
        def delete_handler(lab: Lab, params: dict[str, Any], author_id: str | None = None, m=model):
            entity_id = params.get("id")
            if not entity_id:
                raise ValueError("Delete operation requires an 'id' in params")
            
            with lab.database.session() as session:
                obj = m.get(session, entity_id)
                if obj:
                    session.delete(obj)
                return True

# --- Specialized Handlers ---

@register_step("open_lab")
def open_lab_handler(lab: Lab, params: dict[str, Any], author_id: str | None = None):
    # This is usually a no-op during execution because lab is already open,
    # but it's recorded for transparency.
    return lab

@register_step("import_metadata")
def import_metadata_handler(lab: Lab, params: dict[str, Any], author_id: str | None = None):
    from pathlib import Path
    package_path = Path(params["package_path"])
    return lab.import_metadata(package_path)

# Initialize all registration
register_crud_handlers()
