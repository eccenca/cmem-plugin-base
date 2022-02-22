"""All Plugins base classes."""
from typing import Sequence, Optional

from .entity import Entities


class WorkflowPlugin:
    """Base class of all workflow operator plugins."""

    def execute(self, inputs: Sequence[Entities]) -> Optional[Entities]:
        """Executes the workflow plugin on a given collection of entities.

        :param inputs: Contains a separate collection of entities for each
            input. Currently, DI sends ALWAYS an input. in case no connected
            input is there, the sequence has a length of 0.

        :return: The entities generated from the inputs. At the moment, only one
            entities objects be returned (means only one outgoing connection)
            or none (no outgoing connection).
        """
