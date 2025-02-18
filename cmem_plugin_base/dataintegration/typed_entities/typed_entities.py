"""Custom entity schema that holds entities of a specific type (e.g. files)"""

from abc import abstractmethod
from collections.abc import Iterator, Sequence
from typing import Generic, TypeVar

from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema

T = TypeVar("T")


class TypedEntitySchema(EntitySchema, Generic[T]):
    """A custom entity schema that holds entities of a specific type (e.g. files)."""

    def __init__(self, type_uri: str, paths: Sequence[EntityPath]):
        super().__init__(type_uri, paths)

    @abstractmethod
    def to_entity(self, value: T) -> Entity:
        """Create a generic entity from a typed entity."""

    @abstractmethod
    def from_entity(self, entity: Entity) -> T:
        """Create a typed entity from a generic entity.

        Implementations may assume that the incoming schema matches the schema expected by
        this typed schema, i.e., schema validation is not required.
        """

    def to_entities(self, values: Iterator[T]) -> "TypedEntities[T]":
        """Given a collection of values, create a new typed entities instance."""
        return TypedEntities(values, self)

    def from_entities(self, entities: Entities) -> "TypedEntities[T]":
        """Create typed entities from generic entities.

        Returns None if the entities do not match the target type.
        """
        # TODO(robert): add validation
        # CMEM-6095
        if entities.schema.type_uri == self.type_uri:
            if isinstance(entities, TypedEntities):
                return entities
            return TypedEntities(map(self.from_entity, entities.entities), self)
        raise ValueError(
            f"Expected entities of type '{self.type_uri}' but got '{entities.schema.type_uri}'."
        )


class TypedEntities(Entities, Generic[T]):
    """Collection of entities of a particular type."""

    def __init__(self, values: Iterator[T], schema: TypedEntitySchema[T]):
        super().__init__(map(schema.to_entity, values), schema)
        self.values = values
        self.schema = schema
