"""All Plugins base classes."""
import logging
from typing import Sequence, Optional

from cmem_plugin_base.dataintegration.context import ExecutionContext

from .entity import Entities


class PluginLogger:
    """Logging API for Plugins.
    If a plugin is running within DataIntegration, this class
    will be replaced to log into DI using the path: plugins.python.<plugin_id>."""

    def debug(self, message: str) -> None:
        """Log a message with severity 'DEBUG'."""
        logging.debug(message)

    def info(self, message: str) -> None:
        """Log a message with severity 'INFO'."""
        logging.info(message)

    def warning(self, message: str) -> None:
        """Log a message with severity 'WARNING'."""
        logging.warning(message)

    def error(self, message: str) -> None:
        """Log a message with severity 'ERROR'."""
        logging.error(message)


class PluginConfig:
    """Configuration API for Plugins.
    If a plugin is running within DataIntegration,
    this class will be replaced to retrieve the DI configuration
    in the path: plugins.python.<plugin_id>."""

    def get(self) -> str:
        """Retrieve plugin configuration as a JSON string.
        This test implementation will return an empty string."""
        return ""


class PluginBase:
    """Base class of all plugins."""

    log: PluginLogger = PluginLogger()

    config: PluginConfig = PluginConfig()


class WorkflowPlugin(PluginBase):
    """Base class of all workflow operator plugins."""

    def execute(self, inputs: Sequence[Entities],
                context: ExecutionContext) -> Optional[Entities]:
        """Executes the workflow plugin on a given collection of entities.

        :param inputs: Contains a separate collection of entities for each
            input. Currently, DI sends ALWAYS an input. in case no connected
            input is there, the sequence has a length of 0.

        :return: The entities generated from the inputs. At the moment, only one
            entities objects be returned (means only one outgoing connection)
            or none (no outgoing connection).
        """


class TransformPlugin(PluginBase):
    """
    Base class of all transform operator plugins.
    """

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """
        Transforms a collection of values.
        :param inputs: A sequence which contains as many elements as there are input
            operators for this transformation.
            For each input operator it contains a sequence of values.
        :return: The transformed values.
        """
