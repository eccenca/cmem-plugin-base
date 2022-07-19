"""Utils for dataintegration plugins."""
import os
import re
from typing import Optional

from cmem.cmempy.workspace.projects.resources.resource import create_resource
from cmem.cmempy.workspace.tasks import get_task

from cmem_plugin_base.dataintegration.context import UserContext


def generate_id(name: str) -> str:
    """Generates a valid DataIntegration identifier from a string.
    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def setup_cmempy_user_access(context: Optional[UserContext]):
    """Setup environment for accessing CMEM with cmempy.
    """
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


def write_to_dataset(dataset_id: str, file_resource=None,
                     context: Optional[UserContext] = None):
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

    task_meta_data = get_task(project=project_id, task=task_id)
    resource_name = str(task_meta_data["data"]["parameters"]["file"]["value"])

    return create_resource(
        project_name=project_id,
        resource_name=resource_name,
        file_resource=file_resource,
        replace=True,
    )
