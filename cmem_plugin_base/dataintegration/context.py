"""Contains classes to pass context information into plugins."""

from dataclasses import dataclass
from typing import Optional


class UserContext:
    """Passed into methods that are triggered by a user interaction."""

    def user_uri(self) -> str:
        """The URI of the user."""

    def user_label(self) -> str:
        """The name of the user."""

    def token(self) -> str:
        """Retrieves the OAuth token for the user."""


class TaskContext:
    """Passed into objects that are part of a DataIntegration task/project."""

    def di_version(self) -> str:
        """The version of the running DataIntegration instance."""

    def project_id(self) -> str:
        """The identifier of the project."""

    def task_id(self) -> str:
        """The identifier of the task."""

    def prefixes(self) -> dict[str, str]:
        """The prefixes, which are defined on the project level."""


@dataclass()
class ExecutionReport:
    """Workflow operators may generate execution reports. An execution report holds
    basic information and various statistics about the operator execution."""

    entity_count: int = 0
    """The number of entities that have been processed.
       This value may be displayed in real-time in the UI."""

    operation: Optional[str] = None
    "Short label for the executed operation, e.g., read or write (optional)."

    operation_desc: str = "entities processed"
    "Short description of the operation (plural, past tense)."

    summary: list[(str, str)] = ()
    """Generates a short summary of this report.
       A sequence of key-value pairs representing the summary table """

    warnings: list[str] = ()
    """If issues occurred during execution, this contains a list of user-friendly
    messages. """

    error: Optional[str] = None
    """Error message in case a fatal error occurred."""


class ReportContext:
    """Passed into workflow plugins that may generate a report during execution."""

    def update(self, report: ExecutionReport) -> None:
        """Updates the current execution report.
        May be called repeatedly during operator execution."""


class ExecutionContext:
    """Combines context objects that are available during execution."""

    user: Optional[UserContext]

    task: TaskContext

    report: ReportContext
