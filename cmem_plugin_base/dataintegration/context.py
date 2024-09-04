"""Contains classes to pass context information into plugins.

The classes in this file are only for documentation purposes. The actual classes will
be injected by DataIntegration and will follow the signatures of the classes below.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, Literal

from dataintegration.entity import Entities


class SystemContext:
    """Passed into methods to request general system information."""

    def di_version(self) -> str:
        """The version of the running DataIntegration instance."""

    def encrypt(self, value: str) -> str:
        """Encrypts a value using the secret key, which is configured
        in 'plugin.parameters.password.crypt.key'"""

    def decrypt(self, value: str) -> str:
        """Decrypts a value using the secret key, which is configured
        in 'plugin.parameters.password.crypt.key'"""


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

    def project_id(self) -> str:
        """The identifier of the project."""

    def task_id(self) -> str:
        """The identifier of the task."""


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

    summary: list[Tuple[str, str]] = field(default_factory=list)
    """Generates a short summary of this report.
       A sequence of key-value pairs representing the summary table."""

    warnings: list[str] = field(default_factory=list)
    """If issues occurred during execution, this contains a list of user-friendly
    messages."""

    error: Optional[str] = None
    """Error message in case a fatal error occurred. If an error is set, the workflow
    execution will be stopped after the operator has been executed."""

    sample_entities: Optional[Entities] = None
    """Sample of entities that were output by this task."""


class ReportContext:
    """Passed into workflow plugins that may generate a report during execution."""

    def update(self, report: ExecutionReport) -> None:
        """Updates the current execution report.
        May be called repeatedly during operator execution."""


class PluginContext:
    """Combines context objects that are available during plugin creation or update."""

    system: SystemContext
    """General system information."""

    user: Optional[UserContext]
    """The user that creates or updates the plugin. If the plugin is loaded from an
    existing project, this might be the configured super user. If DataIntegration is
    run outside of a Corporate Memory environment, no user is available.
    Note that after creation, the plugin may be updated or executed by another user."""

    project_id: str
    """The project that contains / will contain this plugin."""


class WorkflowContext:
    """Context information if a plugin is executed within a workflow."""

    def workflow_id(self) -> str:
        """Retrieve the identifier of the current workflow"""

    def status(self) -> Literal['Idle', 'Waiting', 'Running', 'Canceling', 'Finished']:
        """Retrieve the execution status of this plugin within the current workflow.
        One of the following:
            - Idle: Plugin has not been started yet.
            - Waiting: Plugin has been started and is waiting to be executed.
            - Running: Plugin is currently being executed.
            - Canceling: Plugin has been requested to stop.
            - Finished: Plugin has finished execution."""


class ExecutionContext:
    """Combines context objects that are available during plugin execution."""

    system: SystemContext
    """General system information."""

    user: Optional[UserContext]
    """The user that issued the plugin execution. If a scheduler initiated the
    execution, this might be the configured super user. If DataIntegration is
    run outside of a Corporate Memory environment, no user is available."""

    task: TaskContext
    """Task metadata about the executed plugin."""

    workflow: Optional[WorkflowContext]
    """Workflow metadata about the executed plugin.
       None, if this plugin is not executed within a workflow."""

    report: ReportContext
    """Allows to update the execution report."""
