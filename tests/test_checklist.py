"""Unit tests for the checklist loader module (src/checklist.py)."""

import pytest
from src.checklist import ChecklistField, list_conditions, load_checklist


def test_load_checklist_returns_expected_fields_count() -> None:
    """Verifies that load_checklist('chest_pain') loads the exact 10 defined clinical fields."""
    fields = load_checklist("chest_pain")
    assert isinstance(fields, list)
    assert len(fields) == 10
    assert all(isinstance(f, ChecklistField) for f in fields)


def test_load_checklist_raises_on_invalid_condition() -> None:
    """Verifies that attempting to load a non-existent condition raises a descriptive ValueError."""
    with pytest.raises(ValueError, match="Unknown condition 'nonexistent_condition'"):
        load_checklist("nonexistent_condition")


def test_list_conditions_returns_valid_conditions() -> None:
    """Verifies that list_conditions() retrieves available conditions excluding metadata."""
    conditions = list_conditions()
    assert set(conditions) == {"chest_pain", "headache"}
    assert all(not c.startswith("_") for c in conditions)
