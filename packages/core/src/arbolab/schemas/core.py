"""Core Pydantic schemas for the ArboLab domain model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from arbolab.schemas.base import EntitySchema


class ProjectSchema(EntitySchema):
    """Schema for a Project record."""


class ExperimentSchema(EntitySchema):
    """Schema for an Experiment record."""

    project_id: int


class ExperimentalUnitSchema(EntitySchema):
    """Schema for an ExperimentalUnit record."""

    project_id: int
    thing_id: int | None = None


class TreatmentSchema(EntitySchema):
    """Schema for a Treatment record."""

    project_id: int


class TreatmentApplicationSchema(EntitySchema):
    """Schema for a TreatmentApplication record."""

    experiment_id: int
    treatment_id: int
    thing_id: int
    start_time: datetime
    end_time: datetime | None = None


class RunSchema(EntitySchema):
    """Schema for a Run record."""

    experiment_id: int
    start_time: datetime
    end_time: datetime | None = None


class SensorDeploymentSchema(EntitySchema):
    """Schema for a SensorDeployment record."""

    experiment_id: int
    experimental_unit_id: int
    sensor_id: int
    start_time: datetime
    end_time: datetime | None = None


class LocationSchema(EntitySchema):
    """Schema for a Location record."""


class ThingSchema(EntitySchema):
    """Schema for a Thing record."""

    project_id: int
    location_id: int | None = None
    kind: str


class TreeSpeciesSchema(EntitySchema):
    """Schema for a TreeSpecies record."""


class TreeSchema(EntitySchema):
    """Schema for a Tree record (Thing subtype)."""

    id: int
    species_id: int | None = None


class CableSchema(EntitySchema):
    """Schema for a Cable record (Thing subtype)."""

    id: int


class SensorModelSchema(EntitySchema):
    """Schema for a SensorModel record."""


class SensorSchema(EntitySchema):
    """Schema for a Sensor record."""

    project_id: int
    sensor_model_id: int


class ObservedPropertySchema(EntitySchema):
    """Schema for an ObservedProperty record."""


class UnitOfMeasurementSchema(EntitySchema):
    """Schema for a UnitOfMeasurement record."""

    unit: str | None = None
    unit_symbol: str | None = None


class DatastreamSchema(EntitySchema):
    """Schema for a Datastream record."""

    sensor_deployment_id: int


class DatastreamChannelSchema(EntitySchema):
    """Schema for a DatastreamChannel record."""

    datastream_id: int
    observed_property_id: int
    unit_of_measurement_id: int
    channel_index: int


class ColumnSpec(BaseModel):
    """Machine-readable metadata describing a dataset column."""

    name: str
    dtype: str
    description: str

    raw_name: str | None = None

    label: str | None = None
    labels: dict[str, str] | None = None
    symbol: str | None = None
    symbol_latex: str | None = None
    tags: list[str] | None = None

    unit: str | None = None
    unit_symbol: str | None = None
    unit_siunitx: str | None = None
    unit_name: str | None = None
    unit_definition: str | None = None


class DataVariantSchema(EntitySchema):
    """Schema for a DataVariant record."""

    datastream_id: int
    variant_name: str

    format: str = "wide"
    data_format: str = "parquet"
    time_column: str = "timestamp"

    column_specs: list[ColumnSpec] | None = None
    data_path: str | None = None
    data_files: list[str] | None = None

    row_count: int | None = None
    column_count: int | None = None
    file_size_bytes: int | None = None
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
