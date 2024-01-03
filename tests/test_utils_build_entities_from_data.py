"""Tests for `utils.build_entities_from_data`"""
import json

from cmem_plugin_base.dataintegration.entity import EntitySchema, EntityPath
from cmem_plugin_base.dataintegration.utils.entity_builder import build_entities_from_data


def test_single_object():
    """test generation of entities and schema for a simple JSON object."""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com"
}"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    assert len(list(entities.entities)) == 1
    for _ in entities.entities:
        assert len(_.values) == 2
        assert _.values == [["sai"], ["saipraneeth@example.com"]]
    assert len(entities.schema.paths) == 2
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("email", False, is_single_value=True),
        ]
    )


def test_single_object_one_level():
    """test generation of entities and schema for a JSON object with one level of
    hierarchy"""
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
    assert len(list(entities.entities)) == 1
    for _ in entities.entities:
        assert len(_.values) == 3
        assert _.values[0:2] == [["sai"], ["saipraneeth@example.com"]]
        assert _.values[2][0].startswith("urn:x-ulid:")
    assert len(entities.schema.paths) == 3
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("email", False, is_single_value=True),
            EntityPath("city", True, is_single_value=True),
        ]
    )
    # Validate sub entities
    for _ in entities.sub_entities:
        for _entity in _.entities:
            assert len(_entity.values) == 2
            assert _entity.values == [["San Francisco"], ["United States"]]
        assert _.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_single_value=True),
                EntityPath("country", False, is_single_value=True)
            ]
        )


def test_single_object_one_level_array():
    """test generation of entities and schema for a JSON object with array object in
     first level of hierarchy"""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com",
  "city": [{
    "name": "San Francisco",
    "country": "United States"
  },
  {
    "name": "New York",
    "country": "United States"
  }]
}"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    assert len(list(entities.entities)) == 1
    for _ in entities.entities:
        assert len(_.values) == 3
        assert _.values[0:2] == [["sai"], ["saipraneeth@example.com"]]
        assert _.values[2][0].startswith("urn:x-ulid:")
    assert len(entities.schema.paths) == 3
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("email", False, is_single_value=True),
            EntityPath("city", True, is_single_value=False),
        ]
    )
    # Validate sub entities
    for _ in entities.sub_entities:
        assert len(list(_.entities)) == 2
        for _entity in _.entities:
            assert len(_entity.values) == 2
        assert _.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_single_value=True),
                EntityPath("country", False, is_single_value=True)
            ]
        )


def test_single_object_two_level_array():
    """test generation of entities and schema for a JSON object with two levels of
    hierarchy"""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com",
  "city": [
    {
      "name": "San Francisco",
      "country": "United States",
      "geo_location": {
        "lat": "37.773972",
        "long": "-122.431297"
      }
    },
    {
      "name": "New York",
      "country": "United States",
      "geo_location": {
        "lat": "40.730610",
        "long": "-73.935242"
      }
    }
  ]
}"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    assert len(list(entities.entities)) == 1
    for _ in entities.entities:
        assert len(_.values) == 3
        assert _.values[0:2] == [["sai"], ["saipraneeth@example.com"]]
        assert _.values[2][0].startswith("urn:x-ulid:")
    assert len(entities.schema.paths) == 3
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("email", False, is_single_value=True),
            EntityPath("city", True, is_single_value=False),
        ]
    )
    # Validate sub entities
    location_entities = entities.sub_entities[0]
    city_entities = entities.sub_entities[1]
    assert len(list(city_entities.entities)) == 2
    assert len(list(location_entities.entities)) == 2

    assert city_entities.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_single_value=True),
                EntityPath("country", False, is_single_value=True),
                EntityPath("geo_location", True, is_single_value=True),
            ]
        )

    assert location_entities.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("lat", False, is_single_value=True),
                EntityPath("long", False, is_single_value=True),
            ]
        )


def test_array_object():
    """test generation of entities and schema for a simple array JSON object."""
    test_data = """
[{
  "name": "seebi"
},
{
  "name": "sai",
  "email": "saipraneeth@example.com"
}]"""
    data = json.loads(test_data)
    entities = build_entities_from_data(data)
    _ = next(entities.entities)
    assert len(_.values) == 2
    assert _.values == [["seebi"], [""]]
    _ = next(entities.entities)
    assert len(_.values) == 2
    assert _.values == [["sai"], ["saipraneeth@example.com"]]
    assert len(entities.schema.paths) == 2
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("email", False, is_single_value=True),
        ]
    )


def test_empty_object():
    """test empty json object input"""
    test_data = """[]"""
    data = json.loads(test_data)
    assert build_entities_from_data(data) is None
