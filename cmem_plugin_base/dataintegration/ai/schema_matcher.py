"""All classes related to schema matcher plugins.
   WARNING: All classes in this file are preliminary and might be changed."""

from cmem_plugin_base.dataintegration.plugins import PluginBase


class MatchingSchema:
    """The schema that is used by schema matchers."""

    def write_rdf_file(self, path: str, lang: str) -> None:
        """Write this schema to an RDF file.

        :param path: The target file path.
        :param lang: The RDF format. Usually, either "N-TRIPLE" or "TURTLE".
        """
        # Implementation provided by DataIntegration


class Correspondence:
    """Candidate match between two properties from two schemata."""

    def __init__(self, source: str, target: str, confidence: float):
        self.source = source
        self.target = target
        self.confidence = confidence

    def __str__(self):
        """Convert to a string representation"""
        return f"{self.source} - {self.target} ({self.confidence})"


class Alignment:
    """Set of correspondences between two schemata."""

    def __init__(self, matches: list[Correspondence]):
        self.matches = matches


class SchemaMatcherPlugin(PluginBase):
    """
    A schema matcher aligns a source dataset with target vocabularies.
    """

    def match(self, source: MatchingSchema, target: MatchingSchema) -> Alignment:
        """
        Aligns a source dataset with target vocabularies.

        :param source: Source schema
        :param target: Target schema

        :return: The generated alignment.
        """
