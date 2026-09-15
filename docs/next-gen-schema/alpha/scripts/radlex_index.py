# -*- coding: utf-8 -*-
"""Utilities over the native RadLex index produced by build_anatomy.py."""
from __future__ import annotations
import json
from collections import defaultdict, deque
from pathlib import Path

RDFS_SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"


def load_index(path=None):
    p = Path(path or Path(__file__).with_name("anatomy.json"))
    return json.loads(p.read_text(encoding="utf-8"))


def property_descendants(index, root_iri):
    children = defaultdict(set)
    for iri, p in index["object_properties"].items():
        for parent in p.get("subPropertyOf", []):
            children[parent].add(iri)
    out, q = {root_iri}, deque([root_iri])
    while q:
        x=q.popleft()
        for c in children.get(x, ()):
            if c not in out:
                out.add(c); q.append(c)
    return out


def inverse_map(index):
    inv = defaultdict(set)
    for iri, p in index["object_properties"].items():
        for other in p.get("inverseOf", []):
            inv[iri].add(other); inv[other].add(iri)
    return inv


def taxonomy_children(index):
    d=defaultdict(set)
    for e in index["taxonomy"]:
        d[e["to"]].add(e["from"])
    return d


def taxonomy_parents(index):
    d=defaultdict(set)
    for e in index["taxonomy"]:
        d[e["from"]].add(e["to"])
    return d


def descendants(index, root, include_root=False):
    ch=taxonomy_children(index); out={root} if include_root else set(); q=deque([root])
    while q:
        x=q.popleft()
        for c in ch.get(x, ()):
            if c not in out:
                out.add(c); q.append(c)
    if not include_root: out.discard(root)
    return out


def ancestors(index, start, include_start=False):
    par=taxonomy_parents(index); out={start} if include_start else set(); q=deque([start])
    while q:
        x=q.popleft()
        for p in par.get(x, ()):
            if p not in out:
                out.add(p); q.append(p)
    if not include_start: out.discard(start)
    return out


def anatomy_branch(index):
    return descendants(index, "RID3", include_root=True)


def relationships_for(index, concept):
    """Return native RadLex relationships asserted for a concept, unchanged."""
    return [r for r in index.get("relationships", []) if r.get("from") == concept]


def property_definition(index, predicate):
    """Return metadata for one exact native RadLex object property."""
    return index.get("object_properties", {}).get(predicate)


def subproperties_of(index, predicate, recursive=True, include_self=False):
    """Return declared native subproperties without treating them as substitutes.

    This exposes RadLex hierarchy metadata only. Consumers decide whether hierarchy
    expansion is appropriate for their own operation.
    """
    if not recursive:
        out = {iri for iri, p in index.get("object_properties", {}).items()
               if predicate in p.get("subPropertyOf", [])}
    else:
        out = property_descendants(index, predicate)
        out.discard(predicate)
    if include_self:
        out.add(predicate)
    return out


def inverse_of(index, predicate):
    """Return exact owl:inverseOf declarations for a native predicate."""
    return set(inverse_map(index).get(predicate, ()))


def follow_exact_property(index, concept, predicate, direction="forward"):
    """Follow exactly one native predicate for one hop.

    No subproperty expansion, inverse substitution, recursion, or transitivity is
    implied. For direction='reverse', source assertions are read backwards while
    retaining the exact asserted predicate.
    """
    if direction not in {"forward", "reverse"}:
        raise ValueError("direction must be 'forward' or 'reverse'")
    out=[]
    for r in index.get("relationships", []):
        if r.get("predicate") != predicate:
            continue
        if direction == "forward" and r.get("from") == concept:
            out.append(r)
        elif direction == "reverse" and r.get("to") == concept:
            out.append(r)
    return out

