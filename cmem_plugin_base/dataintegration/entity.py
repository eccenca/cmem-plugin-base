"""Instance of any given concept."""
from typing import Sequence, Iterator, Optional


class EntityPath:
    """A path in a schema.

    :param path: The path string using the Silk path language.
    :param is_uri: If true, values for this path must only contain URIs that point to
    a sub entity.
    """

    def __init__(self, path: str, is_uri: bool = False) -> None:
        self.path = path
        self.is_uri = is_uri


class EntitySchema:
    """An entity schema.

    :param type_uri: The entity type
    :param paths: Ordered list of paths
    :param sub_path: Path in relation to the parent schema or from the root if
                     there is no parent
    :param sub_schemata: Nested entity schemata.
    """

    def __init__(self,
                 type_uri: str,
                 paths: Sequence[EntityPath],
                 sub_path: EntityPath = EntityPath(""),
                 sub_schemata: Optional[Sequence['EntitySchema']] = None) -> None:
        self.type_uri = type_uri
        self.paths = paths
        self.sub_path = sub_path
        self.sub_schemata = sub_schemata


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
