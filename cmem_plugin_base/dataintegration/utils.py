"""Utils for dataintegration plugins."""
import os
import re
from typing import Optional, Union, List

from cmem.cmempy.workspace.projects.datasets.dataset import post_resource

from ulid import ULID

from cmem_plugin_base.dataintegration.context import UserContext
from cmem_plugin_base.dataintegration.entity import (
    Entities, Entity, EntityPath
)
from cmem_plugin_base.dataintegration.entity import EntitySchema


def generate_id(name: str) -> str:
    """Generates a valid DataIntegration identifier from a string.
    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def setup_cmempy_user_access(context: Optional[UserContext]):
    """Setup environment for accessing CMEM with cmempy."""
    if context is None:
        raise ValueError("No UserContext given.")
    if context.token() is None:
        raise ValueError("UserContext has no token.")
    os.environ["OAUTH_GRANT_TYPE"] = "prefetched_token"
    os.environ["OAUTH_ACCESS_TOKEN"] = context.token()
    if "CMEM_BASE_URI" not in os.environ:
        os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]


def setup_cmempy_super_user_access():
    """Setup environment for accessing CMEM with cmempy.

    The helper function is used to setup the environment for accessing CMEM with cmempy.
    It does nothing if there is already a working environment.
    If not, it will try to use the configured DI environment.
    """
    try:
        os.environ["OAUTH_GRANT_TYPE"] = "client_credentials"
        if "CMEM_BASE_URI" not in os.environ:
            os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]
        if "OAUTH_CLIENT_ID" not in os.environ:
            os.environ["OAUTH_CLIENT_ID"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT"
            ]
        if "OAUTH_CLIENT_SECRET" not in os.environ:
            os.environ["OAUTH_CLIENT_SECRET"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET"
            ]
    except KeyError as error:
        raise ValueError("Super user configuration not available.") from error


def split_task_id(task_id: str) -> tuple:
    """Split a combined task ID.

    Args:
        task_id (str): The combined task ID.

    Returns:
        The project and task ID

    Raises:
        ValueError: in case the task ID is not splittable
    """
    try:
        project_part = task_id.split(":")[0]
        task_part = task_id.split(":")[1]
    except IndexError as error:
        raise ValueError(f"{task_id} is not a valid task ID.") from error
    return project_part, task_part


def write_to_dataset(
        dataset_id: str, file_resource=None, context: Optional[UserContext] = None
):
    """Write to a dataset.

    Args:
        dataset_id (str): The combined task ID.
        file_resource (file stream): Already opened byte file stream
        context (UserContext):
            The user context to setup environment for accessing CMEM with cmempy.

    Returns:
        requests.Response object

    Raises:
        ValueError: in case the task ID is not splittable
        ValueError: missing parameter
    """
    setup_cmempy_user_access(context=context)
    project_id, task_id = split_task_id(dataset_id)

    return post_resource(
        project_id=project_id,
        dataset_id=task_id,
        file_resource=file_resource,
    )


def _get_paths(values: dict) -> List[str]:
    """Get paths from a dictionary of values."""
    return list(values.keys())


def merge_path_values(paths_map1, paths_map2):
    """
    Merge two dictionaries representing paths and values.

    This function takes two dictionaries, `paths_map1` and `paths_map2`,
    each representing paths and corresponding values. It merges these dictionaries
    by combining values for common paths and returns the merged dictionary.

    Args:
        paths_map1 (dict): The first dictionary containing paths and values.
        paths_map2 (dict): The second dictionary containing paths and values.

    Returns:
        dict: A merged dictionary containing combined values for common paths.
    """
    for key, value in paths_map2.items():
        current_path_map = {}
        if paths_map1.get(key) is not None:
            current_path_map = paths_map1[key]
        current_path_map = current_path_map | value
        paths_map1[key] = current_path_map
    return paths_map1


def generate_paths_from_data(data, path='root'):
    """
    Generate a dictionary representing paths and data types from a nested JSON
    structure.

    This function recursively traverses a nested JSON structure ('data') and builds
    a dictionary ('paths_map') where keys are paths and values are dictionaries
    containing keys and their corresponding data types.

    Args:
        data (dict or list): The nested JSON structure to traverse.
        path (str, optional): The current path (used for recursion). Default is 'root'.

    Returns:
        dict: A dictionary representing paths and data types.
    """
    paths_map = {}
    if isinstance(data, list):
        for _ in data:
            paths_map = merge_path_values(paths_map,
                                          generate_paths_from_data(_, path=path))
    if isinstance(data, dict):
        key_to_type_map = {}
        for key, value in data.items():
            key_to_type_map[key] = type(value).__name__
            if key_to_type_map[key] == 'dict':
                sub_path = f"{path}/{key}"
                paths_map = merge_path_values(paths_map,
                                              generate_paths_from_data(data=value,
                                                                       path=sub_path))
        paths_map[path] = key_to_type_map
    return paths_map


def _get_schema(data: Union[dict, list]):
    """Get the schema of an entity."""
    if not data:
        return None
    paths_map = generate_paths_from_data(data=data)
    path_to_schema_map = {}
    for path, key_to_type_map in paths_map.items():
        schema_paths = []
        for _key, _type in key_to_type_map.items():
            schema_paths.append(
                EntityPath(
                    path=_key,
                    is_uri=_type == 'dict'
                )
            )
        schema = EntitySchema(
            type_uri="",
            paths=schema_paths,
        )
        path_to_schema_map[path] = schema
    return path_to_schema_map


def extend_path_list(path_to_entities, sub_path_to_entities):
    """
    Extend a dictionary of paths to entities by merging with another.

    This function takes two dictionaries, `path_to_entities` and `sub_path_to_entities`,
    representing paths and lists of entities. It extends the lists of entities for each
    path in `path_to_entities` by combining them with corresponding lists in
    `sub_path_to_entities`.

    Args:
        path_to_entities (dict): The main dictionary of paths to entities.
        sub_path_to_entities (dict): The dictionary of additional paths to entities.

    Returns:
        None: The result is modified in-place. `path_to_entities` is extended with
        entities from `sub_path_to_entities`.
    """
    for key, sub_entities in sub_path_to_entities.items():
        entities = path_to_entities.get(key, [])
        entities.extend(sub_entities)
        path_to_entities[key] = entities


def _get_entity(
        path_from_root,
        path_to_schema_map,
        data,
):
    """Get an entity based on the schema and data."""
    path_to_entities = {}
    entity_uri = f"urn:x-ulid:{ULID()}"
    values = []
    schema = path_to_schema_map[path_from_root]
    for _ in schema.paths:
        if data.get(_.path) is None:
            values.append([''])
        elif not _.is_uri:
            values.append([f"{data.get(_.path)}"])
        else:
            sub_entity_path = f"{path_from_root}/{_.path}"
            sub_path_to_entities = _get_entity(
                path_from_root=sub_entity_path,
                path_to_schema_map=path_to_schema_map,
                data=data.get(_.path),
            )
            sub_entity = sub_path_to_entities[sub_entity_path].pop()
            sub_path_to_entities[sub_entity_path].append(sub_entity)
            values.append([sub_entity.uri])
            extend_path_list(path_to_entities, sub_path_to_entities)

    entity = Entity(uri=entity_uri, values=values)
    entities = path_to_entities.get(path_from_root, [])
    entities.append(entity)
    path_to_entities[path_from_root] = entities
    return path_to_entities


def _get_entities(
        data: Union[dict, list],
        path_to_schema_map: dict[str, EntitySchema],
) -> dict[str, list[Entity]]:
    """
    Get entities based on the schema, data, and sub-entities.
    """
    path_to_entities: dict[str, list[Entity]] = {}
    if isinstance(data, list):
        for _ in data:
            sub_path_to_entities = _get_entity(
                path_from_root="root",
                path_to_schema_map=path_to_schema_map,
                data=_
            )
            extend_path_list(path_to_entities, sub_path_to_entities)
    else:
        path_to_entities = _get_entity(
            path_from_root="root",
            path_to_schema_map=path_to_schema_map,
            data=data,
        )
    return path_to_entities


def build_entities_from_data(data: Union[dict, list]) -> Optional[Entities]:
    """
    Get entities from a data object.
    """
    path_to_schema_map = _get_schema(data)
    if not path_to_schema_map:
        return None
    path_to_entities = _get_entities(
        data=data,
        path_to_schema_map=path_to_schema_map,
    )
    return Entities(
        entities=path_to_entities.get('root'),  # type: ignore
        schema=path_to_schema_map['root'],
        sub_entities=[
            Entities(
                entities=iter(value),
                schema=path_to_schema_map[key]
            ) for key, value in path_to_entities.items() if key != 'root'
        ]
    )
