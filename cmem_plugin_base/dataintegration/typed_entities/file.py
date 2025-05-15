"""File entities"""

from cmem_plugin_base.dataintegration.entity import Entity, EntityPath
from cmem_plugin_base.dataintegration.typed_entities import instance_uri, path_uri, type_uri
from cmem_plugin_base.dataintegration.typed_entities.typed_entities import (
    TypedEntitySchema,
)


class File:
    """A file entity that can be held in a FileEntitySchema."""

    def __init__(self, path: str, file_type: str, mime: str | None) -> None:
        self.path = path
        self.file_type = file_type
        self.mime = mime


class LocalFile(File):
    """A file that's located on the local file system."""

    def __init__(self, path: str, mime: str | None = None) -> None:
        super().__init__(path, "Local", mime)


class ProjectFile(File):
    """A project file"""

    def __init__(self, path: str, mime: str | None = None) -> None:
        super().__init__(path, "Project", mime)


class FileEntitySchema(TypedEntitySchema[File]):
    """Entity schema that holds a collection of files."""

    def __init__(self):
        super().__init__(
            type_uri=type_uri("File"),
            paths=[
                EntityPath(path_uri("filePath"), is_single_value=True),
                EntityPath(path_uri("fileType"), is_single_value=True),
                EntityPath(path_uri("mimeType"), is_single_value=True),
            ],
        )

    def to_entity(self, value: File) -> Entity:
        """Create a generic entity from a file"""
        return Entity(
            uri=instance_uri(value.path),
            values=[[value.path], [value.file_type], [value.mime] if value.mime else []],
        )

    def from_entity(self, entity: Entity) -> File:
        """Create a file entity from a generic entity."""
        path = entity.values[0][0]
        file_type = entity.values[1][0]
        mime = entity.values[2][0] if entity.values[2] and entity.values[2][0] else None
        match file_type:
            case "Local":
                return LocalFile(path, mime)
            case "Project":
                return ProjectFile(path, mime)
            case _:
                raise ValueError(f"File '{path}' has unexpected type '{file_type}'.")
