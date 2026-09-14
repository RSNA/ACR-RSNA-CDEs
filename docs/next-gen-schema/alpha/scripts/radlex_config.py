# -*- coding: utf-8 -*-
"""Central RadLex source configuration for the alpha build."""
from pathlib import Path
import os, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _version_key(path):
    m = re.search(r"(?:Owl|RadLex)(\d+(?:\.\d+)+)", str(path))
    if not m:
        return ()
    return tuple(int(x) for x in m.group(1).split("."))


def _discover_default():
    refs = ROOT / "references"
    candidates = list(refs.glob("PunRadLex_Owl*/RadLex.owl"))
    if not candidates:
        candidates = list(refs.glob("**/RadLex.owl"))
    if not candidates:
        raise FileNotFoundError("No bundled RadLex.owl found under references/")
    return max(candidates, key=lambda p: (_version_key(p), str(p)))


def radlex_owl_path():
    override = os.environ.get("RADCDE_RADLEX_OWL") or os.environ.get("RADLEX_OWL")
    return Path(override).expanduser().resolve() if override else _discover_default().resolve()


def radlex_version(path=None):
    p = Path(path or radlex_owl_path())
    m = re.search(r"(?:Owl|RadLex)(\d+(?:\.\d+)+)", str(p))
    return m.group(1) if m else "configured"

RADLEX_OWL = radlex_owl_path()
RADLEX_VERSION = radlex_version(RADLEX_OWL)
RADLEX_NS = "http://www.radlex.org/RID/"
RADLEX_ONTOLOGY_IRI = "http://radlex.org/RID/RadLex.owl"
