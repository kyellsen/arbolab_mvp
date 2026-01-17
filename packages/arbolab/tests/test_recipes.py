
import pytest
from arbolab.core.recipes.executor import RecipeExecutor
from arbolab.core.recipes.transpiler import RecipeTranspiler
from arbolab.lab import Lab
from arbolab.models.core import Project


@pytest.fixture
def lab(tmp_path):
    """Returns a Lab instance in a temporary directory."""
    return Lab.open(workspace_root=tmp_path)

def test_recipe_execution_creates_entity(lab):
    # 1. Execute define_project step
    params = {"name": "Test Project", "description": "A test project"}
    project = lab.define_project(**params)
    
    assert project.id is not None
    assert project.name == "Test Project"
    
    # 2. Verify DB state
    with lab.database.session() as session:
        from sqlalchemy import select
        db_project = session.execute(select(Project).where(Project.id == project.id)).scalars().first()
        assert db_project is not None
        assert db_project.name == "Test Project"

def test_recipe_idempotency(lab):
    # 1. First call
    p1 = lab.define_project(name="Unique Project")
    
    # 2. Second call with same name
    p2 = lab.define_project(name="Unique Project")
    
    # 3. Should return the same object (idempotency by name)
    assert p1.id == p2.id
    
    with lab.database.session() as session:
        from sqlalchemy import func
        count = session.query(func.count(Project.id)).scalar()
        assert count == 1

def test_recipe_transpilation(lab):
    # 1. Record some steps
    project = lab.define_project(name="Alpha")
    lab.define_sensor(name="Sensor1", sensor_model_id=1, project_id=project.id)
    
    # 2. Load recipe and transpile
    recipe = RecipeExecutor.load_recipe(lab)
    code = RecipeTranspiler.to_python(recipe)
    
    assert "import arbolab.core as arbo" in code
    assert "lab.define_project(name='Alpha')" in code
    assert "lab.define_sensor(name='Sensor1', sensor_model_id=1, project_id=1)" in code

def test_lab_getattr_dispatch(lab):
    # Verify that __getattr__ works for mapped models
    # define_tree_species
    species = lab.define_tree_species(name="Quercus robur")
    assert species.id is not None
    assert species.name == "Quercus robur"
