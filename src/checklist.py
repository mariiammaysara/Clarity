"""
Clarity - Checklist Loader and Validator.

This module is responsible for loading, validating, and structuring clinical
documentation checklists from data/checklists.json. It ensures type integrity
and validates condition availability without any text-processing logic.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

# Default path to the clinical checklists JSON file
CHECKLISTS_PATH = Path(__file__).parent.parent / "data" / "checklists.json"

VALID_PRIORITIES = {"HIGH", "MEDIUM"}


@dataclass
class ChecklistField:
    """Represents a single clinical documentation field checklist item.

    Attributes:
        field_name: Unique identifier for the field in snake_case (e.g., 'vital_signs').
        display_name: Human-readable title suitable for report presentation.
        priority: Clinical priority tier, strictly 'HIGH' or 'MEDIUM'.
        keywords: Clinical terms, variations, and abbreviations indicating documentation.
        rationale: Clinical justification explaining the risk or impact if omitted.
        guideline_ref: Medical society guideline or reference publication name and year.
    """

    field_name: str
    display_name: str
    priority: str
    keywords: list[str]
    rationale: str
    guideline_ref: str

    def __post_init__(self) -> None:
        """Validates field attributes upon instantiation."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{self.priority}' for field '{self.field_name}'. "
                f"Allowed priorities are: {sorted(VALID_PRIORITIES)}"
            )


def _load_raw_data(json_path: Path = CHECKLISTS_PATH) -> dict[str, Any]:
    """Loads and returns the raw JSON dictionary from the checklists file.

    Args:
        json_path: Path to the checklists JSON file. Defaults to CHECKLISTS_PATH.

    Returns:
        A dictionary containing the parsed JSON data.

    Raises:
        FileNotFoundError: If the checklists file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"Checklists file not found at: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_conditions(json_path: Path = CHECKLISTS_PATH) -> list[str]:
    """Returns the names of all available medical conditions in the checklist dataset.

    Metadata keys (prefixed with '_', such as '_meta') are automatically excluded.

    Args:
        json_path: Optional Path to checklists file. Defaults to CHECKLISTS_PATH.

    Returns:
        A list of condition key strings (e.g., ['chest_pain', 'headache']).

    Raises:
        FileNotFoundError: If the checklists file cannot be located.
        json.JSONDecodeError: If the checklists file contains invalid JSON.
    """
    raw_data = _load_raw_data(json_path)
    return [key for key in raw_data if not key.startswith("_")]


def load_checklist(
    condition: str, json_path: Path = CHECKLISTS_PATH
) -> list[ChecklistField]:
    """Loads and validates the checklist fields for a specified medical condition.

    Args:
        condition: Key name of the clinical condition (e.g., 'chest_pain', 'headache').
        json_path: Optional custom path to the checklists file. Defaults to CHECKLISTS_PATH.

    Returns:
        A list of validated ChecklistField objects corresponding to the requested condition.

    Raises:
        ValueError: If the condition is not found in the checklists file, or if a field
            lacks required keys or has an invalid priority.
        FileNotFoundError: If the checklists file cannot be located.
        json.JSONDecodeError: If the checklists file contains invalid JSON.
    """
    raw_data = _load_raw_data(json_path)
    available_conditions = [key for key in raw_data if not key.startswith("_")]

    if condition not in raw_data or condition.startswith("_"):
        raise ValueError(
            f"Unknown condition '{condition}'. Available conditions are: {available_conditions}"
        )

    fields_data = raw_data[condition]
    if not isinstance(fields_data, list):
        raise ValueError(
            f"Expected list of fields for condition '{condition}', got {type(fields_data).__name__}"
        )

    checklist_fields: list[ChecklistField] = []
    required_keys = {
        "field_name",
        "display_name",
        "priority",
        "keywords",
        "rationale",
        "guideline_ref",
    }

    for idx, item in enumerate(fields_data):
        if not isinstance(item, dict):
            raise ValueError(
                f"Field #{idx} in condition '{condition}' must be an object/dict, got {type(item).__name__}"
            )

        missing_keys = required_keys - set(item.keys())
        if missing_keys:
            raise ValueError(
                f"Field #{idx} in condition '{condition}' is missing required keys: {sorted(missing_keys)}"
            )

        field = ChecklistField(
            field_name=item["field_name"],
            display_name=item["display_name"],
            priority=item["priority"],
            keywords=item["keywords"],
            rationale=item["rationale"],
            guideline_ref=item["guideline_ref"],
        )
        checklist_fields.append(field)

    return checklist_fields


if __name__ == "__main__":
    print("=== Testing list_conditions() ===")
    conditions = list_conditions()
    print(f"Available conditions: {conditions}\n")

    print("=== Testing load_checklist('chest_pain') ===")
    fields = load_checklist("chest_pain")
    print(f"Total fields loaded: {len(fields)}")
    print("\nFirst field details:")
    first_field = fields[0]
    print(f"  Field Name:    {first_field.field_name}")
    print(f"  Display Name:  {first_field.display_name}")
    print(f"  Priority:      {first_field.priority}")
    print(f"  Keywords:      {first_field.keywords}")
    print(f"  Rationale:     {first_field.rationale}")
    print(f"  Guideline Ref: {first_field.guideline_ref}")
