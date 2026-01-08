"""Tests for core SQLAlchemy models and Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from arbolab.models import (
    Base,
    Datastream,
    DatastreamChannel,
    DataVariant,
    Experiment,
    ExperimentalUnit,
    ObservedProperty,
    Project,
    Sensor,
    SensorDeployment,
    SensorModel,
    Thing,
    Treatment,
    TreatmentApplication,
    Tree,
    TreeSpecies,
    UnitOfMeasurement,
)
from arbolab.schemas.core import DataVariantSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def test_core_schema_creates_and_roundtrips() -> None:
    """Creates the core schema in DuckDB and validates a minimal roundtrip."""

    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        project = Project(name="P1")
        session.add(project)
        session.flush()

        experiment = Experiment(project_id=project.id, name="E1")
        session.add(experiment)

        sensor_model = SensorModel(name="SM1")
        session.add(sensor_model)
        session.flush()

        sensor = Sensor(project_id=project.id, sensor_model_id=sensor_model.id, name="S1")
        session.add(sensor)

        thing = Thing(project_id=project.id, kind="tree", name="T1")
        session.add(thing)
        session.flush()

        species = TreeSpecies(name="Acer")
        session.add(species)
        session.flush()

        tree = Tree(id=thing.id, species_id=species.id)
        session.add(tree)

        experimental_unit = ExperimentalUnit(project_id=project.id, thing_id=thing.id, name="EU1")
        session.add(experimental_unit)
        session.flush()

        deployment = SensorDeployment(
            experiment_id=experiment.id,
            experimental_unit_id=experimental_unit.id,
            sensor_id=sensor.id,
            start_time=datetime(2026, 1, 1),
        )
        session.add(deployment)
        session.flush()

        datastream = Datastream(sensor_deployment_id=deployment.id, name="DS1")
        session.add(datastream)
        session.flush()

        observed_property = ObservedProperty(name="acceleration_x")
        session.add(observed_property)
        session.flush()

        unit = UnitOfMeasurement(name="meter per second squared", unit="m/s^2", unit_symbol="m/s²")
        session.add(unit)
        session.flush()

        channel = DatastreamChannel(
            datastream_id=datastream.id,
            observed_property_id=observed_property.id,
            unit_of_measurement_id=unit.id,
            channel_index=0,
            name="x",
        )
        session.add(channel)

        treatment = Treatment(project_id=project.id, name="baseline")
        session.add(treatment)
        session.flush()

        session.add(
            TreatmentApplication(
                experiment_id=experiment.id,
                treatment_id=treatment.id,
                thing_id=thing.id,
                start_time=datetime(2026, 1, 1),
            )
        )

        session.add(
            DataVariant(
                datastream_id=datastream.id,
                variant_name="raw",
                column_specs=[
                    {
                        "name": "timestamp",
                        "dtype": "timestamp[ns]",
                        "description": "Observation timestamp.",
                    }
                ],
                data_files=["data.parquet"],
            )
        )

        session.commit()

        variant = session.query(DataVariant).one()
        parsed = DataVariantSchema.model_validate(variant)
        assert parsed.variant_name == "raw"
        assert parsed.column_specs is not None
        assert parsed.column_specs[0].name == "timestamp"
