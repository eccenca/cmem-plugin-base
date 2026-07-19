"""Utils for dataintegration plugins."""

import os
import re
from typing import IO

from cmem_client.auth_provider.client_credentials import ClientCredentialsFlow
from cmem_client.auth_provider.prefetched_token import PrefetchedToken
from cmem_client.client import Client
from cmem_client.config import Config

from cmem_plugin_base.dataintegration.context import UserContext


def generate_id(name: str) -> str:
    """Generate a valid DataIntegration identifier from a string.

    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def setup_cmem_client(context: UserContext | None) -> Client:
    """Build a cmem-client Client for the given user context.

    Also sets OAUTH_GRANT_TYPE/OAUTH_ACCESS_TOKEN/CMEM_BASE_URI in the process
    environment, mirroring what cmempy used to do, so that code building a
    Client via Client.from_env() (e.g. File.read_stream's ambient fallback)
    picks up the same identity without being passed a context.
    """
    if context is None:
        raise ValueError("No UserContext given.")
    token = context.token()
    if token is None:
        raise ValueError("UserContext has no token.")
    os.environ["OAUTH_GRANT_TYPE"] = "prefetched_token"
    os.environ["OAUTH_ACCESS_TOKEN"] = token
    if "CMEM_BASE_URI" not in os.environ:
        os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]
    config = Config(url_base=os.environ["CMEM_BASE_URI"])
    return Client(config=config, auth=PrefetchedToken(prefetched_token=token))


def setup_cmempy_user_access(context: UserContext | None) -> None:
    """Set up environment for accessing CMEM.

    Deprecated: use setup_cmem_client(context) instead, which returns a
    ready-to-use cmem_client.Client instead of only mutating the environment.
    """
    setup_cmem_client(context)


def setup_cmem_client_super_user_access() -> Client:
    """Build a cmem-client Client using client-credentials (super user) authentication.

    Uses an already-working environment if present. If not, falls back to the
    configured DI service account (DATAINTEGRATION_CMEM_SERVICE_CLIENT[_SECRET]).
    """
    try:
        os.environ["OAUTH_GRANT_TYPE"] = "client_credentials"
        if "CMEM_BASE_URI" not in os.environ:
            os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]
        if "OAUTH_CLIENT_ID" not in os.environ:
            os.environ["OAUTH_CLIENT_ID"] = os.environ["DATAINTEGRATION_CMEM_SERVICE_CLIENT"]
        if "OAUTH_CLIENT_SECRET" not in os.environ:
            os.environ["OAUTH_CLIENT_SECRET"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET"
            ]
    except KeyError as error:
        raise ValueError("Super user configuration not available.") from error
    config = Config(url_base=os.environ["CMEM_BASE_URI"])
    auth = ClientCredentialsFlow(
        config=config,
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    )
    return Client(config=config, auth=auth)


def setup_cmempy_super_user_access() -> None:
    """Set up environment for accessing CMEM as a super user.

    Deprecated: use setup_cmem_client_super_user_access() instead, which
    returns a ready-to-use cmem_client.Client instead of only mutating the
    environment.
    """
    setup_cmem_client_super_user_access()


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


def write_to_dataset(  # noqa: ANN201
    dataset_id: str, file_resource: IO | None = None, context: UserContext | None = None
):
    """Write to a dataset.

    Args:
        dataset_id (str): The combined task ID.
        file_resource (file stream): Already opened byte file stream
        context (UserContext):
            The user context to setup environment for accessing CMEM.

    Returns:
        None

    Raises:
        ValueError: in case the task ID is not splittable
        ValueError: missing parameter
        httpx.HTTPStatusError: if the upload request fails

    """
    client = setup_cmem_client(context)
    project_id, task_id = split_task_id(dataset_id)

    client.datasets.post_file_resource(
        project_id=project_id,
        dataset_id=task_id,
        file_resource=file_resource,
    )
