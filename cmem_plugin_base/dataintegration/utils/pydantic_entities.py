"""Convert Entities to pydantic objects

maybe an issue: https://github.com/python/typing/issues/629
"""

from abc import ABC
from collections.abc import Iterator, Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel

from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntitySchema

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


class PydanticEntities(ABC, Generic[PydanticModel]):
    """Wrapper class to access Entities with pydantic."""

    _model: PydanticModel
    _entities: Iterator[Entity]
    _schema: EntitySchema

    def __init__(self, entities: Entities) -> None:
        self._entities = entities.entities
        self._schema = entities.schema

    def __next__(self) -> PydanticModel:
        """Get next pydantic entity"""
        return self.entity_to_model(entity=next(self._entities))

    def __iter__(self) -> Iterator[PydanticModel]:
        """Iterate over pydantic entities."""
        return self

    def to_list(self) -> list[PydanticModel]:
        """Convert pydantic entities to list."""
        return [self.entity_to_model(entity=_) for _ in self._entities]

    def to_dict(self) -> dict[str, PydanticModel]:
        """Convert pydantic entities to dict."""
        return {_.uri: self.entity_to_model(entity=_) for _ in self._entities}

    def entity_to_model(self, entity: Entity) -> PydanticModel:
        """Convert an entity to a pydantic model"""
        entity_dict = self.entity_to_dict(entity=entity, schema=self._schema)
        return self._model.model_validate(entity_dict)

    @classmethod
    def values_to_dict_values(cls, values: Sequence[str] | list[str]) -> None | str | list[str]:
        """Convert list of values to dict values"""
        if isinstance(values, Sequence):
            values = list(values)
        if isinstance(values, list):
            if len(values) == 0:
                return None
            if len(values) == 1:
                return values[0]
            return values
        raise ValueError("Values must be a sequence or list of str")

    @classmethod
    def entity_to_dict(
        cls, entity: Entity, schema: EntitySchema
    ) -> dict[str, None | str | list[str]]:
        """Convert an entity to a dict"""
        entity_dict = {}
        all_values = dict(enumerate(entity.values))
        for number, entity_path in enumerate(schema.paths):
            path = entity_path.path
            values = all_values.get(number, [])
            dict_values = cls.values_to_dict_values(values=values)
            if dict_values is not None:
                entity_dict[path] = cls.values_to_dict_values(values=values)
        return entity_dict
