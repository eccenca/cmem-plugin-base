"""Utils for dataintegration plugins."""

import re
from typing import IO

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.context import ExecutionContext, PluginContext


def generate_id(name: str) -> str:
    """Generate a valid DataIntegration identifier from a string.

    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


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
        project_part = task_id.split(":", maxsplit=1)[0]
        task_part = task_id.split(":")[1]
    except IndexError as error:
        raise ValueError(f"{task_id} is not a valid task ID.") from error
    return project_part, task_part


def write_to_dataset(
    dataset_id: str,
    file_resource: IO | None = None,
    context: ExecutionContext | PluginContext | None = None,
) -> None:
    """Write to a dataset.

    Args:
        dataset_id (str): The combined task ID.
        file_resource (file stream): Already opened byte file stream
        context (ExecutionContext | PluginContext):
            The context to create a cmem-client Client from.

    Raises:
        ValueError: in case the task ID is not splittable
        ValueError: missing parameter

    """
    if context is None:
        raise ValueError("No context given.")
    if file_resource is None:
        raise ValueError("No file_resource given.")
    project_id, task_id = split_task_id(dataset_id)

    get_client(context).datasets.post_file_resource(
        project_id=project_id,
        dataset_id=task_id,
        file_resource=file_resource,
    )
