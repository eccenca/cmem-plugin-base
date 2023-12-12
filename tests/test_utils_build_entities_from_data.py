"""Tests for `utils.build_entities_from_data`"""
import json

from cmem_plugin_base.dataintegration.entity import EntitySchema, EntityPath
from cmem_plugin_base.dataintegration.utils import build_entities_from_data


def test_single_object():
    """test write to single object"""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com"
}"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    assert len(entities.entities) == 1
    for _ in entities.entities:
        assert len(_.values) == 2
        assert _.values == [["sai"], ["saipraneeth@example.com"]]
    assert len(entities.schema.paths) == 2
    assert str(entities.schema) == str(EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_attribute=True),
            EntityPath("email", False, is_attribute=True),
        ]
    ))


def test_single_object_one_level():
    """test write to single object"""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com",
  "city": {
    "name": "San Francisco",
    "country": "United States"
  }
}"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    assert len(entities.entities) == 1
    for _ in entities.entities:
        assert len(_.values) == 3
        assert _.values[0:2] == [["sai"], ["saipraneeth@example.com"]]
        assert _.values[2][0].startswith("urn:x-ulid:")
    assert len(entities.schema.paths) == 3
    assert str(entities.schema) == str(EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_attribute=True),
            EntityPath("email", False, is_attribute=True),
            EntityPath("city", True, is_attribute=True),
        ]
    ))
    # Validate sub entities
    for _ in entities.sub_entities:
        for _entity in _.entities:
            assert len(_entity.values) == 2
            assert _entity.values == [["San Francisco"], ["United States"]]
        assert str(_.schema) == str(EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_attribute=True),
                EntityPath("country", False, is_attribute=True)
            ]
        ))
