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


class TransformPlugin:
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
