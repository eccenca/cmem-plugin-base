"""Package and plugin discovery module."""
import json
from subprocess import check_output
from typing import Dict, List


def get_packages() -> List[Dict]:
    """Get installed python packages.

    Returns a list of dict with the following keys:
     - name - package name
     - version - package version
    """
    return json.loads(
        check_output(
            ["pip", "list", "--format", "json"],
            shell=False
        )
    )
