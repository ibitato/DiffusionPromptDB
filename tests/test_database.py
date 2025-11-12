"""
Unit tests for database operations.
"""
import pytest
import tempfile
from pathlib import Path
from diffusion_prompt_db.database import Database
from diffusion_prompt_db.models import Prompt


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = Database(db_path=db_path)
    yield db
    db.close()
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


def test_database_initialization(temp_db):
    """Test database initialization."""
    assert temp_db.connection is not None
    assert temp_db.db_path.exists()


def test_add_prompt(temp_db):
    """Test adding a prompt."""
    prompt = Prompt(
        text="A beautiful landscape",
        model="stable-diffusion-v1",
        category="landscape",
        rating=5
    )
    
    prompt_id = temp_db.add_prompt(prompt)
    assert prompt_id > 0


def test_get_prompt(temp_db):
    """Test retrieving a prompt."""
    prompt = Prompt(
        text="A beautiful sunset",
        negative_prompt="ugly, blurry",
        model="stable-diffusion-v1"
    )
    
    prompt_id = temp_db.add_prompt(prompt)
    retrieved = temp_db.get_prompt(prompt_id)
    
    assert retrieved is not None
    assert retrieved.text == "A beautiful sunset"
    assert retrieved.negative_prompt == "ugly, blurry"
    assert retrieved.model == "stable-diffusion-v1"


def test_get_all_prompts(temp_db):
    """Test retrieving all prompts."""
    prompts = [
        Prompt(text="Prompt 1", category="test"),
        Prompt(text="Prompt 2", category="test"),
        Prompt(text="Prompt 3", category="test")
    ]
    
    for prompt in prompts:
        temp_db.add_prompt(prompt)
    
    all_prompts = temp_db.get_all_prompts()
    assert len(all_prompts) == 3


def test_search_prompts(temp_db):
    """Test searching prompts."""
    prompts = [
        Prompt(text="Beautiful landscape", category="landscape", rating=5),
        Prompt(text="City skyline", category="urban", rating=4),
        Prompt(text="Mountain view", category="landscape", rating=5)
    ]
    
    for prompt in prompts:
        temp_db.add_prompt(prompt)
    
    # Search by category
    landscape_prompts = temp_db.search_prompts(category="landscape")
    assert len(landscape_prompts) == 2
    
    # Search by text
    city_prompts = temp_db.search_prompts(text="city")
    assert len(city_prompts) == 1
    
    # Search by minimum rating
    high_rated = temp_db.search_prompts(min_rating=5)
    assert len(high_rated) == 2


def test_update_prompt(temp_db):
    """Test updating a prompt."""
    prompt = Prompt(text="Original text", rating=3)
    prompt_id = temp_db.add_prompt(prompt)
    
    updated_prompt = Prompt(text="Updated text", rating=5)
    success = temp_db.update_prompt(prompt_id, updated_prompt)
    
    assert success
    
    retrieved = temp_db.get_prompt(prompt_id)
    assert retrieved.text == "Updated text"
    assert retrieved.rating == 5


def test_delete_prompt(temp_db):
    """Test deleting a prompt."""
    prompt = Prompt(text="To be deleted")
    prompt_id = temp_db.add_prompt(prompt)
    
    success = temp_db.delete_prompt(prompt_id)
    assert success
    
    retrieved = temp_db.get_prompt(prompt_id)
    assert retrieved is None


def test_prompt_validation():
    """Test prompt model validation."""
    # Valid rating
    prompt = Prompt(text="Test", rating=3)
    assert prompt.rating == 3
    
    # Invalid rating
    with pytest.raises(ValueError):
        Prompt(text="Test", rating=6)
    
    with pytest.raises(ValueError):
        Prompt(text="Test", rating=0)
