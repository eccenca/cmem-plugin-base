"""File entities"""

import zipfile
from abc import abstractmethod
from io import BytesIO
from pathlib import Path
from typing import IO

from cmem.cmempy.workspace.projects.resources.resource import get_resource_response

from cmem_plugin_base.dataintegration.entity import Entity, EntityPath
from cmem_plugin_base.dataintegration.typed_entities import instance_uri, path_uri, type_uri
from cmem_plugin_base.dataintegration.typed_entities.typed_entities import (
    TypedEntitySchema,
)


class File:
    """A file entity that can be held in a FileEntitySchema.

    :param path: The file path.
    :param file_type: The type of the file (one of: "Local", "Project").
    :param mime: The MIME type of the file, if known.
    :param entry_path: If the file path points to a archive, the entry within the archive.
    """

    def __init__(self, path: str, file_type: str, mime: str | None, entry_path: str | None) -> None:
        self.path = path
        self.file_type = file_type
        self.mime = mime
        self.entry_path = entry_path

    @abstractmethod
    def read_stream(self, project_id: str) -> IO[bytes]:
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.
        """


class LocalFile(File):
    """A file that's located on the local file system."""

    def __init__(self, path: str, mime: str | None = None, entry_path: str | None = None) -> None:
        super().__init__(path, "Local", mime, entry_path)

    def read_stream(self, project_id: str) -> IO[bytes]:
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.
        """
        if self.entry_path:
            archive = zipfile.ZipFile(self.path, "r")
            try:
                return archive.open(self.entry_path, "r")
            except KeyError as err:
                archive.close()
                raise FileNotFoundError(
                    f"Entry '{self.entry_path}' not found in archive '{self.path}'."
                ) from err
        else:
            if not Path(self.path).is_file():
                raise FileNotFoundError(f"File '{self.path}' does not exist.")
            return Path(self.path).open("rb")


class ProjectFile(File):
    """A project file"""

    def __init__(self, path: str, mime: str | None = None, entry_path: str | None = None) -> None:
        super().__init__(path, "Project", mime, entry_path)

    def read_stream(self, project_id: str) -> IO[bytes]:
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.
        """
        response = get_resource_response(project_id, self.path)
        if response.status_code != 200:  # noqa: PLR2004
            raise FileNotFoundError(f"Project file '{self.path}' not found.")
        response_bytes = BytesIO(response.raw.read())
        if self.entry_path:
            archive = zipfile.ZipFile(response_bytes, "r")
            try:
                return archive.open(self.entry_path, "r")
            except KeyError as err:
                archive.close()
                raise FileNotFoundError(
                    f"Entry '{self.entry_path}' not found in project file '{self.path}'."
                ) from err
        else:
            return response_bytes


class FileEntitySchema(TypedEntitySchema[File]):
    """Entity schema that holds a collection of files."""

    def __init__(self):
        # The parent class TypedEntitySchema implements a singleton pattern
        if not hasattr(self, "_initialized"):
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
            values=[
                [value.path],
                [value.file_type],
                [value.mime] if value.mime else [],
                [value.entry_path] if value.entry_path else [],
            ],
        )

    def from_entity(self, entity: Entity) -> File:
        """Create a file entity from a generic entity."""
        path = entity.values[0][0]
        file_type = entity.values[1][0]
        mime = entity.values[2][0] if entity.values[2] and entity.values[2][0] else None
        entry_path = entity.values[3][0] if entity.values[3] and entity.values[3][0] else None

        match file_type:
            case "Local":
                return LocalFile(path, mime, entry_path)
            case "Project":
                return ProjectFile(path, mime, entry_path)
            case _:
                raise ValueError(f"File '{path}' has unexpected type '{file_type}'.")
