"""Instance of any given concept."""

from collections.abc import Iterator, Sequence

from pydantic import BaseModel, ConfigDict


class EntityPath(BaseModel, frozen=True):
    """A path in a schema.

    :param is_relation: If true, values for this path must only contain URIs that
    point to a sub entity.
    :param is_single_value If true, a single value is expected and supporting datasets
    will not use arrays etc. For instance, in XML, attributes will be used instead of
    nested elements.
    """

    path: str
    is_relation: bool = False
    is_single_value: bool = False


class EntitySchema(BaseModel):
    """An entity schema.

    :param type_uri: The entity type
    :param paths: Ordered list of paths
    :param path_to_root: Specifies a path which defines where this schema is located
    in the schema tree. Empty by default.
    :param sub_schemata: Nested entity schemata
    """

    type_uri: str
    paths: tuple[EntityPath, ...]
    path_to_root: EntityPath = EntityPath(path="")
    sub_schemata: tuple["EntitySchema", ...] | None = None


class Entity(BaseModel):
    """An Entity can represent an instance of any given concept.

    :param uri: The URI of this entity
    :param values: All values of this entity. Contains a sequence of values for
        each path in the schema.

    TODO: uri generation
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    uri: str
    values: Sequence[Sequence[str]]


class Entities:
    """Holds a collection of entities and their schema.

    :param entities: An iterable collection of entities. May be very large, so it
        should be iterated over and not loaded into memory at once.
    :param schema: All entities conform to this entity schema.
    :param sub_entities Additional entity collections.
    """

    def __init__(
        self,
        entities: Iterator[Entity],
        schema: EntitySchema,
        sub_entities: Sequence["Entities"] | None = None,
    ) -> None:
        self.entities = entities
        self.schema = schema
        self.sub_entities = sub_entities
