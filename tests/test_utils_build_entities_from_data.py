"""Tests for `utils.build_entities_from_data`"""

import json

from cmem_plugin_base.dataintegration.entity import Entities, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.utils.entity_builder import build_entities_from_data


def build_entities_from_json(json_data: str) -> Entities:
    """Build entities from a test JSON string."""
    data = json.loads(json_data)
    entities = build_entities_from_data(data)
    assert entities is not None
    return entities


def test_single_object() -> None:
    """Test generation of entities and schema for a simple JSON object."""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com"
}"""
    entities = build_entities_from_json(test_data)
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
        ],
    )


def test_single_object_one_level() -> None:
    """Test generation of entities and schema for a JSON object with one level of hierarchy."""
    test_data = """
{
  "name": "sai",
  "email": "saipraneeth@example.com",
  "city": {
    "name": "San Francisco",
    "country": "United States"
  }
}"""
    entities = build_entities_from_json(test_data)
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
        ],
    )
    # Validate sub entities
    assert entities.sub_entities is not None
    for _ in entities.sub_entities:
        for _entity in _.entities:
            assert len(_entity.values) == 2
            assert _entity.values == [["San Francisco"], ["United States"]]
        assert _.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_single_value=True),
                EntityPath("country", False, is_single_value=True),
            ],
        )


def test_single_object_one_level_array() -> None:
    """Test generation of entities and schema for a JSON object.

    Test with array object in first level of hierarchy.
    """
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
    entities = build_entities_from_json(test_data)
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
        ],
    )
    # Validate sub entities
    assert entities.sub_entities is not None
    for _ in entities.sub_entities:
        assert len(list(_.entities)) == 2
        for _entity in _.entities:
            assert len(_entity.values) == 2
        assert _.schema == EntitySchema(
            type_uri="",
            paths=[
                EntityPath("name", False, is_single_value=True),
                EntityPath("country", False, is_single_value=True),
            ],
        )


def test_single_object_two_level_array() -> None:
    """Test generation of entities and schema.

    Tests a JSON object with two levels of hierarchy.
    """
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
    entities = build_entities_from_json(test_data)
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
        ],
    )
    # Validate sub entities
    assert entities.sub_entities is not None
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
        ],
    )

    assert location_entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("lat", False, is_single_value=True),
            EntityPath("long", False, is_single_value=True),
        ],
    )


def test_array_object() -> None:
    """Test generation of entities and schema for a simple array JSON object."""
    test_data = """
[{
  "name": "seebi"
},
{
  "name": "sai",
  "email": "saipraneeth@example.com"
}]"""
    entities = build_entities_from_json(test_data)
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
        ],
    )


def test_empty_object() -> None:
    """Test empty json object input"""
    test_data = """[]"""
    data = json.loads(test_data)
    assert build_entities_from_data(data) is None


def test_null_object_leaves_the_relation_empty() -> None:
    """Test that an object which is null in one item does not fake a sub entity.

    A relation path carries URIs pointing at sub entities. Writing "" there hands out
    a reference that resolves to nothing, and a JSON dataset sink following it aborts
    the whole write with "Current context not Array but Object".
    """
    test_data = """
[{
  "name": "seebi",
  "address": null
},
{
  "name": "sai",
  "address": {"city": "San Francisco"}
}]"""
    entities = build_entities_from_json(test_data)
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("address", True, is_single_value=True),
        ],
    )
    without_address, with_address = list(entities.entities)
    assert without_address.values == [["seebi"], []]
    assert with_address.values[1][0].startswith("urn:x-ulid:")


def test_an_object_is_not_flattened_by_a_later_null() -> None:
    """Test that the item order does not decide whether a key is a relation.

    The same two items as above, the other way round. Reading the type off the last
    item seen made `address` a plain path, and the object in the first item was then
    written as its `str()` - `{'city': 'San Francisco'}` - instead of a sub entity.
    """
    test_data = """
[{
  "name": "sai",
  "address": {"city": "San Francisco"}
},
{
  "name": "seebi",
  "address": null
}]"""
    entities = build_entities_from_json(test_data)
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("address", True, is_single_value=True),
        ],
    )
    with_address, without_address = list(entities.entities)
    assert with_address.values[1][0].startswith("urn:x-ulid:")
    assert without_address.values == [["seebi"], []]
    assert entities.sub_entities is not None
    assert len(entities.sub_entities) == 1
    assert [_.values for _ in entities.sub_entities[0].entities] == [[["San Francisco"]]]


def test_an_empty_list_does_not_flatten_a_list_of_objects() -> None:
    """Test that a key empty in one item stays a relation because another item fills it"""
    test_data = """
[{
  "name": "sai",
  "pets": [{"name": "cat"}]
},
{
  "name": "seebi",
  "pets": []
}]"""
    entities = build_entities_from_json(test_data)
    assert entities.schema == EntitySchema(
        type_uri="",
        paths=[
            EntityPath("name", False, is_single_value=True),
            EntityPath("pets", True, is_single_value=False),
        ],
    )
    with_pets, without_pets = list(entities.entities)
    assert with_pets.values[1][0].startswith("urn:x-ulid:")
    assert without_pets.values == [["seebi"], []]
