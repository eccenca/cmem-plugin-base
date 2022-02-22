"""Instance of any given concept."""
from typing import Sequence, Iterator


class EntityPath:
    """A path in a schema.

    :param path: The path string using the Silk path language.
    """

    def __init__(self, path: str) -> None:
        self.path = path


class EntitySchema:
    """An entity schema.

    :param type_uri: The entity type
    :param paths: Ordered list of paths
    """

    def __init__(self, type_uri: str, paths: Sequence[EntityPath]) -> None:
        self.type_uri = type_uri
        self.paths = paths


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
    """

    def __init__(self, entities: Iterator[Entity], schema: EntitySchema) -> None:
        self.entities = entities
        self.schema = schema
