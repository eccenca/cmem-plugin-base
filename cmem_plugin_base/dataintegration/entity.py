"""Instance of any given concept."""
from typing import Sequence, Iterator, Optional


class EntityPath:
    """A path in a schema.

    :param is_relation: If true, values for this path must only contain URIs that
    point to a sub entity.
    :param is_single_value If true, a single value is expected and supporting datasets
    will not use arrays etc. For instance, in XML, attributes will be used instead of
    nested elements.
    """

    def __init__(self, path: str,
                 is_relation: bool = False,
                 is_single_value: bool = False) -> None:
        self.path = path
        self.is_relation = is_relation
        self.is_single_value = is_single_value

    def __repr__(self):
        obj = {
            'path': self.path, 'is_relation': self.is_relation,
            'is_single_value': self.is_single_value
        }
        return f"EntityPath({obj})"

    def __eq__(self, other):
        return (isinstance(other, EntityPath)
                and self.path == other.path
                and self.is_relation == other.is_relation
                and self.is_single_value == other.is_single_value)


class EntitySchema:
    """An entity schema.

    :param type_uri: The entity type
    :param paths: Ordered list of paths
    :param path_to_root: Specifies a path which defines where this schema is located
    in the schema tree
    :param sub_schemata: Nested entity schemata
    """

    def __init__(self,
                 type_uri: str,
                 paths: Sequence[EntityPath],
                 path_to_root: EntityPath = EntityPath(""),
                 sub_schemata: Optional[Sequence['EntitySchema']] = None) -> None:
        self.type_uri = type_uri
        self.paths = paths
        self.path_to_root = path_to_root
        self.sub_schemata = sub_schemata

    def __repr__(self):
        obj = {
            "type_uri": self.type_uri, "paths": self.paths,
            "path_to_root": self.path_to_root
        }
        return f"EntitySchema({obj})"

    def __eq__(self, other):
        return (isinstance(other, EntitySchema)
                and self.type_uri == other.type_uri
                and self.paths == other.paths
                and self.path_to_root == other.path_to_root
                and self.sub_schemata == other.sub_schemata)


class Entity:
    """An Entity can represent an instance of any given concept.

    :param uri: The URI of this entity
    :param values: All values of this entity. Contains a sequence of values for
        each path in the schema.

    TODO: uri generation
    """

    def __init__(self, uri: str, values: Sequence[Sequence[str]]) -> None:
        self.uri = uri
        self.values = values


class Entities:
    """Holds a collection of entities and their schema.

    :param entities: An iterable collection of entities. May be very large, so it
        should be iterated over and not loaded into memory at once.
    :param schema: All entities conform to this entity schema.
    :param sub_entities Additional entity collections.
    """

    def __init__(self,
                 entities: Iterator[Entity],
                 schema: EntitySchema,
                 sub_entities: Optional[Sequence['Entities']] = None) -> None:
        self.entities = entities
        self.schema = schema
        self.sub_entities = sub_entities
