"""Shared view on one LinkML source file as IFDD uses it."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from linkml_runtime.linkml_model.meta import ClassDefinition, SlotDefinition
from linkml_runtime.utils.schemaview import SchemaView


@dataclass
class IfddSchema:
    """One namespace: a LinkML schema plus the IFDD reading of it.

    The *main class* is the class whose ``class_uri`` lies in the schema's own
    namespace. Only schemas with a main class get a JSON-LD context. All other
    classes are reference targets in other namespaces (stubs); they only carry
    a URI.
    """

    path: Path
    view: SchemaView

    @classmethod
    def load(cls, path: str | Path) -> IfddSchema:
        path = Path(path)
        return cls(path=path, view=SchemaView(str(path)))

    @property
    def name(self) -> str:
        return self.view.schema.name

    @property
    def alias(self) -> str:
        """Prefix of the own namespace, e.g. ``breaker``."""
        return self.view.schema.default_prefix

    @property
    def namespace(self) -> str:
        return self.view.namespaces()[self.alias]

    def expand(self, curie_or_uri: str) -> str:
        return self.view.expand_curie(curie_or_uri)

    @property
    def main_class(self) -> ClassDefinition | None:
        found = [c for c in self.view.all_classes(imports=False).values()
                 if c.class_uri and self.expand(c.class_uri).startswith(self.namespace)]
        if len(found) > 1:
            raise ValueError(f"{self.path}: more than one class in the own namespace: {[c.name for c in found]}")
        return found[0] if found else None

    def terms(self) -> list[SlotDefinition]:
        """Terms of the namespace, ordered by rank.

        With a main class these are its attributes, otherwise the schema's
        top-level slots (vocabulary without context, e.g. for time series).
        """
        main = self.main_class
        if main is not None:
            slots = [self.view.induced_slot(n, main.name) for n in self.view.class_slots(main.name)]
        else:
            slots = [self.view.induced_slot(n) for n in self.view.all_slots(imports=False)]
        missing = [s.name for s in slots if s.rank is None]
        if missing:
            raise ValueError(f"{self.path}: terms without rank: {missing}")
        return sorted(slots, key=lambda s: (s.rank, s.name))

    def annotation(self, element, key: str) -> str | None:
        anns = element.annotations
        if not anns:
            return None
        # Plain schema elements hold a dict; induced slots hold a JsonObj.
        ann = anns.get(key) if isinstance(anns, dict) else getattr(anns, key, None)
        if ann is None:
            return None
        return str(ann.value if hasattr(ann, "value") else ann["value"])


def main(argv: list[str]) -> int:
    """``python -m ifdd_model.schema has-context SCHEMA.yaml``: exit 0 if the
    schema has a class in its own namespace (and so gets a JSON-LD context)."""
    if len(argv) != 2 or argv[0] != "has-context":
        print("usage: python -m ifdd_model.schema has-context SCHEMA.yaml", file=sys.stderr)
        return 2
    return 0 if IfddSchema.load(argv[1]).main_class is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
