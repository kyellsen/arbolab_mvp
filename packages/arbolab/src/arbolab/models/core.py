"""Core domain persistence models.

These SQLAlchemy models implement the canonical workspace schema described in:
- `docs/specs/data-model.md`
- `docs/specs/data-model-diagram.md`
- `docs/architecture/storage-format.md` (DataVariant fields)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from arbolab.models.base import Base, DescribedMixin, IdMixin, PropertiesMixin, TimestampMixin


class Project(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A long-lived research context grouping experiments, assets, and metadata."""

    __tablename__ = "projects"

    experiments: Mapped[list[Experiment]] = relationship(back_populates="project", cascade="all, delete-orphan")
    experimental_units: Mapped[list[ExperimentalUnit]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    treatments: Mapped[list[Treatment]] = relationship(back_populates="project", cascade="all, delete-orphan")
    things: Mapped[list[Thing]] = relationship(back_populates="project", cascade="all, delete-orphan")
    sensors: Mapped[list[Sensor]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Experiment(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A time-bounded measurement campaign within a Project."""

    __tablename__ = "experiments"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="experiments")
    runs: Mapped[list[Run]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    sensor_deployments: Mapped[list[SensorDeployment]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )
    treatment_applications: Mapped[list[TreatmentApplication]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentalUnit(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A conceptual unit of analysis, optionally referencing a Thing."""

    __tablename__ = "experimental_units"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    thing_id: Mapped[int | None] = mapped_column(ForeignKey("things.id"), nullable=True, index=True)

    project: Mapped[Project] = relationship(back_populates="experimental_units")
    thing: Mapped[Thing | None] = relationship(back_populates="experimental_units")
    sensor_deployments: Mapped[list[SensorDeployment]] = relationship(
        back_populates="experimental_unit", cascade="all, delete-orphan"
    )


class Treatment(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """An abstract, project-scoped experimental condition definition."""

    __tablename__ = "treatments"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="treatments")
    applications: Mapped[list[TreatmentApplication]] = relationship(
        back_populates="treatment", cascade="all, delete-orphan"
    )


class TreatmentApplication(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A concrete, time-bounded application of a Treatment to a Thing."""

    __tablename__ = "treatment_applications"

    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), nullable=False, index=True)
    treatment_id: Mapped[int] = mapped_column(ForeignKey("treatments.id"), nullable=False, index=True)
    thing_id: Mapped[int] = mapped_column(ForeignKey("things.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[Experiment] = relationship(back_populates="treatment_applications")
    treatment: Mapped[Treatment] = relationship(back_populates="applications")
    thing: Mapped[Thing] = relationship(back_populates="treatment_applications")


class Run(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A concrete execution interval within an Experiment."""

    __tablename__ = "runs"

    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[Experiment] = relationship(back_populates="runs")


class SensorDeployment(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A time-bounded record describing how a Sensor is installed on a Thing."""

    __tablename__ = "sensor_deployments"

    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), nullable=False, index=True)
    experimental_unit_id: Mapped[int] = mapped_column(
        ForeignKey("experimental_units.id"), nullable=False, index=True
    )
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[Experiment] = relationship(back_populates="sensor_deployments")
    experimental_unit: Mapped[ExperimentalUnit] = relationship(back_populates="sensor_deployments")
    sensor: Mapped[Sensor] = relationship(back_populates="sensor_deployments")
    datastreams: Mapped[list[Datastream]] = relationship(back_populates="sensor_deployment")


class Location(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A current spatial description associated with a Thing."""

    __tablename__ = "locations"

    things: Mapped[list[Thing]] = relationship(back_populates="location")


class Thing(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A persistent real-world object of interest (tree, cable, component, ...)."""

    __tablename__ = "things"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String, nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="things")
    location: Mapped[Location | None] = relationship(back_populates="things")
    experimental_units: Mapped[list[ExperimentalUnit]] = relationship(back_populates="thing")
    treatment_applications: Mapped[list[TreatmentApplication]] = relationship(back_populates="thing")
    tree: Mapped[Tree | None] = relationship(back_populates="thing", uselist=False, cascade="all, delete-orphan")
    cable: Mapped[Cable | None] = relationship(back_populates="thing", uselist=False, cascade="all, delete-orphan")


class TreeSpecies(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A reusable classification describing the species of a Tree."""

    __tablename__ = "tree_species"

    trees: Mapped[list[Tree]] = relationship(back_populates="species")


class Tree(Base, TimestampMixin, PropertiesMixin):
    """Thing subtype representing a tree."""

    __tablename__ = "trees"

    id: Mapped[int] = mapped_column(ForeignKey("things.id"), primary_key=True)
    species_id: Mapped[int | None] = mapped_column(ForeignKey("tree_species.id"), nullable=True, index=True)

    thing: Mapped[Thing] = relationship(back_populates="tree")
    species: Mapped[TreeSpecies | None] = relationship(back_populates="trees")


class Cable(Base, TimestampMixin, PropertiesMixin):
    """Thing subtype representing a cable system or cable component."""

    __tablename__ = "cables"

    id: Mapped[int] = mapped_column(ForeignKey("things.id"), primary_key=True)

    thing: Mapped[Thing] = relationship(back_populates="cable")


class SensorModel(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """Reusable metadata describing a sensor type and its measurement capabilities."""

    __tablename__ = "sensor_models"

    sensors: Mapped[list[Sensor]] = relationship(back_populates="sensor_model")


class Sensor(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A concrete physical sensor device."""

    __tablename__ = "sensors"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    sensor_model_id: Mapped[int] = mapped_column(ForeignKey("sensor_models.id"), nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="sensors")
    sensor_model: Mapped[SensorModel] = relationship(back_populates="sensors")
    sensor_deployments: Mapped[list[SensorDeployment]] = relationship(back_populates="sensor")


class ObservedProperty(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """Definition of what is measured, independent of sensor and unit."""

    __tablename__ = "observed_properties"

    channels: Mapped[list[DatastreamChannel]] = relationship(back_populates="observed_property")


class UnitOfMeasurement(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """Definition of how values are represented numerically."""

    __tablename__ = "units_of_measurement"

    unit: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    unit_symbol: Mapped[str | None] = mapped_column(String, nullable=True)

    channels: Mapped[list[DatastreamChannel]] = relationship(back_populates="unit_of_measurement")


class Datastream(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A logical container for time-ordered observations produced by one deployment."""

    __tablename__ = "datastreams"

    sensor_deployment_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_deployments.id"), nullable=False, index=True
    )

    sensor_deployment: Mapped[SensorDeployment] = relationship(back_populates="datastreams")
    channels: Mapped[list[DatastreamChannel]] = relationship(
        back_populates="datastream", cascade="all, delete-orphan"
    )
    variants: Mapped[list[DataVariant]] = relationship(back_populates="datastream", cascade="all, delete-orphan")


class DatastreamChannel(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """A single measurement channel binding property and unit to a channel index."""

    __tablename__ = "datastream_channels"
    __table_args__ = (UniqueConstraint("datastream_id", "channel_index", name="uq_datastream_channel_index"),)

    datastream_id: Mapped[int] = mapped_column(ForeignKey("datastreams.id"), nullable=False, index=True)
    observed_property_id: Mapped[int] = mapped_column(
        ForeignKey("observed_properties.id"), nullable=False, index=True
    )
    unit_of_measurement_id: Mapped[int] = mapped_column(
        ForeignKey("units_of_measurement.id"), nullable=False, index=True
    )
    channel_index: Mapped[int] = mapped_column(Integer, nullable=False)

    datastream: Mapped[Datastream] = relationship(back_populates="channels")
    observed_property: Mapped[ObservedProperty] = relationship(back_populates="channels")
    unit_of_measurement: Mapped[UnitOfMeasurement] = relationship(back_populates="channels")


class DataVariant(Base, IdMixin, TimestampMixin, DescribedMixin, PropertiesMixin):
    """Metadata describing an immutable persisted variant of a Datastream."""

    __tablename__ = "data_variants"
    __table_args__ = (UniqueConstraint("datastream_id", "variant_name", name="uq_datastream_variant_name"),)

    datastream_id: Mapped[int] = mapped_column(ForeignKey("datastreams.id"), nullable=False, index=True)
    variant_name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    format: Mapped[str] = mapped_column(String, nullable=False, server_default="wide")
    data_format: Mapped[str] = mapped_column(String, nullable=False, server_default="parquet")
    time_column: Mapped[str] = mapped_column(String, nullable=False, server_default="timestamp")

    column_specs: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    data_path: Mapped[str | None] = mapped_column(String, nullable=True)
    data_files: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    first_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    datastream: Mapped[Datastream] = relationship(back_populates="variants")

