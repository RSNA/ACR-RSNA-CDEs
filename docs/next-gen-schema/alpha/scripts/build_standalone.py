# -*- coding: utf-8 -*-
"""Optional full standalone packaging.

The authoritative modular form is radcde-alpha.ttl plus its direct RadLex import.
This helper creates a single Turtle file containing both the generated CDE graph
and the configured native RadLex graph. RadLex triples are serialized unchanged
as N-Triples, which is valid Turtle syntax, then appended atomically to the CDE
Turtle. No RadLex assertions are rewritten or authored by the CDE layer.
"""
from pathlib import Path
import os
import tempfile
from rdflib import Graph

from radlex_config import RADLEX_OWL

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "standalone"


def main():
    OUT.mkdir(exist_ok=True)
    destination = OUT / "radcde-standalone.ttl"

    radlex = Graph().parse(RADLEX_OWL, format="xml")

    # Serialize RadLex completely before touching the destination. Writing the
    # final file through a temporary sibling and os.replace() prevents an
    # interrupted build from leaving a truncated standalone artifact.
    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".nt", dir=OUT, delete=False
    ) as radlex_tmp:
        radlex_tmp_path = Path(radlex_tmp.name)
    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".ttl", dir=OUT, delete=False
    ) as out_tmp:
        out_tmp_path = Path(out_tmp.name)

    try:
        radlex.serialize(destination=radlex_tmp_path, format="nt")
        with out_tmp_path.open("wb") as dst:
            dst.write((ROOT / "radcde-alpha.ttl").read_bytes())
            dst.write(b"\n# ---- Imported RadLex graph, serialized as N-Triples ----\n")
            with radlex_tmp_path.open("rb") as src:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    dst.write(chunk)
        os.replace(out_tmp_path, destination)
        destination.chmod(0o644)
    finally:
        radlex_tmp_path.unlink(missing_ok=True)
        out_tmp_path.unlink(missing_ok=True)

    print("standalone CDE triples:", len(Graph().parse(ROOT / "radcde-alpha.ttl", format="turtle")))
    print("standalone RadLex triples:", len(radlex))
    print("standalone file:", destination)


if __name__ == "__main__":
    main()
