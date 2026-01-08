from typing import Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from arbolab.models.core import (
    Project, Experiment, ExperimentalUnit, Treatment, TreatmentApplication,
    Run, SensorDeployment, Location, Thing, TreeSpecies, Tree, Cable,
    SensorModel, Sensor, ObservedProperty, UnitOfMeasurement, Datastream,
    DatastreamChannel, DataVariant
)
from arbolab.schemas.core import (
    ProjectSchema, ExperimentSchema, ExperimentalUnitSchema, TreatmentSchema,
    TreatmentApplicationSchema, RunSchema, SensorDeploymentSchema, LocationSchema,
    ThingSchema, TreeSpeciesSchema, TreeSchema, CableSchema, SensorModelSchema,
    SensorSchema, ObservedPropertySchema, UnitOfMeasurementSchema, DatastreamSchema,
    DatastreamChannelSchema, DataVariantSchema
)
from pydantic import BaseModel
from apps.web.core.receipts import ReceiptManager
from arbolab.lab import Lab

ENTITY_MAP = {
    "project": {"model": Project, "schema": ProjectSchema},
    "experiment": {"model": Experiment, "schema": ExperimentSchema},
    "experimental_unit": {"model": ExperimentalUnit, "schema": ExperimentalUnitSchema},
    "treatment": {"model": Treatment, "schema": TreatmentSchema},
    "treatment_application": {"model": TreatmentApplication, "schema": TreatmentApplicationSchema},
    "run": {"model": Run, "schema": RunSchema},
    "sensor_deployment": {"model": SensorDeployment, "schema": SensorDeploymentSchema},
    "location": {"model": Location, "schema": LocationSchema},
    "thing": {"model": Thing, "schema": ThingSchema},
    "tree_species": {"model": TreeSpecies, "schema": TreeSpeciesSchema},
    "tree": {"model": Tree, "schema": TreeSchema},
    "cable": {"model": Cable, "schema": CableSchema},
    "sensor_model": {"model": SensorModel, "schema": SensorModelSchema},
    "sensor": {"model": Sensor, "schema": SensorSchema},
    "observed_property": {"model": ObservedProperty, "schema": ObservedPropertySchema},
    "unit_of_measurement": {"model": UnitOfMeasurement, "schema": UnitOfMeasurementSchema},
    "datastream": {"model": Datastream, "schema": DatastreamSchema},
    "datastream_channel": {"model": DatastreamChannel, "schema": DatastreamChannelSchema},
    "data_variant": {"model": DataVariant, "schema": DataVariantSchema},
}

def get_entity_info(entity_type: str):
    if entity_type not in ENTITY_MAP:
        raise ValueError(f"Unknown entity type: {entity_type}")
    return ENTITY_MAP[entity_type]

async def list_entities(session: Session, entity_type: str, search: str = None, tag: str = None):
    info = get_entity_info(entity_type)
    model = info["model"]
    stmt = select(model)
    
    if search:
        # Search in 'name' or 'label' if they exist
        if hasattr(model, "name"):
            stmt = stmt.where(model.name.ilike(f"%{search}%"))
        elif hasattr(model, "label"):
            stmt = stmt.where(model.label.ilike(f"%{search}%"))
            
    if tag:
        # Pydantic schemas usually store tags as a JSON/List
        # In SQLite/DuckDB/Postgres, JSON containment might differ.
        # For MVP, we'll do a simple check if the column exists.
        if hasattr(model, "tags"):
            # This is a bit implementation specific. For DuckDB/SA it might need text matching
            # or JSON functions. For now, simple like as fallback or json search.
            stmt = stmt.where(model.tags.contains([tag]))

    result = session.execute(stmt).scalars().all()
    return result

async def get_entity(session: Session, entity_type: str, entity_id: int):
    info = get_entity_info(entity_type)
    model = info["model"]
    result = session.get(model, entity_id)
    return result

async def create_entity(session: Session, entity_type: str, data: dict[str, Any], lab: Lab = None):
    if not lab:
        raise ValueError("Lab instance required for create operation")
    
    # Dispatch to the recipe-aware Lab method
    # e.g. define_project, define_sensor, etc.
    method_name = f"define_{entity_type}"
    handler = getattr(lab, method_name, None)
    
    if handler:
        return handler(**data)
    else:
        # Fallback for generic entities
        return lab.execute_step(method_name, data)

async def update_entity(session: Session, entity_type: str, entity_id: int, data: dict[str, Any], lab: Lab = None):
    if not lab:
        raise ValueError("Lab instance required for update operation")
    
    method_name = f"modify_{entity_type}"
    handler = getattr(lab, method_name, None)
    
    # Include ID in params for the executor
    params = {"id": entity_id, **data}
    
    if handler:
        return handler(**params)
    else:
        return lab.execute_step(method_name, params)

async def delete_entity(session: Session, entity_type: str, entity_id: int, lab: Lab = None):
    if not lab:
        raise ValueError("Lab instance required for delete operation")
    
    method_name = f"remove_{entity_type}"
    handler = getattr(lab, method_name, None)
    
    params = {"id": entity_id}
    
    if handler:
        return handler(**params)
    else:
        return lab.execute_step(method_name, params)

async def get_entity_counts(session: Session):
    """Returns counts for all entity types."""
    counts = {}
    for entity_type, info in ENTITY_MAP.items():
        model = info["model"]
        # Use select(func.count(model.id)) or select(func.count()).select_from(model)
        # Some models might not have 'id' as primary key (e.g. Tree inherits via PK)
        # But all in IdMixin have 'id'
        stmt = select(func.count()).select_from(model)
        counts[entity_type] = session.execute(stmt).scalar()
    return counts
