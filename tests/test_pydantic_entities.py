"""Test Pydantic Entities"""

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.utils.pydantic_entities import PydanticEntities


class Person(BaseModel):
    """Person model"""

    name: str
    age: int = Field(gt=20)
    interests: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


PERSON_SCHEMA = EntitySchema(
    type_uri="https://example.org/Person",
    paths=[
        EntityPath(path="name"),
        EntityPath(path="age"),
        EntityPath(path="interests"),
    ],
)

PERSON_ENTITIES: dict[str, list[Entity]] = {
    "all-fields-valid": [Entity(values=[["John"], ["30"], ["swimming", "running"]])],
    "no-interest-valid": [Entity(values=[["Adam"], ["25"], []])],
    "additional-field-valid": [
        Entity(values=[["Satoshi"], ["50"], ["crypto", "blockchain"], ["unclear"]])
    ],
    "name-missing-invalid": [Entity(values=[[], ["30"], ["hacking", "D&D"]])],
    "age-gt-invalid": [Entity(values=[["Jane"], ["18"], ["dancing", "smoking"]])],
}


class PersonEntities(PydanticEntities):
    """Wrapper class to access Person Entities with pydantic."""

    _model = Person


def test_entity_uri_generation() -> None:
    """Test that Entity URI creation works."""
    john = Entity(values=[["John"], ["30"], ["swimming", "running"]])
    assert john.uri.startswith("urn:")
    jane_uri = "https://example.org"
    jane = Entity(uri=jane_uri, values=[["Jane"], ["25"], ["dancing", "party"]])
    assert jane.uri == jane_uri


def test_entity_to_dict() -> None:
    """Test that Entity dict creation works."""
    assert PydanticEntities.entity_to_dict(
        Entity(values=[["John"], ["30"], ["swimming", "running"]]), PERSON_SCHEMA
    ) == {
        "name": "John",
        "age": "30",
        "interests": ["swimming", "running"],
    }
    assert PydanticEntities.entity_to_dict(Entity(values=[["John"], ["30"]]), PERSON_SCHEMA) == {
        "name": "John",
        "age": "30",
    }
    assert PydanticEntities.entity_to_dict(Entity(values=[["John"], [""]]), PERSON_SCHEMA) == {
        "name": "John",
        "age": "",
    }
    assert PydanticEntities.entity_to_dict(Entity(values=[["John"], []]), PERSON_SCHEMA) == {
        "name": "John",
    }


@pytest.mark.parametrize("key", [key for key in PERSON_ENTITIES if key.endswith("-valid")])
def test_valid_entities(key: str) -> None:
    """Test that Pydantic entities work."""
    entities = Entities(schema=PERSON_SCHEMA, entities=iter(PERSON_ENTITIES[key]))
    pydantic_entities = PersonEntities(entities=entities)
    person_list: list[Person] = list(pydantic_entities)
    for person in person_list:
        assert len(person.name) > 0


@pytest.mark.parametrize("key", [key for key in PERSON_ENTITIES if key.endswith("-invalid")])
def test_invalid_entities(key: str) -> None:
    """Test that Pydantic entities work with invalid entities."""
    entities = Entities(schema=PERSON_SCHEMA, entities=iter(PERSON_ENTITIES[key]))
    pydantic_entities = PersonEntities(entities=entities)
    with pytest.raises(ValidationError):
        list(pydantic_entities)
