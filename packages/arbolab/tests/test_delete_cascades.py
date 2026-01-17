"""Tests for ORM delete cascades."""

from __future__ import annotations

from datetime import datetime

import pytest
from arbolab.models import (
    Base,
    Datastream,
    DatastreamChannel,
    DataVariant,
    Experiment,
    ExperimentalUnit,
    Location,
    ObservedProperty,
    Project,
    Run,
    Sensor,
    SensorDeployment,
    SensorModel,
    Thing,
    Treatment,
    TreatmentApplication,
    UnitOfMeasurement,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def session() -> Session:
    """Returns an in-memory DuckDB session for testing."""
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_delete_thing_cascades_location(session: Session) -> None:
    project = Project.create(session, name="Project")
    location = Location.create(session, name="Location")
    thing = Thing.create(session, project=project, location=location, kind="tree")
    session.flush()

    thing_id = thing.id
    location_id = location.id

    thing.delete(session)
    session.flush()

    assert session.get(Thing, thing_id) is None
    assert session.get(Location, location_id) is None


def test_delete_sensor_deployment_cascades_datastream_graph(session: Session) -> None:
    project = Project.create(session, name="Project")
    experiment = Experiment.create(session, project=project, name="Experiment")
    experimental_unit = ExperimentalUnit.create(session, project=project)
    sensor_model = SensorModel.create(session, name="Model")
    sensor = Sensor.create(session, project=project, sensor_model=sensor_model, name="Sensor")

    deployment = SensorDeployment.create(
        session,
        experiment=experiment,
        experimental_unit=experimental_unit,
        sensor=sensor,
        start_time=datetime(2024, 1, 1, 0, 0, 0),
    )
    datastream = Datastream.create(session, sensor_deployment=deployment)
    observed_property = ObservedProperty.create(session, name="Temperature")
    unit = UnitOfMeasurement.create(session, unit="C", unit_symbol="C")
    channel = DatastreamChannel.create(
        session,
        datastream=datastream,
        observed_property=observed_property,
        unit_of_measurement=unit,
        channel_index=0,
    )
    variant = DataVariant.create(session, datastream=datastream, variant_name="raw")
    session.flush()

    deployment_id = deployment.id
    datastream_id = datastream.id
    channel_id = channel.id
    variant_id = variant.id

    deployment.delete(session)
    session.flush()

    assert session.get(SensorDeployment, deployment_id) is None
    assert session.get(Datastream, datastream_id) is None
    assert session.get(DatastreamChannel, channel_id) is None
    assert session.get(DataVariant, variant_id) is None


def test_delete_thing_cascades_treatment_applications(session: Session) -> None:
    project = Project.create(session, name="Project")
    experiment = Experiment.create(
        session, project=project, name="Experiment", start_time=datetime(2024, 1, 1, 0, 0, 0)
    )
    treatment = Treatment.create(session, project=project, name="Treatment")
    thing = Thing.create(session, project=project, kind="tree")
    application = TreatmentApplication.create(
        session,
        experiment=experiment,
        treatment=treatment,
        thing=thing,
        start_time=datetime(2024, 1, 1, 0, 0, 0),
    )
    session.flush()

    thing_id = thing.id
    application_id = application.id

    thing.delete(session)
    session.flush()

    assert session.get(Thing, thing_id) is None
    assert session.get(TreatmentApplication, application_id) is None


def test_delete_sensor_cascades_deployments_and_datastreams(session: Session) -> None:
    project = Project.create(session, name="Project")
    experiment = Experiment.create(
        session, project=project, name="Experiment", start_time=datetime(2024, 1, 1, 0, 0, 0)
    )
    experimental_unit = ExperimentalUnit.create(session, project=project)
    sensor_model = SensorModel.create(session, name="Model")
    sensor = Sensor.create(session, project=project, sensor_model=sensor_model, name="Sensor")

    deployment = SensorDeployment.create(
        session,
        experiment=experiment,
        experimental_unit=experimental_unit,
        sensor=sensor,
        start_time=datetime(2024, 1, 1, 0, 0, 0),
    )
    datastream = Datastream.create(session, sensor_deployment=deployment)
    observed_property = ObservedProperty.create(session, name="Temperature")
    unit = UnitOfMeasurement.create(session, unit="C", unit_symbol="C")
    channel = DatastreamChannel.create(
        session,
        datastream=datastream,
        observed_property=observed_property,
        unit_of_measurement=unit,
        channel_index=0,
    )
    variant = DataVariant.create(session, datastream=datastream, variant_name="raw")
    session.flush()

    sensor_id = sensor.id
    deployment_id = deployment.id
    datastream_id = datastream.id
    channel_id = channel.id
    variant_id = variant.id

    sensor.delete(session)
    session.flush()

    assert session.get(Sensor, sensor_id) is None
    assert session.get(SensorDeployment, deployment_id) is None
    assert session.get(Datastream, datastream_id) is None
    assert session.get(DatastreamChannel, channel_id) is None
    assert session.get(DataVariant, variant_id) is None


def test_delete_run_detaches_sensor_deployments(session: Session) -> None:
    project = Project.create(session, name="Project")
    experiment = Experiment.create(session, project=project, name="Experiment")
    run = Run.create(session, experiment=experiment, name="Run", start_time=datetime(2024, 1, 1, 0, 0, 0))
    experimental_unit = ExperimentalUnit.create(session, project=project)
    sensor_model = SensorModel.create(session, name="Model")
    sensor = Sensor.create(session, project=project, sensor_model=sensor_model, name="Sensor")
    deployment = SensorDeployment.create(
        session,
        experiment=experiment,
        run=run,
        experimental_unit=experimental_unit,
        sensor=sensor,
        start_time=datetime(2024, 1, 1, 0, 0, 0),
    )
    session.flush()

    run_id = run.id
    deployment_id = deployment.id

    run.delete(session)
    session.flush()
    session.expire_all()

    assert session.get(Run, run_id) is None
    remaining = session.get(SensorDeployment, deployment_id)
    assert remaining is not None
    assert remaining.run_id is None
