"""Utils for dataintegration plugins."""
import os
import re


def generate_id(name: str) -> str:
    """Generates a valid DataIntegration identifier from a string.
    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def setup_cmempy_super_user_access():
    """Setup environment for accessing CMEM with cmempy.

    The helper function is used to setup the environment for accessing CMEM with cmempy.
    It does nothing if there is already a working environment.
    If not, it will try to use the configured DI environment.
    """
    try:
        len(os.environ["CMEM_BASE_URI"])
        os.environ["OAUTH_GRANT_TYPE"] = "client_credentials"
        if "OAUTH_CLIENT_ID" not in os.environ:
            os.environ["OAUTH_CLIENT_ID"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT"
            ]
        if "OAUTH_CLIENT_ID" not in os.environ:
            os.environ["OAUTH_CLIENT_SECRET"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET"
            ]
    except KeyError as error:
        raise ValueError("Super user configuration not available.") from error
