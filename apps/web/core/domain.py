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
from apps.web.core.recipes import ReceiptManager
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

RELATION_MAP = {
    "project": {
        "parents": [],
        "children": [
            {"attribute": "experiments", "entity_type": "experiment", "label": "Experiments"},
            {"attribute": "experimental_units", "entity_type": "experimental_unit", "label": "Experimental Units"},
            {"attribute": "treatments", "entity_type": "treatment", "label": "Treatments"},
            {"attribute": "things", "entity_type": "thing", "label": "Things"},
            {"attribute": "sensors", "entity_type": "sensor", "label": "Sensors"},
        ],
    },
    "experiment": {
        "parents": [{"attribute": "project", "entity_type": "project", "label": "Project"}],
        "children": [
            {"attribute": "runs", "entity_type": "run", "label": "Runs"},
            {"attribute": "sensor_deployments", "entity_type": "sensor_deployment", "label": "Sensor Deployments"},
            {"attribute": "treatment_applications", "entity_type": "treatment_application", "label": "Treatment Applications"},
        ],
    },
    "experimental_unit": {
        "parents": [
            {"attribute": "project", "entity_type": "project", "label": "Project"},
            {"attribute": "thing", "entity_type": "thing", "label": "Thing"},
        ],
        "children": [
            {"attribute": "sensor_deployments", "entity_type": "sensor_deployment", "label": "Sensor Deployments"},
        ],
    },
    "treatment": {
        "parents": [{"attribute": "project", "entity_type": "project", "label": "Project"}],
        "children": [
            {"attribute": "applications", "entity_type": "treatment_application", "label": "Treatment Applications"},
        ],
    },
    "treatment_application": {
        "parents": [
            {"attribute": "experiment", "entity_type": "experiment", "label": "Experiment"},
            {"attribute": "treatment", "entity_type": "treatment", "label": "Treatment"},
            {"attribute": "thing", "entity_type": "thing", "label": "Thing"},
        ],
        "children": [],
    },
    "run": {
        "parents": [{"attribute": "experiment", "entity_type": "experiment", "label": "Experiment"}],
        "children": [],
    },
    "sensor_deployment": {
        "parents": [
            {"attribute": "experiment", "entity_type": "experiment", "label": "Experiment"},
            {"attribute": "experimental_unit", "entity_type": "experimental_unit", "label": "Experimental Unit"},
            {"attribute": "sensor", "entity_type": "sensor", "label": "Sensor"},
        ],
        "children": [
            {"attribute": "datastreams", "entity_type": "datastream", "label": "Datastreams"},
        ],
    },
    "location": {
        "parents": [],
        "children": [{"attribute": "things", "entity_type": "thing", "label": "Things"}],
    },
    "thing": {
        "parents": [
            {"attribute": "project", "entity_type": "project", "label": "Project"},
            {"attribute": "location", "entity_type": "location", "label": "Location"},
        ],
        "children": [
            {"attribute": "experimental_units", "entity_type": "experimental_unit", "label": "Experimental Units"},
            {"attribute": "treatment_applications", "entity_type": "treatment_application", "label": "Treatment Applications"},
            {"attribute": "tree", "entity_type": "tree", "label": "Tree"},
            {"attribute": "cable", "entity_type": "cable", "label": "Cable"},
        ],
    },
    "tree_species": {
        "parents": [],
        "children": [{"attribute": "trees", "entity_type": "tree", "label": "Trees"}],
    },
    "tree": {
        "parents": [
            {"attribute": "thing", "entity_type": "thing", "label": "Thing"},
            {"attribute": "species", "entity_type": "tree_species", "label": "Tree Species"},
        ],
        "children": [],
    },
    "cable": {
        "parents": [{"attribute": "thing", "entity_type": "thing", "label": "Thing"}],
        "children": [],
    },
    "sensor_model": {
        "parents": [],
        "children": [{"attribute": "sensors", "entity_type": "sensor", "label": "Sensors"}],
    },
    "sensor": {
        "parents": [
            {"attribute": "project", "entity_type": "project", "label": "Project"},
            {"attribute": "sensor_model", "entity_type": "sensor_model", "label": "Sensor Model"},
        ],
        "children": [
            {"attribute": "sensor_deployments", "entity_type": "sensor_deployment", "label": "Sensor Deployments"},
        ],
    },
    "observed_property": {
        "parents": [],
        "children": [{"attribute": "channels", "entity_type": "datastream_channel", "label": "Datastream Channels"}],
    },
    "unit_of_measurement": {
        "parents": [],
        "children": [{"attribute": "channels", "entity_type": "datastream_channel", "label": "Datastream Channels"}],
    },
    "datastream": {
        "parents": [{"attribute": "sensor_deployment", "entity_type": "sensor_deployment", "label": "Sensor Deployment"}],
        "children": [
            {"attribute": "channels", "entity_type": "datastream_channel", "label": "Datastream Channels"},
            {"attribute": "variants", "entity_type": "data_variant", "label": "Data Variants"},
        ],
    },
    "datastream_channel": {
        "parents": [
            {"attribute": "datastream", "entity_type": "datastream", "label": "Datastream"},
            {"attribute": "observed_property", "entity_type": "observed_property", "label": "Observed Property"},
            {"attribute": "unit_of_measurement", "entity_type": "unit_of_measurement", "label": "Unit of Measurement"},
        ],
        "children": [],
    },
    "data_variant": {
        "parents": [{"attribute": "datastream", "entity_type": "datastream", "label": "Datastream"}],
        "children": [],
    },
}

def _entity_display_name(entity: Any) -> str:
    for attr in ("name", "label", "kind"):
        value = getattr(entity, attr, None)
        if value:
            return str(value)
    if hasattr(entity, "id"):
        return f"{entity.__class__.__name__} #{entity.id}"
    return str(entity)

def get_entity_relations(entity_type: str, entity: Any) -> tuple[dict[str, Any], list[str]]:
    relation_def = RELATION_MAP.get(entity_type, {"parents": [], "children": []})
    parents = []
    children = []

    for relation in relation_def["parents"]:
        related = getattr(entity, relation["attribute"], None)
        if related is None:
            continue
        parents.append({
            "label": relation["label"],
            "entity_type": relation["entity_type"],
            "id": related.id,
            "display": _entity_display_name(related),
        })

    for relation in relation_def["children"]:
        related = getattr(entity, relation["attribute"], None)
        if related is None:
            items = []
        elif isinstance(related, (list, tuple, set)):
            items = list(related)
        else:
            items = [related]
        children.append({
            "label": relation["label"],
            "entity_type": relation["entity_type"],
            "items": [
                {"id": child.id, "display": _entity_display_name(child)}
                for child in items
            ],
            "count": len(items),
        })

    relation_keys = {
        relation["attribute"]
        for relation in relation_def["parents"] + relation_def["children"]
    }
    return {"parents": parents, "children": children}, sorted(relation_keys)

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

def list_mappable_entities():
    """Returns a list of (id, label) for all supported entities."""
    return [
        ("project", "Projects"),
        ("experiment", "Experiments"),
        ("experimental_unit", "Experimental Units"),
        ("thing", "Things"),
        ("tree_species", "Tree Species"),
        ("tree", "Trees"),
        ("cable", "Cables"),
        ("sensor_model", "Sensor Models"),
        ("sensor", "Sensors"),
        ("observed_property", "Observed Properties"),
        ("unit_of_measurement", "Units of Measurement"),
        ("datastream", "Datastreams"),
        ("run", "Runs"),
        ("location", "Locations")
    ]

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
